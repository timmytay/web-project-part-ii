import { defineStore } from 'pinia'
import { ref } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie'

export const useAuthStore = defineStore("auth", () => {
    const userInfo = ref({});
    const username = ref();
    const is_authenticated = ref(false);
    const isLoading = ref(true);

    async function fetchUserInfo() {
        try {
            isLoading.value = true;
            const r = await axios.get("/api/users/me/");
            userInfo.value = r.data;
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
            username.value = r.data.username;
            is_authenticated.value = r.data.is_authenticated;
            return true;
        } catch (error) {
            userInfo.value = null;
            is_authenticated.value = false;
            return false;
        }
        finally {
            isLoading.value = false;
        }
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
        try {
            await axios.post("/api/users/logout/");
        } finally {
            userInfo.value = {};
            username.value = null;
            is_authenticated.value = false;
        }
    }

    return {
        userInfo,
        username,
        is_authenticated,
        isLoading,
        fetchUserInfo,
        login,
        logout
    }
});