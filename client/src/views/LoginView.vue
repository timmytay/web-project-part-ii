<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

async function onLoginFormSubmit() {
  errorMessage.value = '';
  isLoading.value = true;
  
  try {
    const success = await authStore.login({
      username: username.value,
      password: password.value,
    });
    
    if (success) {
      await router.push({ name: 'ProjectsView' });
    } else {
      errorMessage.value = 'Неверное имя пользователя или пароль';
    }
  } catch (error) {
    errorMessage.value = 'Ошибка при входе. Попробуйте еще раз.';
  } finally {
    isLoading.value = false;
    username.value = '';
    password.value = '';
  }
}
</script>

<template>
  <form @submit.stop.prevent="onLoginFormSubmit" class="form d-flex flex-column p-3" style="gap: 8px">
    <input placeholder="Логин (пример: tay)" class="form-control" type="text" v-model="username" :disabled="isLoading" required>
    <input placeholder="Пароль" class="form-control" type="password" v-model="password" :disabled="isLoading" required>
    <button class="btn btn-info" :disabled="isLoading">
      <span v-if="isLoading">Вход...</span>
      <span v-else>Войти</span>
    </button>
    <div v-if="errorMessage" class="alert alert-danger mt-2" style="padding: 8px; font-size: 14px;">
      {{ errorMessage }}
    </div>
  </form>
</template>

<style>
</style>