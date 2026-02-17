<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';

const loading = ref(false);
const columns = ref([]);
const projects = ref([]);
const ColumnToAdd = ref({});
const ColumnToEdit = ref({});
const stats = ref(null);

const filters = ref({
  name: '',
  project: ''
});
// страница колонок
const projectsByID = computed(() => {
  return _.keyBy(projects.value, x => x.id)
})

const filteredColumns = computed(() => {
  return columns.value.filter(column => {
    const matchesName = column.name.toLowerCase().includes(filters.value.name.toLowerCase());
    
    const matchesProject = !filters.value.project || column.project === parseInt(filters.value.project);
    
    return matchesName && matchesProject;
  });
});

function resetFilters() {
  filters.value = {
    name: '',
    project: ''
  };
}

async function fetchProjects() {
  const r = await axios.get("/api/projects/");
  projects.value = r.data;
}

async function fetchColumns() {
  loading.value = true;
  const r = await axios.get("/api/columns/");
  columns.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  try {
    const r = await axios.get("/api/columns/stats/");
    stats.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики колонок:', error);
  }
}

async function onColumnEditClick(column) {
  ColumnToEdit.value = { ...column };
}

async function onUpdateColumn() {
  await axios.put(`/api/columns/${ColumnToEdit.value.id}/`, {
    ...ColumnToEdit.value
  });
  await Promise.all([fetchColumns(), fetchStats()]);
}

async function onColumnAdd() {
  await axios.post("/api/columns/", {
    ...ColumnToAdd.value,
  });
  await Promise.all([fetchColumns(), fetchStats()]);
}

async function onRemoveClick(column) {
  await axios.delete(`/api/columns/${column.id}/`);
  await Promise.all([fetchColumns(), fetchStats()]);
}

onBeforeMount(async () => {
  await Promise.all([fetchColumns(), fetchProjects(), fetchStats()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Колонки</h2>

      <form @submit.prevent.stop="onColumnAdd" class="mb-4">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="addColumnName"
                v-model="ColumnToAdd.name" 
                required
              >
              <label for="addColumnName">Название</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="addColumnProject"
                v-model="ColumnToAdd.project" 
                required
              >
                <option :value="p.id" v-for="p in projects">{{ p.name }}</option>
              </select>
              <label for="addColumnProject">Проект</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary">Добавить</button>
          </div>
        </div>
      </form>

      <!-- Панель фильтров -->
      <div class="filters-panel mb-4">
        <h5>Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-5">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterName"
                v-model="filters.name"
                placeholder="Введите название"
              >
              <label for="filterName">По названию</label>
            </div>
          </div>
          <div class="col-md-5">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterProject"
                v-model="filters.project"
              >
                <option value="">Все проекты</option>
                <option :value="p.id" v-for="p in projects">{{ p.name }}</option>
              </select>
              <label for="filterProject">По проекту</label>
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
          Показано: <b>{{ filteredColumns.length }}</b> из <b>{{ columns.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small">
        Всего колонок: <b>{{ stats.count }}</b>
      </div>

      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <div v-else>
        <!-- Сообщение если ничего не найдено -->
        <div v-if="filteredColumns.length === 0" class="alert alert-info">
          Колонки не найдены
        </div>
        
        <div v-for="item in filteredColumns" class="column-item" :key="item.id">
          <div>{{ item.name }}</div>
          <div>{{ projectsByID[item.project]?.name }}</div>
          <button 
            type="button" 
            class="btn btn-success" 
            @click="onColumnEditClick(item)" 
            data-bs-toggle="modal"
            data-bs-target="#editColumnModal"
          >
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editColumnModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать колонку</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col">
                <div class="form-floating">
                  <input 
                    type="text" 
                    class="form-control" 
                    id="editColumnName"
                    v-model="ColumnToEdit.name"
                  >
                  <label for="editColumnName">Название</label>
                </div>
              </div>
              <div class="col-auto">
                <div class="form-floating">
                  <select 
                    class="form-select" 
                    id="editColumnProject"
                    v-model="ColumnToEdit.project"
                  >
                    <option :value="p.id" v-for="p in projects">{{ p.name }}</option>
                  </select>
                  <label for="editColumnProject">Проект</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              data-bs-dismiss="modal"
              @click="onUpdateColumn"
            >
              Сохранить
            </button>
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

.column-item {
  padding: 0.5rem;
  border: 1px solid silver;
  border-radius: 8px;
  margin: 0.5rem 0;
  display: grid;
  grid-template-columns: 1fr 1fr auto auto auto;
  gap: 16px;
  justify-content: space-between;
  align-content: center;
  align-items: center;
}
</style>ы