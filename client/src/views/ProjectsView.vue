<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { is_staff } = storeToRefs(authStore)

const loading = ref(false)
const projects = ref([])
const users = ref([])

const projectToAdd = ref({
  name: '',
  description: '',
  user: null
})

const projectToEdit = ref({
  id: null,
  name: '',
  description: '',
  user: null
})

const stats = ref(null)
const exporting = ref(false)

const filters = ref({ name: '' })

const filteredProjects = computed(() =>
  projects.value.filter(p =>
    p.name.toLowerCase().includes(filters.value.name.toLowerCase())
  )
)

function resetFilters() {
  filters.value = { name: '' }
}

async function fetchUsers() {
  if (!is_staff.value) return
  const r = await axios.get('/api/users/')
  users.value = r.data
}

async function fetchProjects() {
  loading.value = true
  const r = await axios.get('/api/projects/')
  projects.value = r.data.map(p => ({
    ...p,
    user_name: users.value.find(u => u.user === p.user)?.username || 'Неизвестный'
  }))
  loading.value = false
}

async function fetchStats() {
  const r = await axios.get('/api/projects/stats/')
  stats.value = r.data
}

async function onProjectAdd() {
  const payload = { ...projectToAdd.value }
  if (!is_staff.value) delete payload.user
  await axios.post('/api/projects/', payload)
  projectToAdd.value = { name: '', description: '', user: null }
  await Promise.all([fetchProjects(), fetchStats()])
}

function onProjectEditClick(project) {
  projectToEdit.value = {
    id: project.id,
    name: project.name,
    description: project.description,
    user: project.user
  }
}

async function onUpdateProject() {
  const payload = { ...projectToEdit.value }
  if (!is_staff.value) delete payload.user
  await axios.put(`/api/projects/${projectToEdit.value.id}/`, payload)
  projectToEdit.value = { id: null, name: '', description: '', user: null }
  await Promise.all([fetchProjects(), fetchStats()])
}

async function onRemoveClick(project) {
  if (!confirm('Вы уверены, что хотите удалить проект?')) return
  await axios.delete(`/api/projects/${project.id}/`)
  await Promise.all([fetchProjects(), fetchStats()])
}

async function exportToExcel() {
  exporting.value = true
  const response = await axios.get('/api/projects/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'projects.xlsx')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
  exporting.value = false
}

onBeforeMount(async () => {
  await fetchUsers()
  await Promise.all([fetchProjects(), fetchStats()])
})
</script>

<template>
<div class="container-fluid">
  <div class="p-2">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Проекты</h2>

      <button class="btn btn-outline-success btn-sm" @click="exportToExcel"
        :disabled="exporting || projects.length === 0">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
        <span v-else>Загрузить в Excel</span>
      </button>
    </div>

    <form @submit.prevent.stop="onProjectAdd" class="mb-4">
      <div class="row g-2">
        <div class="col-md-3">
          <div class="form-floating">
            <input type="text" class="form-control" v-model="projectToAdd.name" required />
            <label>Название проекта</label>
          </div>
        </div>

        <div class="col-md-4">
          <div class="form-floating">
            <input type="text" class="form-control" v-model="projectToAdd.description" />
            <label>Описание</label>
          </div>
        </div>

        <div class="col-md-3" v-if="is_staff">
          <div class="form-floating">
            <select class="form-select" v-model="projectToAdd.user">
              <option :value="null">Текущий пользователь</option>
              <option v-for="user in users" :key="user.user" :value="user.user">
                {{ user.username }}
              </option>
            </select>
            <label>Автор проекта</label>
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
            <input type="text" class="form-control" v-model="filters.name" />
            <label>По названию проекта</label>
          </div>
        </div>
        <div class="col-md-2 d-flex align-items-center">
          <button class="btn btn-outline-secondary w-100" @click="resetFilters">Сбросить</button>
        </div>
      </div>
      <div class="filter-info mt-2 text-muted small">
        Показано: <b>{{ filteredProjects.length }}</b> из <b>{{ projects.length }}</b>
      </div>
    </div>

    <div v-if="stats" class="mb-3 text-muted small">
      Всего проектов: <strong>{{ stats.count }}</strong>
    </div>

    <div v-if="loading" class="text-center"><div class="spinner-border"></div></div>

    <div v-else>
      <div v-if="filteredProjects.length === 0" class="alert alert-info">Проекты не найдены</div>
      <div v-for="project in filteredProjects" :key="project.id" class="project-item card mb-2">
        <div class="card-body row align-items-center">
          <div class="col-md-4"><h5>{{ project.name }}</h5></div>
          <div class="col-md-5">
            <p class="text-muted">{{ project.description || 'Нет описания' }}</p>
            <small v-if="project.user_name" class="text-muted d-block">Автор: {{ project.user_name }}</small>
            <small class="text-muted">Создан: {{ new Date(project.created_at).toLocaleDateString() }}</small>
          </div>
              <div class="col-md-3 text-end">
                <button type="button" class="btn btn-success btn-sm" @click="onProjectEditClick(project)"
                  data-bs-toggle="modal" data-bs-target="#editProjectModal">
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

  <!-- EDIT MODAL -->
  <div class="modal fade" id="editProjectModal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать проект</h5>
          <button class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="form-floating mb-3">
            <input type="text" class="form-control" v-model="projectToEdit.name" />
            <label>Название проекта</label>
          </div>
          <div class="form-floating mb-3">
            <textarea class="form-control" v-model="projectToEdit.description" style="height: 100px"></textarea>
            <label>Описание</label>
          </div>
          <div v-if="is_staff" class="form-floating">
            <select class="form-select" v-model="projectToEdit.user">
              <option v-for="user in users" :key="user.user" :value="user.user">{{ user.username }}</option>
            </select>
            <label>Автор проекта</label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateProject">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style lang="scss" scoped>
.filters-panel {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}
.project-item {
  transition: box-shadow 0.2s;
}
.project-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, .15);
}
</style>