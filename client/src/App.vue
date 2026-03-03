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
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">менеджер проектов</a>
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
          <li v-if="is_authenticated" class="nav-item">
            <router-link class="nav-link" to="/second-auth">Прохождение 2FA</router-link>
          </li>
          <li v-if="is_staff" class="nav-item">
            <router-link class="nav-link" to="/users">Пользователи</router-link>
          </li>
        </ul>
        <div class="d-flex align-items-center gap-2">
          <router-link v-if="is_authenticated" to="/users" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-person-circle me-1"></i> {{ username }}
            <span v-if="is_staff">(админ)</span>
          </router-link>
          <button v-if="is_authenticated" @click="onLogout" class="btn btn-outline-danger btn-sm">
            <i class="bi bi-box-arrow-right"></i> Выйти</button>
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