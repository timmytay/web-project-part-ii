<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'vue-router'
import { useAuthStore} from './stores/auth';
import { storeToRefs } from 'pinia';

const router = useRouter()
const userInfoStore = useAuthStore();
const {is_authenticated} = storeToRefs(userInfoStore)

async function onLogout() {
  const r = await axios.post("/api/users/logout/")
  userInfoStore.fetchUserInfo();
  
  router.go()
}

onBeforeMount(async () => {
  await userInfoStore.fetchUserInfo();
})
</script>

<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">управление задачами</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown"
        aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavDropdown">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Проекты</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/columns">Колонки</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/tasks">Задачи</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/comments">Комментарии</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/time-tracking">Учет времени</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/users">Пользователи</router-link>
          </li>
        </ul>
          <button @click="onLogout" v-if="is_authenticated">Выйти</button>
      </div>
    </nav>
  </div>
  <div class="container">
    <router-view></router-view>
  </div>
</template>

<style>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");
</style>