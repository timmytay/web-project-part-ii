<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const timeTrackings = ref([]);
const tasks = ref([]);
const timeToAdd = ref({});
const timeToEdit = ref({});
const stats = ref(null);

const filters = ref({
  task: '',
  description: '',
  dateFrom: '',
  dateTo: ''
});

const filteredTimeTrackings = computed(() => {
  return timeTrackings.value.filter(time => {
    const matchesTask = !filters.value.task || time.task === parseInt(filters.value.task);
    
    const matchesDescription = time.description?.toLowerCase().includes(filters.value.description.toLowerCase()) ?? true;
    
    let matchesDateFrom = true;
    if (filters.value.dateFrom) {
      const startDate = new Date(time.start_time);
      const filterDate = new Date(filters.value.dateFrom);
      matchesDateFrom = startDate >= filterDate;
    }
    
    let matchesDateTo = true;
    if (filters.value.dateTo) {
      const endDate = time.end_time ? new Date(time.end_time) : new Date();
      const filterDate = new Date(filters.value.dateTo);
      filterDate.setHours(23, 59, 59);
      matchesDateTo = endDate <= filterDate;
    }
    
    return matchesTask && matchesDescription && matchesDateFrom && matchesDateTo;
  });
});

function resetFilters() {
  filters.value = {
    task: '',
    description: '',
    dateFrom: '',
    dateTo: ''
  };
}

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

async function fetchStats() {
  try {
    const r = await axios.get("/api/timetracking/stats/");
    stats.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики учета времени:', error);
  }
}

async function onTimeAdd() {
  try {
    await axios.post("/api/timetracking/", {
      ...timeToAdd.value,
    });
    timeToAdd.value = {};
    await Promise.all([fetchTimeTrackings(), fetchStats()]);
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
    await Promise.all([fetchTimeTrackings(), fetchStats()]);
  } catch (error) {
    console.error('Ошибка обновления учета времени:', error);
  }
}

async function onRemoveClick(timeTracking) {
  if (confirm('Вы уверены, что хотите удалить запись учета времени?')) {
    try {
      await axios.delete(`/api/timetracking/${timeTracking.id}/`);
      await Promise.all([fetchTimeTrackings(), fetchStats()]);
    } catch (error) {
      console.error('Ошибка удаления учета времени:', error);
    }
  }
}
// временной трекинг
onBeforeMount(async () => {
  await Promise.all([fetchTimeTrackings(), fetchTasks(), fetchStats()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Учет времени</h2>
      
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

      <!-- Панель фильтров -->
      <div class="filters-panel mb-4">
        <h5>Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-3">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterTask"
                v-model="filters.task"
              >
                <option value="">Все задачи</option>
                <option :value="task.id" v-for="task in tasks">{{ task.title }}</option>
              </select>
              <label for="filterTask">По задаче</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterDescription"
                v-model="filters.description"
                placeholder="Введите описание"
              >
              <label for="filterDescription">По описанию</label>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-floating">
              <input 
                type="date" 
                class="form-control" 
                id="filterDateFrom"
                v-model="filters.dateFrom"
              >
              <label for="filterDateFrom">Дата с</label>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-floating">
              <input 
                type="date" 
                class="form-control" 
                id="filterDateTo"
                v-model="filters.dateTo"
              >
              <label for="filterDateTo">Дата по</label>
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-center">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle"></i> Сбросить
            </button>
          </div>
        </div>
        
        <!-- Информация о количестве отфильтрованных записей -->
        <div class="filter-info mt-2 text-muted small">
          Показано: <b>{{ filteredTimeTrackings.length }}</b> из <b>{{ timeTrackings.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small">
        Всего записей учета времени: <strong>{{ stats.count }}</strong>
      </div>

      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else>
        <!-- Сообщение если ничего не найдено -->
        <div v-if="filteredTimeTrackings.length === 0" class="alert alert-info">
          Записи учета времени не найдены
        </div>
        
        <div v-for="time in filteredTimeTrackings" :key="time.id" class="time-item card mb-2">
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

<style lang="scss" scoped>
.filters-panel {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  
  h5 {
    margin-bottom: 1rem;
    color: #495057;
    font-size: 1rem;
  }
}

.filter-info {
  font-size: 0.875rem;
}

.time-item {
  transition: box-shadow 0.2s;
}
.time-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>