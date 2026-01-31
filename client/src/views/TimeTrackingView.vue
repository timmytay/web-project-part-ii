<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const timeTrackings = ref([]);
const tasks = ref([]);
const timeToAdd = ref({});
const timeToEdit = ref({});

async function fetchTimeTrackings() {
  try {
    loading.value = true;
    const r = await axios.get("/api/timetracking/");
    timeTrackings.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки учета времени:', error);
  } finally {
    loading.value = false;
  }
}

async function fetchTasks() {
  try {
    const r = await axios.get("/api/tasks/");
    tasks.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки задач:', error);
  }
}

async function onTimeAdd() {
  try {
    await axios.post("/api/timetracking/", {
      ...timeToAdd.value,
    });
    timeToAdd.value = {};
    await fetchTimeTrackings();
  } catch (error) {
    console.error('Ошибка добавления учета времени:', error);
  }
}

async function onTimeEditClick(timeTracking) {
  timeToEdit.value = { ...timeTracking };
}

async function onUpdateTime() {
  try {
    await axios.put(`/api/timetracking/${timeToEdit.value.id}/`, {
      ...timeToEdit.value
    });
    await fetchTimeTrackings();
  } catch (error) {
    console.error('Ошибка обновления учета времени:', error);
  }
}

async function onRemoveClick(timeTracking) {
  if (confirm('Вы уверены, что хотите удалить запись учета времени?')) {
    try {
      await axios.delete(`/api/timetracking/${timeTracking.id}/`);
      await fetchTimeTrackings();
    } catch (error) {
      console.error('Ошибка удаления учета времени:', error);
    }
  }
}

onBeforeMount(async () => {
  await Promise.all([fetchTimeTrackings(), fetchTasks()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Учет времени</h2>
      
      <!-- Форма добавления -->
      <form @submit.prevent.stop="onTimeAdd" class="mb-4">
        <div class="row g-2">
          <div class="col-md-4">
            <div class="form-floating">
              <select class="form-select" v-model="timeToAdd.task" required>
                <option :value="task.id" v-for="task in tasks">{{ task.title }}</option>
              </select>
              <label>Задача</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input type="datetime-local" class="form-control" v-model="timeToAdd.start_time" required>
              <label>Начало</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input type="datetime-local" class="form-control" v-model="timeToAdd.end_time">
              <label>Окончание</label>
            </div>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary h-100 w-100">Добавить</button>
          </div>
        </div>
        <div class="row mt-2">
          <div class="col-12">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="timeToAdd.description" placeholder="Описание работы">
              <label>Описание работы</label>
            </div>
          </div>
        </div>
      </form>

      <!-- Список учета времени -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else>
        <div v-for="time in timeTrackings" :key="time.id" class="time-item card mb-2">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-4">
                <strong>{{ time.task_title }}</strong>
              </div>
              <div class="col-md-2">
                <small>
                  Начало:<br>
                  {{ new Date(time.start_time).toLocaleString() }}
                </small>
              </div>
              <div class="col-md-2">
                <small>
                  Окончание:<br>
                  {{ time.end_time ? new Date(time.end_time).toLocaleString() : 'В процессе' }}
                </small>
              </div>
              <div class="col-md-2">
                <p class="card-text mb-1 small">{{ time.description || 'Нет описания' }}</p>
              </div>
              <div class="col-md-2 text-end">
                <button type="button" class="btn btn-success btn-sm" 
                        @click="onTimeEditClick(time)" 
                        data-bs-toggle="modal" 
                        data-bs-target="#editTimeModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-danger btn-sm ms-1" @click="onRemoveClick(time)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования учета времени -->
    <div class="modal fade" id="editTimeModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать учет времени</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <div class="form-floating">
                  <input type="datetime-local" class="form-control" v-model="timeToEdit.start_time" required>
                  <label>Начало</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <input type="datetime-local" class="form-control" v-model="timeToEdit.end_time">
                  <label>Окончание</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <textarea class="form-control" v-model="timeToEdit.description" style="height: 100px"></textarea>
                  <label>Описание работы</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" 
                    @click="onUpdateTime">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.time-item {
  transition: box-shadow 0.2s;
}
.time-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>