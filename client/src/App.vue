<script setup>
import { onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'vue-router'

const router = useRouter()

const goToAdmin = () => {
  window.open('/admin', '_blank')
}

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})
</script>



<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">Task Manager</a>
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
        </ul>
        
        <!-- Кнопка входа в админку -->
        <div class="d-flex">
          <button 
            @click="goToAdmin" 
            class="btn btn-outline-primary"
            title="Перейти в панель администратора"
          >
            <i class="bi bi-shield-lock me-1"></i> Админка
          </button>
        </div>
      </div>
    </nav>
  </div>
  <div class="container">
    <router-view></router-view>
  </div>
</template>

<style>
/* Добавьте Bootstrap Icons если их еще нет */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");
</style>