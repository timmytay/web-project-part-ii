<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const projects = ref([]);
const projectToAdd = ref({});
const projectToEdit = ref({});

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

async function onProjectAdd() {
  try {
    await axios.post("/api/projects/", {
      ...projectToAdd.value,
    });
    projectToAdd.value = {};
    await fetchProjects();
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
    await fetchProjects();
  } catch (error) {
    console.error('Ошибка обновления проекта:', error);
  }
}

async function onRemoveClick(project) {
  if (confirm('Вы уверены, что хотите удалить проект?')) {
    try {
      await axios.delete(`/api/projects/${project.id}/`);
      await fetchProjects();
    } catch (error) {
      console.error('Ошибка удаления проекта:', error);
    }
  }
}

onBeforeMount(async () => {
  await fetchProjects();
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Проекты</h2>
      
      <!-- Форма добавления -->
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

      <!-- Список проектов -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else>
        <div v-for="project in projects" :key="project.id" class="project-item card mb-2">
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

    <!-- Модальное окно редактирования -->
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

<style scoped>
.project-item {
  transition: box-shadow 0.2s;
}
.project-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>