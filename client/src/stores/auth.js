import { defineStore } from 'pinia'
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie'

export const useAuthStore = defineStore("auth", () => {
    const userInfo = ref({});
    const username = ref();
    const is_authenticated = ref(null);
    const is_staff = ref(null);

    async function fetchUserInfo() {
        const r = await axios.get("/api/users/me/");
        userInfo.value = r.data;
        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
        username.value = r.data.username;
        is_authenticated.value = r.data.is_authenticated;
        is_staff.value = r.data.is_staff;
        return true;
    }

    async function login(credentials) {
        try {
            await axios.post("/api/users/login/", credentials);
            const success = await this.fetchUserInfo();
            return success;
        } catch (error) {
            is_authenticated.value = false;
            return false;
        }
    }

    async function logout() {
        await axios.post("/api/users/logout/");
        userInfo.value = {};
        username.value = null;
        is_authenticated.value = false;
        is_staff.value = false;
    }
    onBeforeMount(async () => {
        await fetchUserInfo();
    })

    return {
        userInfo,
        username,
        is_authenticated,
        is_staff,
        fetchUserInfo,
        login,
        logout
    }
});