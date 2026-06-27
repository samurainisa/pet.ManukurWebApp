import { createApp } from 'vue'

import App from '@/app/App.vue'
import { createAppPinia, setupHttpClient } from '@/app/providers'
import router from '@/app/router'

import '@/style.css'

const app = createApp(App)
const pinia = createAppPinia()

app.use(pinia)
setupHttpClient()
app.use(router)
app.mount('#app')
