<script setup>
import {ref} from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
const key = ref();

const authStore = useAuthStore();

async function onActivate() {
    await axios.post("/api/users/second-login/", {
        key: key.value,
    })
    await authStore.fetchUserInfo();
}

async function onDoSmth() {
    await axios.post("/api/users/do-smth/")
}
</script>

<template>
    <input type="text" v-model="key">
    <button @click="onActivate">Активировать фактор II</button>
    <button @click="onDoSmth">Сделать что-то</button>
</template>