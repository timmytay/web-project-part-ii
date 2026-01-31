import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// ТОЛЬКО ОДИН импорт Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'

// ТОЛЬКО ОДИН импорт Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

// Импортируем Bootstrap JavaScript КАК МОДУЛЬ
import * as bootstrap from 'bootstrap'

const app = createApp(App)

// Делаем Bootstrap доступным глобально во всех компонентах
app.config.globalProperties.$bootstrap = bootstrap

app.use(createPinia())
app.use(router)

app.mount('#app')