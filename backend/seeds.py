"""
TrekMate AI - Comprehensive Seed Data Script

Seeds the database with:
- Sample users (trekkers with varied fitness profiles)
- Trek guides with expertise
- Diverse treks across difficulty levels
- Itineraries with acclimatization plans
- Trek documents for RAG pipeline
- Sample bookings
- Reviews for sentiment analysis
- AI conversation history

Run: python seeds.py
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import (
    db, User, GuideProfile, Trek, ItineraryItem,
    TrekDocument, Booking, Review
)
from config import Config

# Sample trek document content for RAG
KEDARKANTHA_GUIDE = """# Kedarkantha Trek - Complete Guide

## Overview
Kedarkantha is one of the most popular winter treks in India, located in the Uttarkashi district of Uttarakhand. The trek offers stunning 360-degree views of Himalayan peaks including Swargarohini, Bandarpoonch, and Black Peak.

**Altitude**: 3,800m (12,500 ft)
**Duration**: 5-6 days
**Difficulty**: Easy to Moderate
**Best Season**: December to April (winter snow trek)

## Day-by-Day Itinerary

### Day 1: Dehradun to Sankri (1,950m)
- Drive duration: 8-10 hours (220 km)
- Overnight stay in Sankri village
- Acclimatization: Spend evening exploring the village

### Day 2: Sankri to Juda Ka Talab (2,800m)
- Trek distance: 4 km
- Duration: 4-5 hours
- Altitude gain: 850m
- Camp beside the pristine frozen lake
- First experience with snow-covered trails

### Day 3: Juda Ka Talab to Kedarkantha Base Camp (3,400m)
- Trek distance: 4 km
- Duration: 3-4 hours
- Altitude gain: 600m
- Gradual ascent through dense pine forests
- Set up camp with views of snow peaks

### Day 4: Base Camp to Kedarkantha Summit (3,800m) and back to Base Camp
- Trek distance: 6 km
(3 km ascent + 3 km descent)
- Duration: 7-8 hours total
- Start early (3:00 AM) for sunrise summit
- Summit offers 360° panoramic views
- Steep but well-defined trail

### Day 5: Base Camp to Sankri
- Descend back through Juda Ka Talab
- Return to Sankri for overnight stay

## Acclimatization Requirements

**Critical Guidelines:**
- Spend full day in Sankri (1,950m) before starting trek
- Drink 3-4 liters of water daily
- Ascend slowly, following "climb high, sleep low" principle
- Watch for AMS symptoms: headache, nausea, dizziness

## Essential Gear & Packing List

### Clothing Layers
- Base layer: Thermal inners (2 sets)
- Mid layer: Fleece jacket or down jacket
- Outer layer: Waterproof jacket and pants
- Trek pants (2), warm socks (4 pairs)
- Woolen cap, sun hat, balaclava
- Warm gloves (waterproof preferred)

### Footwear
- High-ankle waterproof trekking boots (broken in)
- Gaiters (essential for snow)
- Camp shoes or sandals

### Equipment
- Backpack (50-60L) with rain cover
- Trekking poles (mandatory for snow descent)
- Headlamp with extra batteries
- Sunglasses (UV protection category 3 or 4)
- Water bottles (2L capacity total)

### Personal Items
- Sunscreen SPF 40+
- Lip balm with SPF
- Personal first-aid kit
- Diamox (for AMS - consult doctor)
- Energy bars, dry fruits
- Toilet paper and wet wipes

## Safety Guidelines

### Acute Mountain Sickness (AMS) Prevention
- Never ascend more than 500m per day above 3,000m
- Acclimatize properly in Sankri
- Stay hydrated (clear urine indicator)
- Avoid alcohol and smoking
- Inform guide immediately if symptoms appear

### Winter-Specific Safety
- Temperatures drop to -10°C to -15°C at night
- Risk of frostbite on exposed skin
- Avalanche risk in heavy snowfall - follow guide's route
- Carry emergency whistle and GPS device

### Emergency Protocols
- Trek with certified guide only
- Carry emergency medicines: Diamox, Dexamethasone
- Know nearest medical facility: Sankri PHC (basic), Dehradun for serious cases
- Mobile network: Limited to Sankri only

## Permits Required
- Forest Department Permit: ₹150 per person
- Camping Permit: ₹100 per tent
- Obtain from Forest Range Office, Sankri

## Physical Fitness Requirements
- Ability to walk 5-6 hours continuously with breaks
- Cardiovascular endurance for altitude
- Prior trekking experience helpful but not mandatory
- 6-week training recommended for beginners

### Suggested Training Regimen (6 weeks before trek)
**Weeks 1-2**: Walk 30 minutes daily, build stamina
**Weeks 3-4**: Increase to 45-60 minutes, include stairs/incline
**Weeks 5-6**: Practice with loaded backpack (5-7kg), simulate trek conditions

## Best Time to Visit
- **December-January**: Heavy snow, winter wonderland
- **February-March**: Peak season, clear weather
- **April**: Snow starts melting, spring flowers

## Local Culture & Etiquette
- Sankri is a traditional Garhwali village
- Respect local customs and temples
- Practice Leave No Trace principles
- Carry back all non-biodegradable waste

## Weather Conditions
- Winter: -10°C at night, 5-10°C day
- Strong winds at summit
- Snowfall possible anytime December-March

## Food on Trek
- Vegetarian meals provided
- Typical menu: Dal, rice, sabzi, chapati
- Hot soups and tea at camps
- Carry personal snacks for energy

## What Makes Kedarkantha Special
- Perfect beginner-friendly winter trek
- Stunning campsites beside frozen lakes
- 360° summit views of major Himalayan peaks
- Rich pine and oak forests
- Traditional village experience

## Important Notes
⚠️ **Medical Clearance**: Consult doctor if you have heart conditions, respiratory issues, or are pregnant
⚠️ **Insurance**: Trekking insurance covering high-altitude rescue recommended
⚠️ **Fitness**: Do NOT attempt if you have altitude sickness history without medical advice

## Emergency Contacts
- Trek Organizer: [Provided at briefing]
- Sankri PHC: +91-XXXX-XXXXXX
- Uttarkashi District Hospital: +91-1374-222181
- Uttarakhand Emergency Services: 112

---
*This guide is for informational purposes. Always trek with certified guides and follow their instructions.*
"""

SAFETY_MANUAL = """# High Altitude Trekking - Safety Manual

## Altitude Sickness (AMS) - Critical Information

### What is AMS?
Acute Mountain Sickness occurs when you ascend to high altitude too quickly, causing your body to struggle with reduced oxygen levels.

### Symptoms by Severity

**Mild AMS** (Common above 2,500m):
- Headache
- Fatigue
- Loss of appetite
- Nausea
- Dizziness
- Disturbed sleep

**Moderate AMS**:
- Severe headache not relieved by medication
- Vomiting
- Increased weakness
- Shortness of breath at rest

**Severe AMS (HACE/HAPE - LIFE THREATENING)**:
- Confusion, altered mental state
- Loss of coordination (ataxia)
- Extreme fatigue, cannot walk
- Bubbling/gurgling in chest
- Coughing pink frothy sputum

### Prevention Guidelines
1. **Gradual Ascent**: Never gain more than 500m sleeping altitude per day above 3,000m
2. **Hydration**: Drink 3-4 liters water daily (clear urine)
3. **Acclimatization Days**: Take rest days every 1,000m gain
4. **Climb High, Sleep Low**: Day hikes to higher altitude, return to lower camp
5. **Medication**: Diamox 125mg twice daily (consult doctor)
6. **Avoid**: Alcohol, sleeping pills, smoking

### Treatment Protocol
**Mild AMS**:
- Stop ascending
- Rest for 24-48 hours
- Hydrate and take painkillers
- Monitor symptoms

**Moderate to Severe**:
- DESCEND IMMEDIATELY (most effective treatment)
- Administer oxygen if available
- Give Dexamethasone 8mg stat
- Evacuate to medical facility

## Emergency Procedures

### Medical Emergency Checklist
1. Assess patient condition and symptoms
2. Stabilize patient (keep warm, hydrated)
3. Contact emergency services
4. Prepare for evacuation if needed
5. Continue monitoring vitals

### Evacuation Protocols
- Helicopter rescue: Only in severe cases
- Requires clear weather and landing zone
- Cost: ₹1-3 lakhs (insurance essential)
- Alternative: Stretcher evacuation to roadhead

## First Aid Kit Essentials

### Medications
- Diamox (AMS prevention)
- Dexamethasone (severe AMS)
- Ibuprofen/Paracetamol (pain, fever)
- Antihistamines (allergies)
- Antibiotics (infections)
- ORS packets (rehydration)
- Antiseptic cream

### Equipment
- Digital thermometer
- Pulse oximeter
- Blood pressure monitor
- Emergency blanket
- Sterile gauze and bandages
- Adhesive tape
- Scissors and tweezers

## Weather Hazards

### Hypothermia
**Signs**: Shivering, confusion, slurred speech, drowsiness
**Action**: Warm gradually, dry clothing, warm drinks, emergency shelter

### Frostbite
**Prevention**: Keep extremities covered and dry
**Signs**: Numbness, white/grayish skin
**Action**: Warm affected area gradually, do NOT rub

### Lightning Safety
- Avoid ridge lines and peaks during storms
- Seek shelter in low areas (not under trees)
- Squat low if caught in open

## River Crossing Safety
- Cross in morning when water level is lowest
- Unbuckle backpack waist strap
- Use trekking poles for balance
- Face upstream, move sideways

## Wildlife Encounters
- Bears: Make noise, carry bear spray, never approach
- Snakes: Watch where you step, especially in summer
- Dogs: Village dogs can be aggressive, maintain distance

## Leave No Trace Principles
1. Pack out all trash (including toilet paper)
2. Use designated toilet areas
3. No washing directly in streams
4. Respect wildlife and vegetation
5. Stay on marked trails

## Communication
- Mobile network: Limited above base camps
- Satellite phone: Carried by trek leader
- Emergency whistle: 3 short blasts = distress signal

## Pre-Trek Medical Screening

### Conditions Requiring Medical Clearance
- Heart disease or hypertension
- Respiratory conditions (asthma, COPD)
- Diabetes
- Epilepsy
- Pregnancy
- Recent surgery (within 6 months)

### Fitness Requirements
- Ability to walk 5-7 hours with breaks
- Carry 8-10kg backpack
- Cardiovascular endurance tested

## Insurance Recommendations
Trek insurance should cover:
- High altitude rescue (up to 6,000m)
- Medical evacuation
- Hospital expenses
- Trip cancellation

---
**Remember**: Altitude illness can affect anyone regardless of fitness. Descent is the ONLY reliable cure for severe AMS.
"""


def seed_all():
    """Master seed function"""
    print("=" * 60)
    print("🏔️  TrekMate AI - Seeding Database")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # Clear existing data (optional - comment out for additive seeding)
        print("\n🗑️  Clearing existing data...")
        Review.query.delete()
        Booking.query.delete()
        TrekDocument.query.delete()
        ItineraryItem.query.delete()
        Trek.query.delete()
        GuideProfile.query.delete()
        User.query.filter(User.role != 'admin').delete()
        db.session.commit()

        print("✅ Database cleared (keeping admin)")

        # Seed in order
        seed_users()
        seed_guides()
        seed_treks()
        seed_itineraries()
        seed_documents()
        seed_bookings()
        seed_reviews()

        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   Users: {User.query.filter_by(role='trekker').count()}")
        print(f"   Guides: {GuideProfile.query.count()}")
        print(f"   Treks: {Trek.query.count()}")
        print(f"   Documents: {TrekDocument.query.count()}")
        print(f"   Bookings: {Booking.query.count()}")
        print(f"   Reviews: {Review.query.count()}")
        print("\n🚀 Ready to test TrekMate AI features!")


def seed_users():
    """Create sample trekkers with varied profiles"""
    print("\n👥 Seeding users...")

    users_data = [
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "password": "Test@123",
            "phone": "+91-9876543210",
            "experience_level": "Beginner",
            "fitness_level": "Moderate",
            "preferred_difficulty": "Easy",
            "max_altitude_climbed": 2000,
            "budget_preference": 12000.0,
        },
        {
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@example.com",
            "password": "Test@123",
            "phone": "+91-9876543211",
            "experience_level": "Intermediate",
            "fitness_level": "High",
            "preferred_difficulty": "Moderate",
            "max_altitude_climbed": 3500,
            "budget_preference": 18000.0,
        },
        {
            "name": "Ananya Reddy",
            "email": "ananya.reddy@example.com",
            "password": "Test@123",
            "phone": "+91-9876543212",
            "experience_level": "Advanced",
            "fitness_level": "Athletic",
            "preferred_difficulty": "Difficult",
            "max_altitude_climbed": 5000,
            "budget_preference": 25000.0,
        },
        {
            "name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "password": "Test@123",
            "phone": "+91-9876543213",
            "experience_level": "Expert",
            "fitness_level": "Athletic",
            "preferred_difficulty": "Expert",
            "max_altitude_climbed": 6000,
            "budget_preference": 35000.0,
        },
    ]

    for user_data in users_data:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            phone=user_data["phone"],
            role="trekker",
            status="active",
            experience_level=user_data["experience_level"],
            fitness_level=user_data["fitness_level"],
            preferred_difficulty=user_data["preferred_difficulty"],
            max_altitude_climbed=user_data["max_altitude_climbed"],
            budget_preference=user_data["budget_preference"],
        )
        user.set_password(user_data["password"])
        db.session.add(user)

    db.session.commit()
    print(f"✅ Created {len(users_data)} sample users")


def seed_guides():
    """Create trek guides"""
    print("\n🧗 Seeding guides...")

    guides_data = [
        {
            "name": "Tenzing Sherpa",
            "email": "tenzing.sherpa@trekmate.com",
            "phone": "+91-9800000001",
            "bio": "20+ years high-altitude mountaineering experience. Summited Everest 7 times.",
            "specialization": "High Altitude Expeditions",
            "experience_years": 20,
            "certifications": "NIM Advanced Mountaineering, Wilderness First Responder, Avalanche Level 2",
            "spoken_languages": "English, Hindi, Nepali, Sherpa",
            "rating": 4.9,
        },
        {
            "name": "Arjun Thakur",
            "email": "arjun.thakur@trekmate.com",
            "phone": "+91-9800000002",
            "bio": "Expert in Himalayan treks. Passionate about trekking safety and environmental conservation.",
            "specialization": "Himalayan Treks & Safety",
            "experience_years": 12,
            "certifications": "NIM Basic & Advanced, Wilderness First Aid, Leave No Trace Master",
            "spoken_languages": "English, Hindi, Garhwali",
            "rating": 4.8,
        },
    ]

    for guide_data in guides_data:
        guide = GuideProfile(**guide_data)
        db.session.add(guide)

    db.session.commit()
    print(f"✅ Created {len(guides_data)} guides")


def seed_treks():
    """Create diverse treks"""
    print("\n🏔️  Seeding treks...")

    guides = GuideProfile.query.all()

    treks_data = [
        {
            "trek_name": "Kedarkantha Winter Expedition",
            "slug": "kedarkantha-winter-expedition",
            "location": "Sankri, Uttarkashi",
            "region": "Garhwal Himalayas",
            "country": "India",
            "difficulty": "Easy",
            "duration": 6,
            "distance_km": 20.0,
            "max_altitude_m": 3800,
            "base_camp": "Sankri Village",
            "best_season": "December to April",
            "price": 9500.0,
            "available_slots": 15,
            "total_slots": 20,
            "assigned_staff_id": guides[0].id if guides else None,
            "status": "Open",
            "start_date": datetime.now().date() + timedelta(days=30),
            "end_date": datetime.now().date() + timedelta(days=36),
            "description": "Perfect winter trek for beginners. Experience snow-covered trails, frozen lakes, and 360° Himalayan views from the summit.",
            "highlights": "Summit sunrise, Juda Ka Talab frozen lake, dense pine forests, 360° mountain views",
            "safety_guidelines": "Gradual acclimatization required. Carry warm layers. Trek with certified guide only.",
            "gear_requirements": "Winter boots, gaiters, warm layers, trekking poles, headlamp, sleeping bag rated -10°C",
            "permits_required": "Forest Department Permit from Sankri",
            "latitude": 31.0167,
            "longitude": 78.3833,
            "rating_avg": 4.8,
            "review_count": 47,
        },
        {
            "trek_name": "Hampta Pass Circuit",
            "slug": "hampta-pass-circuit",
            "location": "Manali, Himachal",
            "region": "Pir Panjal Range",
            "country": "India",
            "difficulty": "Moderate",
            "duration": 5,
            "distance_km": 35.0,
            "max_altitude_m": 4270,
            "base_camp": "Jobra",
            "best_season": "June to October",
            "price": 12500.0,
            "available_slots": 12,
            "total_slots": 15,
            "assigned_staff_id": guides[1].id if len(guides) > 1 else None,
            "status": "Open",
            "start_date": datetime.now().date() + timedelta(days=45),
            "end_date": datetime.now().date() + timedelta(days=50),
            "description": "Dramatic landscape transition from lush Kullu Valley to barren Spiti. Cross the stunning Hampta Pass at 4,270m.",
            "highlights": "Hampta Pass crossing, Chandratal Lake, dramatic valley transitions, glacier views",
            "safety_guidelines": "Moderate fitness required. River crossing involved. Acclimatize properly.",
            "gear_requirements": "Trekking boots, layered clothing, rain gear, trekking poles, 50L backpack",
            "permits_required": "Forest Permit, Camping Permit for Chandratal",
            "latitude": 32.3850,
            "longitude": 77.1734,
            "rating_avg": 4.7,
            "review_count": 38,
        },
        {
            "trek_name": "Valley of Flowers & Hemkund Sahib",
            "slug": "valley-of-flowers-hemkund",
            "location": "Govindghat, Uttarakhand",
            "region": "Chamoli Garhwal",
            "country": "India",
            "difficulty": "Moderate",
            "duration": 6,
            "distance_km": 38.0,
            "max_altitude_m": 4632,
            "base_camp": "Ghangaria",
            "best_season": "July to September",
            "price": 14000.0,
            "available_slots": 10,
            "total_slots": 12,
            "assigned_staff_id": guides[0].id if guides else None,
            "status": "Open",
            "start_date": datetime.now().date() + timedelta(days=60),
            "end_date": datetime.now().date() + timedelta(days=66),
            "description": "UNESCO World Heritage Site. Trek through meadows filled with alpine flowers and visit the sacred Hemkund Sahib gurudwara.",
            "highlights": "400+ flower species, Hemkund Sahib, glacial lake, Pushpawati river valley",
            "safety_guidelines": "Monsoon trek - rain gear essential. Steep ascent to Hemkund. Start early to avoid afternoon clouds.",
            "gear_requirements": "Waterproof boots, rain jacket and pants, trekking poles, poncho, day pack",
            "permits_required": "Valley of Flowers National Park Entry, Forest Permit",
            "latitude": 30.7268,
            "longitude": 79.6037,
            "rating_avg": 4.9,
            "review_count": 52,
        },
        {
            "trek_name": "Roopkund Mystery Lake",
            "slug": "roopkund-mystery-lake",
            "location": "Lohajung, Uttarakhand",
            "region": "Chamoli Garhwal",
            "country": "India",
            "difficulty": "Difficult",
            "duration": 8,
            "distance_km": 53.0,
            "max_altitude_m": 5029,
            "base_camp": "Lohajung",
            "best_season": "May to June, September to October",
            "price": 18500.0,
            "available_slots": 8,
            "total_slots": 10,
            "assigned_staff_id": guides[1].id if len(guides) > 1 else None,
            "status": "Open",
            "start_date": datetime.now().date() + timedelta(days=75),
            "end_date": datetime.now().date() + timedelta(days=83),
            "description": "High-altitude trek to the mysterious skeleton lake. Challenging terrain with stunning views of Trishul and Nanda Ghunti peaks.",
            "highlights": "Roopkund glacial lake, human skeletons, Junargali Ridge, Bedni Bugyal meadows, Mt. Trishul views",
            "safety_guidelines": "High altitude - proper acclimatization critical. Technical sections. Good fitness essential.",
            "gear_requirements": "High-altitude boots, crampons, ice axe, 4-season sleeping bag, down jacket, gaiters",
            "permits_required": "Forest Department Permit, Camping Permit",
            "latitude": 30.2890,
            "longitude": 79.7280,
            "rating_avg": 4.6,
            "review_count": 29,
        },
        {
            "trek_name": "Brahmatal Winter Trek",
            "slug": "brahmatal-winter-trek",
            "location": "Lohajung, Uttarakhand",
            "region": "Garhwal Himalayas",
            "country": "India",
            "difficulty": "Easy",
            "duration": 6,
            "distance_km": 24.0,
            "max_altitude_m": 3734,
            "base_camp": "Lohajung",
            "best_season": "December to March",
            "price": 10500.0,
            "available_slots": 14,
            "total_slots": 18,
            "assigned_staff_id": guides[0].id if guides else None,
            "status": "Open",
            "start_date": datetime.now().date() + timedelta(days=90),
            "end_date": datetime.now().date() + timedelta(days=96),
            "description": "Excellent winter trek with lesser crowds. Trek to Brahmatal Lake with spectacular views of Mt. Trishul and Nanda Ghunti.",
            "highlights": "Brahmatal frozen lake, Bekaltal Lake, oak and rhododendron forests, Mt. Trishul close-up views",
            "safety_guidelines": "Winter trek - warm layers essential. Gradual altitude gain. Safe for first-time winter trekkers.",
            "gear_requirements": "Winter boots, gaiters, 4 layers of warm clothing, gloves, woolen cap, trekking poles",
            "permits_required": "Forest Department Permit",
            "latitude": 30.3547,
            "longitude": 79.7085,
            "rating_avg": 4.7,
            "review_count": 34,
        },
    ]

    for trek_data in treks_data:
        trek = Trek(**trek_data)
        db.session.add(trek)

    db.session.commit()
    print(f"✅ Created {len(treks_data)} treks")


def seed_itineraries():
    """Create detailed itineraries for treks"""
    print("\n📅 Seeding itineraries...")

    kedarkantha = Trek.query.filter_by(slug="kedarkantha-winter-expedition").first()

    if kedarkantha:
        itinerary_data = [
            {
                "trek_id": kedarkantha.id,
                "day_number": 1,
                "title": "Dehradun to Sankri Village",
                "description": "Scenic drive through Mussoorie and Yamuna valley. Arrive at Sankri base village. Acclimatization walk in evening.",
                "start_altitude_m": 600,
                "end_altitude_m": 1950,
                "distance_km": 0,
                "trekking_time_hours": 0,
                "campsite": "Sankri Guesthouse",
                "overnight_stay": "Guesthouse / Hotel",
                "meals_included": "Dinner",
                "acclimatization_notes": "First night at altitude. Rest and hydrate well.",
            },
            {
                "trek_id": kedarkantha.id,
                "day_number": 2,
                "title": "Sankri to Juda Ka Talab Camp",
                "description": "Gradual ascent through dense pine forests. First encounter with snow-covered trails. Reach the beautiful frozen Juda Ka Talab lake.",
                "start_altitude_m": 1950,
                "end_altitude_m": 2800,
                "distance_km": 4.0,
                "trekking_time_hours": 4.5,
                "campsite": "Juda Ka Talab",
                "overnight_stay": "Alpine Tents",
                "meals_included": "Breakfast, Lunch, Dinner",
                "acclimatization_notes": "850m altitude gain. Drink 3-4L water. Watch for headache symptoms.",
            },
            {
                "trek_id": kedarkantha.id,
                "day_number": 3,
                "title": "Juda Ka Talab to Kedarkantha Base Camp",
                "description": "Trek through open meadows with stunning mountain views. Gradual ascent to base camp. Prepare for summit day.",
                "start_altitude_m": 2800,
                "end_altitude_m": 3400,
                "distance_km": 4.0,
                "trekking_time_hours": 3.5,
                "campsite": "Kedarkantha Base Camp",
                "overnight_stay": "Alpine Tents",
                "meals_included": "Breakfast, Lunch, Dinner",
                "acclimatization_notes": "Moderate gain. Early dinner and sleep for summit day.",
            },
            {
                "trek_id": kedarkantha.id,
                "day_number": 4,
                "title": "Summit Day - Kedarkantha Peak and Return to Base",
                "description": "Early 3 AM start for summit push. Steep ascent to 3,800m peak. 360° panoramic views of Himalayan giants. Descend back to base camp.",
                "start_altitude_m": 3400,
                "end_altitude_m": 3400,
                "distance_km": 6.0,
                "trekking_time_hours": 7.0,
                "campsite": "Kedarkantha Base Camp",
                "overnight_stay": "Alpine Tents",
                "meals_included": "Breakfast, Packed Lunch, Dinner",
                "acclimatization_notes": "Climb high, sleep low principle. Summit altitude 3,800m.",
            },
            {
                "trek_id": kedarkantha.id,
                "day_number": 5,
                "title": "Base Camp to Sankri",
                "description": "Descend through Juda Ka Talab to Sankri. Celebrate completion of trek. Overnight at Sankri.",
                "start_altitude_m": 3400,
                "end_altitude_m": 1950,
                "distance_km": 8.0,
                "trekking_time_hours": 5.0,
                "campsite": "Sankri Village",
                "overnight_stay": "Guesthouse",
                "meals_included": "Breakfast, Lunch, Dinner",
            },
            {
                "trek_id": kedarkantha.id,
                "day_number": 6,
                "title": "Sankri to Dehradun",
                "description": "Drive back to Dehradun. Trek concludes by evening.",
                "start_altitude_m": 1950,
                "end_altitude_m": 600,
                "distance_km": 0,
                "trekking_time_hours": 0,
                "overnight_stay": "Home",
                "meals_included": "Breakfast",
            },
        ]

        for item_data in itinerary_data:
            item = ItineraryItem(**item_data)
            db.session.add(item)

        db.session.commit()
        print(f"✅ Created {len(itinerary_data)} itinerary items for Kedarkantha")


def seed_documents():
    """Create trek documents for RAG pipeline"""
    print("\n📄 Seeding documents...")

    # Ensure documents directory exists
    os.makedirs(Config.DOCUMENTS_FOLDER, exist_ok=True)

    kedarkantha = Trek.query.filter_by(slug="kedarkantha-winter-expedition").first()

    if not kedarkantha:
        print("⚠️  Kedarkantha trek not found, skipping documents")
        return

    # Create Kedarkantha guide document
    guide_path = os.path.join(Config.DOCUMENTS_FOLDER, "kedarkantha_complete_guide.txt")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(KEDARKANTHA_GUIDE)

    doc1 = TrekDocument(
        trek_id=kedarkantha.id,
        organizer_id=1,  # Admin
        title="Kedarkantha Complete Trekking Guide",
        filename="kedarkantha_complete_guide.txt",
        file_path=guide_path,
        file_type="txt",
        category="route_guide",
        file_size_bytes=len(KEDARKANTHA_GUIDE.encode('utf-8')),
        is_indexed=False,
        chunk_count=0,
    )
    db.session.add(doc1)

    # Create safety manual
    safety_path = os.path.join(Config.DOCUMENTS_FOLDER, "high_altitude_safety_manual.txt")
    with open(safety_path, "w", encoding="utf-8") as f:
        f.write(SAFETY_MANUAL)

    doc2 = TrekDocument(
        trek_id=None,  # General document
        organizer_id=1,
        title="High Altitude Safety & AMS Prevention Manual",
        filename="high_altitude_safety_manual.txt",
        file_path=safety_path,
        file_type="txt",
        category="safety",
        file_size_bytes=len(SAFETY_MANUAL.encode('utf-8')),
        is_indexed=False,
        chunk_count=0,
    )
    db.session.add(doc2)

    db.session.commit()

    # Index documents using RAG service
    try:
        from ai.rag_service import get_rag_service
        rag_service = get_rag_service()

        chunks1 = rag_service.chunk_and_index_document(doc1.id)
        print(f"   ✅ Indexed '{doc1.title}' → {chunks1} chunks")

        chunks2 = rag_service.chunk_and_index_document(doc2.id)
        print(f"   ✅ Indexed '{doc2.title}' → {chunks2} chunks")

    except Exception as e:
        print(f"   ⚠️  Document indexing error: {e}")
        print("   💡 Documents created but not indexed. Run indexing separately.")


def seed_bookings():
    """Create sample bookings"""
    print("\n🎫 Seeding bookings...")

    users = User.query.filter_by(role="trekker").all()
    treks = Trek.query.limit(3).all()

    if not users or not treks:
        print("⚠️  Not enough users or treks for bookings")
        return

    bookings_data = [
        {
            "user_id": users[0].id,
            "trek_id": treks[0].id,
            "status": "Booked",
            "amount": treks[0].price,
            "participants_count": 1,
            "payment_method": "Card",
            "payment_status": "Paid",
            "booking_code": f"TMA-{1000 + users[0].id}",
        },
        {
            "user_id": users[1].id if len(users) > 1 else users[0].id,
            "trek_id": treks[1].id if len(treks) > 1 else treks[0].id,
            "status": "Booked",
            "amount": treks[1].price if len(treks) > 1 else treks[0].price,
            "participants_count": 2,
            "payment_method": "UPI",
            "payment_status": "Paid",
            "booking_code": f"TMA-{1000 + (users[1].id if len(users) > 1 else users[0].id)}",
        },
    ]

    for booking_data in bookings_data:
        booking = Booking(**booking_data)
        db.session.add(booking)

        # Decrease trek slots
        trek = Trek.query.get(booking_data["trek_id"])
        if trek:
            trek.available_slots -= booking_data["participants_count"]

    db.session.commit()
    print(f"✅ Created {len(bookings_data)} bookings")


def seed_reviews():
    """Create sample reviews for sentiment analysis"""
    print("\n⭐ Seeding reviews...")

    users = User.query.filter_by(role="trekker").all()
    treks = Trek.query.all()

    if not users or not treks:
        print("⚠️  Not enough users or treks for reviews")
        return

    reviews_data = [
        {
            "user_id": users[0].id,
            "trek_id": treks[0].id,
            "rating": 5,
            "comment": "Absolutely stunning trek! The Kedarkantha summit views were breathtaking. Our guide Tenzing was extremely knowledgeable about altitude sickness prevention. The acclimatization schedule was perfect, and the food at camps exceeded expectations. Highly recommend for first-time winter trekkers.",
            "difficulty_felt": "As Described",
            "weather_encountered": "Clear & Sunny",
            "guide_rating": 5.0,
            "sentiment_score": 0.95,
            "sentiment_label": "Positive",
        },
        {
            "user_id": users[1].id if len(users) > 1 else users[0].id,
            "trek_id": treks[1].id if len(treks) > 1 else treks[0].id,
            "rating": 4,
            "comment": "Great trek with dramatic landscape changes. The Hampta Pass crossing was challenging but rewarding. Chandratal Lake visit was the highlight. Only complaint - the tents provided were a bit old. Guide Arjun was helpful and always checked our oxygen levels. Would do this trek again!",
            "difficulty_felt": "Slightly Harder",
            "weather_encountered": "Partly Cloudy",
            "guide_rating": 4.5,
            "sentiment_score": 0.75,
            "sentiment_label": "Positive",
        },
        {
            "user_id": users[2].id if len(users) > 2 else users[0].id,
            "trek_id": treks[0].id,
            "rating": 3,
            "comment": "Good trek but transportation from Dehradun was delayed by 3 hours. The trek itself was well-organized. Juda Ka Talab campsite was beautiful. However, I experienced some altitude sickness symptoms on summit day which could have been managed better. The guide did provide Diamox but more rest time would have helped.",
            "difficulty_felt": "Harder Than Expected",
            "weather_encountered": "Windy",
            "guide_rating": 3.5,
            "sentiment_score": 0.45,
            "sentiment_label": "Neutral",
        },
    ]

    for review_data in reviews_data:
        review = Review(**review_data)
        db.session.add(review)

    db.session.commit()
    print(f"✅ Created {len(reviews_data)} reviews")


if __name__ == "__main__":
    seed_all()
