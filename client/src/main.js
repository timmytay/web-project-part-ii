import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap/dist/js/bootstrap"

import "bootstrap-icons/font/bootstrap-icons.css"

import * as bootstrap from 'bootstrap'

const app = createApp(App)

app.config.globalProperties.$bootstrap = bootstrap

app.use(createPinia())
app.use(router)

app.mount('#app')