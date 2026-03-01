import { defineStore } from 'pinia'
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie'

export const useAuthStore = defineStore("auth", () => {
    const username = ref();
    const is_authenticated = ref(null);
    const is_staff = ref(null);
    const permissions = ref([]);

    async function fetchUserInfo() {
        const r = await axios.get("/api/users/me/");

        username.value = r.data.username;
        is_authenticated.value = r.data.is_authenticated;
        is_staff.value = r.data.is_staff;
        permissions.value= r.data.permissions;

        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
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
        username.value = null;
        is_authenticated.value = false;
        is_staff.value = false;
    }
    onBeforeMount(async () => {
        await fetchUserInfo();
    })

    function hasPermission(name){
        return permissions.value.includes(name);
    }

    return {
        username,
        is_authenticated,
        is_staff,
        hasPermission,


        fetchUserInfo,
        login,
        logout
    }
});