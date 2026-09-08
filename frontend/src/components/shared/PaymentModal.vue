<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box" style="position:relative;">
      <button v-if="step !== 'processing'" class="modal-close" @click="$emit('close')">&times;</button>

      <!-- ===== Payment form ===== -->
      <template v-if="step === 'form'">
        <div class="pay-header">
          <div class="pay-brand">TMA Secure Checkout</div>
          <div class="pay-amount">₹{{ trek.price?.toLocaleString() }}</div>
          <div class="pay-trek">{{ trek.trek_name }} · {{ trek.location }} · {{ formatDate(trek.start_date) }}</div>
        </div>

        <div class="pay-body">
          <div class="pay-methods">
            <button :class="{active: method==='Card'}" @click="method='Card'">Card</button>
            <button :class="{active: method==='UPI'}" @click="method='UPI'">UPI</button>
            <button :class="{active: method==='Cash'}" @click="method='Cash'">Cash</button>
          </div>

          <div v-if="error" class="alert error">{{ error }}</div>

          <!-- Card -->
          <div v-if="method === 'Card'">
            <div class="card-visual">
              <div class="row"><span>TMA Bank</span><span>VISA</span></div>
              <div class="chip"></div>
              <div class="num">{{ cardNumber || '•••• •••• •••• ••••' }}</div>
              <div class="row">
                <span>{{ cardName || 'CARD HOLDER' }}</span>
                <span>{{ expiry || 'MM/YY' }}</span>
              </div>
            </div>
            <div class="field">
              <label>Card Number</label>
              <input :value="cardNumber" @input="onCardNumberInput" placeholder="1234 5678 9012 3456" maxlength="19" />
            </div>
            <div class="field"><label>Cardholder Name</label><input v-model="cardName" placeholder="As on card" /></div>
            <div class="form-row">
              <div class="field">
                <label>Expiry</label>
                <input :value="expiry" @input="onExpiryInput" placeholder="MM/YY" maxlength="5" />
              </div>
              <div class="field">
                <label>CVV</label>
                <input v-model="cvv" type="password" placeholder="123" maxlength="3" />
              </div>
            </div>
          </div>

          <!-- UPI -->
          <div v-else-if="method === 'UPI'">
            <div class="field">
              <label>UPI ID</label>
              <input v-model="upiId" placeholder="yourname@okbank" />
            </div>
            <p style="color:var(--muted); font-size:0.85rem;">Approve the payment request on your UPI app to complete the booking.</p>
          </div>

          <!-- Cash -->
          <div v-else>
            <div class="alert info" style="margin-bottom:0;">
              Pay ₹{{ trek.price?.toLocaleString() }} in cash directly to trek staff at the reporting point. Your slot will be reserved now.
            </div>
          </div>

          <button class="btn block" style="margin-top:18px;" @click="pay">Pay ₹{{ trek.price?.toLocaleString() }}</button>
          <div class="pay-secure"><span class="lock"></span> Payments are encrypted and secure</div>
        </div>
      </template>

      <!-- ===== Processing ===== -->
      <div v-else-if="step === 'processing'" class="pay-processing">
        <div class="spinner"></div>
        <div style="font-weight:600;">Processing payment...</div>
        <div style="color:var(--muted); font-size:0.85rem; margin-top:4px;">Please don't close this window</div>
      </div>

      <!-- ===== Success ===== -->
      <div v-else-if="step === 'success'" class="pay-success">
        <div class="success-tick"></div>
        <div style="font-weight:700; font-size:1.15rem;">Payment Successful</div>
        <div style="color:var(--muted); font-size:0.9rem; margin:6px 0 18px;">
          ₹{{ trek.price?.toLocaleString() }} paid via {{ method }} for {{ trek.trek_name }}
        </div>
        <button class="btn block" @click="$emit('close')">Done</button>
      </div>

      <!-- ===== Error ===== -->
      <div v-else class="pay-processing">
        <div class="alert error">{{ error }}</div>
        <button class="btn outline" @click="step = 'form'">Try Again</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../services/api'

const props = defineProps({ trek: { type: Object, required: true } })
const emit = defineEmits(['close', 'booked'])

const step = ref('form')
const method = ref('Card')
const error = ref('')

const cardNumber = ref('')
const cardName = ref('')
const expiry = ref('')
const cvv = ref('')
const upiId = ref('')

function onCardNumberInput(e) {
  const digits = e.target.value.replace(/\D/g, '').slice(0, 16)
  cardNumber.value = digits.replace(/(.{4})/g, '$1 ').trim()
}
function onExpiryInput(e) {
  let digits = e.target.value.replace(/\D/g, '').slice(0, 4)
  if (digits.length >= 3) digits = digits.slice(0, 2) + '/' + digits.slice(2)
  expiry.value = digits
}

function validate() {
  if (method.value === 'Card') {
    if (cardNumber.value.replace(/\s/g, '').length !== 16) return 'Enter a valid 16-digit card number'
    if (!cardName.value.trim()) return 'Enter the cardholder name'
    if (!/^\d{2}\/\d{2}$/.test(expiry.value)) return 'Enter expiry as MM/YY'
    if (!/^\d{3}$/.test(cvv.value)) return 'Enter a valid 3-digit CVV'
  } else if (method.value === 'UPI') {
    if (!/^[\w.\-]+@[\w.\-]+$/.test(upiId.value)) return 'Enter a valid UPI ID (e.g. name@bank)'
  }
  return ''
}

async function pay() {
  const validationError = validate()
  if (validationError) { error.value = validationError; return }
  error.value = ''
  step.value = 'processing'
  try {
    await new Promise(resolve => setTimeout(resolve, 1100)) // simulate gateway round-trip
    const res = await api.post('/bookings', { trek_id: props.trek.id, payment_method: method.value })
    step.value = 'success'
    emit('booked', res.data.booking)
  } catch (e) {
    error.value = e.response?.data?.error || 'Payment failed. Please try again.'
    step.value = 'error'
  }
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
</script>
