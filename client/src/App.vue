<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth';
import { storeToRefs } from 'pinia';


const router = useRouter()

const userInfoStore = useAuthStore();
const { is_authenticated, username, is_staff, second } = storeToRefs(userInfoStore)

async function onLogout() {
  const r = await axios.post("/api/users/logout/")
  userInfoStore.fetchUserInfo();
  router.go();
}
</script>

<template>
  <div class="container mt-3">
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm rounded-3 px-3 py-2">
      <router-link class="navbar-brand fw-semibold text-primary" to="/">
        <i class="bi bi-book me-2"></i> Менеджер проектов
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNavDropdown">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

          <li class="nav-item">
            <router-link class="nav-link px-3" to="/">Проекты</router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link px-3" to="/columns">Колонки</router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link px-3" to="/tasks">Задачи</router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link px-3" to="/comments">Комментарии</router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link px-3" to="/time-tracking">Учет времени</router-link>
          </li>

          <li v-if="is_authenticated" class="nav-item">
            <router-link class="nav-link px-3" to="/second-auth">2FA</router-link>
          </li>

          <li v-if="is_staff" class="nav-item">
            <router-link class="nav-link px-3" to="/users">Пользователи</router-link>
          </li>
        </ul>

        <div v-if="is_authenticated" class="d-flex align-items-center gap-2">

          <router-link to="/users" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-person-circle me-1"></i>
            {{ username }}
            <span v-if="is_staff"> (админ)</span>
          </router-link>

          <button @click="onLogout" class="btn btn-outline-danger btn-sm">
            <i class="bi bi-box-arrow-right me-1"></i>
            Выйти
          </button>

        </div>
      </div>
    </nav>
  </div>

  <div v-if="!second && is_authenticated && !is_staff" class="container mt-3">
    <div class="alert alert-light border alert-dismissible fade show" role="alert">
      <i class="bi bi-pencil-square me-2 text-muted"></i>
      <span>
        Чтобы создавать, редактировать и удалять задания, пройдите двухфакторную аутентификацию (2FA).
        <router-link to="/second-auth" class="alert-link">Пройти</router-link>
      </span>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  </div>

  <div class="container mt-3">
    <router-view></router-view>
  </div>
</template>

<style>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");
</style>