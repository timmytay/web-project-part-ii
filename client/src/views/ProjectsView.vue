<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const projects = ref([]);
const projectToAdd = ref({});
const projectToEdit = ref({});
const stats = ref(null);
const exporting = ref(false);
// здесь у нас проекты
const filters = ref({
  name: ''
});

const filteredProjects = computed(() => {
  return projects.value.filter(project => {
    const matchesName = project.name.toLowerCase().includes(filters.value.name.toLowerCase());
    return matchesName;
  });
});

function resetFilters() {
  filters.value = {
    name: ''
  };
}

async function fetchProjects() {
  try {
    loading.value = true;
    const r = await axios.get("/api/projects/");
    projects.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки проектов:', error);
  } finally {
    loading.value = false;
  }
}

async function fetchStats() {
  try {
    const r = await axios.get("/api/projects/stats/");
    stats.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики проектов:', error);
  }
}

async function onProjectAdd() {
  try {
    await axios.post("/api/projects/", {
      ...projectToAdd.value,
    });
    projectToAdd.value = {};
    await Promise.all([fetchProjects(), fetchStats()]);
  } catch (error) {
    console.error('Ошибка добавления проекта:', error);
  }
}

async function onProjectEditClick(project) {
  projectToEdit.value = { ...project };
}

async function onUpdateProject() {
  try {
    await axios.put(`/api/projects/${projectToEdit.value.id}/`, {
      ...projectToEdit.value
    });
    await Promise.all([fetchProjects(), fetchStats()]);
  } catch (error) {
    console.error('Ошибка обновления проекта:', error);
  }
}

async function onRemoveClick(project) {
  if (confirm('Вы уверены, что хотите удалить проект?')) {
    try {
      await axios.delete(`/api/projects/${project.id}/`);
      await Promise.all([fetchProjects(), fetchStats()]);
    } catch (error) {
      console.error('Ошибка удаления проекта:', error);
    }
  }
}

async function exportToExcel() {
  try {
    exporting.value = true;
    
    const response = await axios.get("/api/projects/export-excel/", {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'projects.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Ошибка экспорта:', error);
    alert('Не удалось выгрузить данные');
  } finally {
    exporting.value = false;
  }
}

onBeforeMount(async () => {
  await Promise.all([fetchProjects(), fetchStats()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Проекты</h2>
        <button 
          class="btn btn-outline-success btn-sm" 
          @click="exportToExcel" 
          :disabled="exporting || projects.length === 0"
        >
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          <span v-else>Загрузить в Excel</span>
        </button>
      </div>
      
      <form @submit.prevent.stop="onProjectAdd" class="mb-4">
        <div class="row g-2">
          <div class="col-md-4">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="projectToAdd.name" required>
              <label>Название проекта</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="projectToAdd.description">
              <label>Описание</label>
            </div>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary h-100 w-100">Добавить проект</button>
          </div>
        </div>
      </form>

      <div class="filters-panel mb-4">
        <h5>Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-10">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterName"
                v-model="filters.name"
                placeholder="Введите название"
              >
              <label for="filterName">По названию проекта</label>
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-center">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle"></i> Сбросить
            </button>
          </div>
        </div>
        
        <div class="filter-info mt-2 text-muted small">
          Показано: <b>{{ filteredProjects.length }}</b> из <b>{{ projects.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small">
        Всего проектов: <strong>{{ stats.count }}</strong>
      </div>

      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else>
        <div v-if="filteredProjects.length === 0" class="alert alert-info">
          Проекты не найдены
        </div>
        
        <div v-for="project in filteredProjects" :key="project.id" class="project-item card mb-2">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-4">
                <h5 class="card-title">{{ project.name }}</h5>
              </div>
              <div class="col-md-5">
                <p class="card-text text-muted">{{ project.description || 'Нет описания' }}</p>
                <small class="text-muted">Создан: {{ new Date(project.created_at).toLocaleDateString() }}</small>
              </div>
              <div class="col-md-3 text-end">
                <button type="button" class="btn btn-success btn-sm" 
                        @click="onProjectEditClick(project)" 
                        data-bs-toggle="modal" 
                        data-bs-target="#editProjectModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-danger btn-sm ms-1" @click="onRemoveClick(project)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editProjectModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать проект</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="projectToEdit.name" required>
              <label>Название проекта</label>
            </div>
            <div class="form-floating">
              <textarea class="form-control" v-model="projectToEdit.description" style="height: 100px"></textarea>
              <label>Описание</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" 
                    @click="onUpdateProject">Сохранить</button>
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

.project-item {
  transition: box-shadow 0.2s;
}
.project-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>