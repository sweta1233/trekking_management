"""Celery app instance + background jobs, all in one file."""
import os
import csv
import smtplib
import logging
from datetime import date, timedelta, datetime
from email.mime.text import MIMEText

import requests
from celery import Celery
from celery.schedules import crontab

from config import Config

logger = logging.getLogger("tma.tasks")
logging.basicConfig(level=logging.INFO)

celery_app = Celery("tma", broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)
celery_app.conf.update(timezone="UTC", enable_utc=True)
celery_app.conf.beat_schedule = {
    "daily-trek-reminder": {"task": "tasks.send_daily_reminders", "schedule": crontab(hour=7, minute=0)},
    "monthly-admin-report": {"task": "tasks.generate_monthly_report", "schedule": crontab(hour=6, minute=0, day_of_month=1)},
}


class _AppContextTask(celery_app.Task):
    """Wraps every task so it runs inside a Flask app context (needed for DB access)."""
    def __call__(self, *args, **kwargs):
        from app import app
        with app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = _AppContextTask


def _send_email(to_email, subject, body_html):
    if not Config.MAIL_ENABLED:
        logger.info(f"[EMAIL - not sent, MAIL_ENABLED=false] To: {to_email} | Subject: {subject}")
        return
    try:
        msg = MIMEText(body_html, "html")
        sender = Config.MAIL_USERNAME or Config.MAIL_FROM
        msg["Subject"], msg["From"], msg["To"] = subject, sender, to_email
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(sender, [to_email], msg.as_string())
        logger.info(f"[EMAIL sent via {Config.MAIL_SERVER}:{Config.MAIL_PORT}] To: {to_email} | Subject: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


def _send_sms(phone, message):
    logger.info(f"[SMS - not sent, no gateway configured] To: {phone} | {message}")


def _send_google_chat(message):
    if not Config.GOOGLE_CHAT_WEBHOOK_URL:
        logger.info(f"[GOOGLE CHAT - not sent, no webhook configured] {message}")
        return
    try:
        requests.post(Config.GOOGLE_CHAT_WEBHOOK_URL, json={"text": message}, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send Google Chat webhook: {e}")


@celery_app.task(name="tasks.send_otp_email")
def send_otp_email(to_email, otp, name=None):
    """User-triggered: sends a one-time login code. Not on the beat schedule -
    fired directly from the /auth/otp/request route."""
    greeting = f"Hi {name}," if name else "Hi,"
    body = (
        f"<h3>Your TMA Login OTP</h3>"
        f"<p>{greeting}</p>"
        f"<p>Your one-time password is:</p>"
        f"<h2 style='letter-spacing:6px'>{otp}</h2>"
        f"<p>This code expires in 5 minutes. If you did not request this, you can safely ignore this email.</p>"
    )
    _send_email(to_email, "Your TMA Login OTP", body)


@celery_app.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    """Runs daily. Reminds users (email/SMS/Google Chat) about treks starting tomorrow."""
    from models import Trek

    tomorrow = date.today() + timedelta(days=1)
    treks = Trek.query.filter(Trek.start_date == tomorrow, Trek.status.in_(["Open", "Closed"])).all()

    count = 0
    for trek in treks:
        bookings = [b for b in trek.bookings if b.status == "Booked"]
        for booking in bookings:
            user = booking.user
            if not user:
                continue
            body = (
                f"<h3>Trek Reminder: {trek.trek_name}</h3><p>Start Date: {trek.start_date}</p>"
                f"<p>Location: {trek.location}</p><p>Reporting Time: 6:00 AM at base camp</p>"
            )
            _send_email(user.email, f"Reminder: {trek.trek_name} starts tomorrow!", body)
            if user.phone:
                _send_sms(user.phone, f"Reminder: Your trek '{trek.trek_name}' starts tomorrow.")
            count += 1
        if bookings:
            _send_google_chat(f"Reminder sent for '{trek.trek_name}' to {len(bookings)} participant(s).")

    logger.info(f"Daily reminders sent: {count}")
    return {"reminders_sent": count}


@celery_app.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """Runs on the 1st of every month. Emails an HTML summary to all admins."""
    from models import User, Trek, Booking

    treks, bookings = Trek.query.all(), Booking.query.all()
    counts = {}
    for b in bookings:
        counts[b.trek_id] = counts.get(b.trek_id, 0) + 1
    trek_by_id = {t.id: t for t in treks}
    popular = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    popular_html = "".join(f"<li>{trek_by_id[tid].trek_name}: {c} bookings</li>" for tid, c in popular if tid in trek_by_id)

    body = f"""
    <h2>Monthly Trekking Report - {date.today().strftime('%B %Y')}</h2>
    <ul>
      <li>Total Treks: {len(treks)}</li>
      <li>Total Bookings: {len(bookings)}</li>
      <li>Total Registered Trekkers: {User.query.filter_by(role='user').count()}</li>
    </ul>
    <h3>Popular Treks</h3><ul>{popular_html}</ul>
    """

    admins = User.query.filter_by(role="admin").all()
    for admin in admins:
        _send_email(admin.email, "TMA Monthly Report", body)

    logger.info("Monthly report generated and sent to admins.")
    return {"status": "sent", "admins_notified": len(admins)}


@celery_app.task(name="tasks.export_booking_history_csv")
def export_booking_history_csv(user_id):
    """Generates a CSV of a user's booking history asynchronously and returns the file path."""
    from models import Booking, User

    os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
    bookings = Booking.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)

    filename = f"booking_history_user{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(Config.EXPORT_FOLDER, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Trek Name", "Location", "Booking Date", "Amount", "Status", "Start Date", "End Date"])
        for b in bookings:
            writer.writerow([
                b.user_id, b.trek.trek_name if b.trek else "", b.trek.location if b.trek else "",
                b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "", b.amount, b.status,
                b.trek.start_date if b.trek else "", b.trek.end_date if b.trek else "",
            ])

    if user:
        _send_email(user.email, "Your booking history export is ready", f"<p>Your CSV export is ready: {filename}</p>")

    logger.info(f"CSV export ready: {filepath}")
    return filepath
