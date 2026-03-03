<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import QRCode from 'qrcode'

const key = ref('')
const authStore = useAuthStore()
const totpUrl = ref(null)
const qrcodeUrl = ref(null)
const error = ref(null)
const timeLeft = ref('--:--')
let intervalId = null

const isSecondActive = computed(() => {
    if (!authStore.second || !authStore.second_expire) return false

    const now = Math.floor(Date.now() / 1000)
    const expireTime = Math.floor(Number(authStore.second_expire))
    return expireTime > now
})

function updateTimeLeft() {
    if (!authStore.second_expire) {
        timeLeft.value = '--:--'
        return
    }

    const now = Math.floor(Date.now() / 1000)
    const expireTime = Math.floor(Number(authStore.second_expire))
    const diff = expireTime - now

    if (diff <= 0) {
        timeLeft.value = '00:00'
        if (authStore.second) {
            authStore.second = false
            authStore.second_expire = null
        }
        stopTimer()
        return
    }

    const minutes = Math.floor(diff / 60)
    const seconds = diff % 60
    timeLeft.value =
        `${minutes.toString().padStart(2, '0')}:` +
        `${seconds.toString().padStart(2, '0')}`
}

function startTimer() {
    stopTimer()
    updateTimeLeft()
    intervalId = setInterval(updateTimeLeft, 1000)
}

function stopTimer() {
    if (intervalId) {
        clearInterval(intervalId)
        intervalId = null
        
    }
}
watch(() => authStore.second, (newVal) => {
    if (newVal) {
        startTimer()
    } else {
        stopTimer()
        timeLeft.value = '--:--'
    }
})

watch(totpUrl, async (val) => {
    if (val) {
        qrcodeUrl.value = await QRCode.toDataURL(val)
    }
})

async function onActivate() {
    error.value = null
    try {
        await axios.post('/api/users/second-login/', {
            key: key.value
        })
        await authStore.fetchUserInfo()
        key.value = ''
    } catch (err) {
        error.value = err.response?.data?.key?.[0] || 'Неправильный код'
    }
}

async function getTOTPKey() {
        const r = await axios.post('/api/users/show-totp/')
        totpUrl.value = r.data.url
}

onMounted(async () => {
    await getTOTPKey()
    if (authStore.second && isSecondActive.value) {
        startTimer()
    } else if (authStore.second && !isSecondActive.value) {
        await authStore.fetchUserInfo()
    }
})

onUnmounted(() => {
    stopTimer()
})
</script>

<template>
    <div class="container py-4">
        <h2>Двухфакторная аутентификация</h2>

        <div v-if="authStore.second && isSecondActive">
            <div class="mt-2">
                Осталось времени: <span class="fw-bold">{{ timeLeft }}</span>
            </div>
            <small class="text-muted">
                Для выполнения действий подтвердите личность снова после истечения времени
            </small>
        </div>

        <div v-else>
            <div class="text-center mb-3">
                <img :src="qrcodeUrl" alt="QR Code" style="max-width: 180px;">
            </div>

            <div class="mb-3 text-muted small text-center">
                Отсканируйте QR-код в приложении Google Authenticator, Authy или аналогичном
            </div>

            <div class="mb-2">
                <label class="form-label small">Код подтверждения</label>
                <input type="text" class="form-control" :class="{ 'is-invalid': error }" v-model="key"
                    @keyup.enter="onActivate" placeholder="6-значный код" maxlength="6">
                <div v-if="error" class="invalid-feedback">
                    {{ error }}
                </div>
            </div>

            <button class="btn btn-outline-primary w-100" @click="onActivate" :disabled="!key || key.length < 6">
                Подтвердить
            </button>
        </div>
    </div>
</template>