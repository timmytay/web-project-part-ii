<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const tasks = ref([]);
const columns = ref([]);
const taskToAdd = ref({});
const taskToEdit = ref({});
const taskAddPictureRef = ref(null);
const taskAddImageUrl = ref('');
const taskEditPictureRef = ref(null);
const taskEditImageUrl = ref('');
const taskToEditOriginal = ref(null);
const removeImageFlag = ref(false);
const imageViewUrl = ref('');
const imageViewModal = ref(null);
const stats = ref(null);

// Фильтры
const filters = ref({
  title: '',
  column: '',
  status: '',
  priority: ''
});

const statusOptions = [
  { value: 'todo', label: 'К выполнению' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'review', label: 'На проверке' },
  { value: 'done', label: 'Выполнено' }
];

const priorityOptions = [
  { value: 'low', label: 'Низкий' },
  { value: 'medium', label: 'Средний' },
  { value: 'high', label: 'Высокий' }
];

// Отфильтрованные задачи
const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    // Фильтр по названию
    const matchesTitle = task.title.toLowerCase().includes(filters.value.title.toLowerCase());
    
    // Фильтр по колонке
    const matchesColumn = !filters.value.column || task.column === parseInt(filters.value.column);
    
    // Фильтр по статусу
    const matchesStatus = !filters.value.status || task.status === filters.value.status;
    
    // Фильтр по приоритету
    const matchesPriority = !filters.value.priority || task.priority === filters.value.priority;
    
    return matchesTitle && matchesColumn && matchesStatus && matchesPriority;
  });
});

// Сброс фильтров
function resetFilters() {
  filters.value = {
    title: '',
    column: '',
    status: '',
    priority: ''
  };
}

async function fetchTasks() {
  try {
    loading.value = true;
    const r = await axios.get("/api/tasks/");
    tasks.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки задач:', error);
  } finally {
    loading.value = false;
  }
}

async function fetchColumns() {
  try {
    const r = await axios.get("/api/columns/");
    columns.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки колонок:', error);
  }
}

async function fetchStats() {
  try {
    const r = await axios.get("/api/tasks/stats/");
    stats.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error);
  }
}

function taskAddPictureChange() {
  if (taskAddPictureRef.value.files[0]) {
    taskAddImageUrl.value = URL.createObjectURL(taskAddPictureRef.value.files[0]);
  } else {
    taskAddImageUrl.value = '';
  }
}

function taskEditPictureChange() {
  if (taskEditPictureRef.value.files[0]) {
    taskEditImageUrl.value = URL.createObjectURL(taskEditPictureRef.value.files[0]);
    removeImageFlag.value = false;
  } else {
    taskEditImageUrl.value = '';
  }
}

function openImageViewModal(imageUrl) {
  imageViewUrl.value = imageUrl;

  const modalElement = document.getElementById('imageViewModal');
  if (modalElement) {
    modalElement.style.display = 'block';
    modalElement.classList.add('show');

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    backdrop.id = 'imageViewModalBackdrop';
    document.body.appendChild(backdrop);

    backdrop.onclick = closeImageViewModal;

    const handleEsc = (e) => e.key === 'Escape' && closeImageViewModal();
    document.addEventListener('keydown', handleEsc);

    imageViewModal.value = { handleEsc };
  }
}

function closeImageViewModal() {
  const modalElement = document.getElementById('imageViewModal');
  const backdrop = document.getElementById('imageViewModalBackdrop');

  if (modalElement) {
    modalElement.style.display = 'none';
    modalElement.classList.remove('show');
  }

  if (backdrop) backdrop.remove();
  if (imageViewModal.value?.handleEsc) {
    document.removeEventListener('keydown', imageViewModal.value.handleEsc);
  }

  imageViewUrl.value = '';
  imageViewModal.value = null;
}

async function onTaskAdd() {
  try {
    const formData = new FormData();

    if (taskAddPictureRef.value.files[0]) {
      formData.append('picture', taskAddPictureRef.value.files[0]);
    }

    // Добавляем все поля задачи
    for (const key in taskToAdd.value) {
      if (taskToAdd.value[key] !== undefined && taskToAdd.value[key] !== null) {
        formData.append(key, taskToAdd.value[key]);
      }
    }

    await axios.post("/api/tasks/", formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    taskToAdd.value = {};
    taskAddImageUrl.value = '';
    if (taskAddPictureRef.value) taskAddPictureRef.value.value = '';

    await Promise.all([fetchTasks(), fetchStats()]);
  } catch (error) {
    console.error('Ошибка добавления задачи:', error);
    alert('Ошибка при добавлении задачи');
  }
}

async function onTaskEditClick(task) {
  taskToEdit.value = { ...task };
  taskToEditOriginal.value = { ...task };

  taskEditImageUrl.value = task.picture || '';
  removeImageFlag.value = false;

  if (taskEditPictureRef.value) {
    taskEditPictureRef.value.value = '';
  }
}

async function onUpdateTask() {
  try {
    const formData = new FormData();

    if (taskEditPictureRef.value.files[0]) {

      formData.append('picture', taskEditPictureRef.value.files[0]);
    } else if (removeImageFlag.value && taskToEditOriginal.value?.picture) {

      formData.append('picture', '');
    }

    formData.append('title', taskToEdit.value.title);
    formData.append('description', taskToEdit.value.description);
    formData.append('column', taskToEdit.value.column);
    formData.append('status', taskToEdit.value.status);
    formData.append('priority', taskToEdit.value.priority);
    if (taskToEdit.value.due_date) {
      formData.append('due_date', taskToEdit.value.due_date);
    }

    await axios.patch(`/api/tasks/${taskToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    taskEditImageUrl.value = '';
    taskToEdit.value = {};
    taskToEditOriginal.value = null;
    removeImageFlag.value = false;

    if (taskEditPictureRef.value) taskEditPictureRef.value.value = '';

    await Promise.all([fetchTasks(), fetchStats()]); // Обновляем и задачи и статистику
  } catch (error) {
    console.error('Ошибка обновления задачи:', error);
    alert('Ошибка при обновлении задачи');
  }
}

async function onRemoveClick(task) {
  if (confirm('Вы уверены, что хотите удалить задачу?')) {
    try {
      await axios.delete(`/api/tasks/${task.id}/`);
      await Promise.all([fetchTasks(), fetchStats()]);
    } catch (error) {
      console.error('Ошибка удаления задачи:', error);
      alert('Ошибка при удалении задачи');
    }
  }
}

function getStatusLabel(status) {
  const found = statusOptions.find(s => s.value === status);
  return found ? found.label : status;
}

function getPriorityLabel(priority) {
  const found = priorityOptions.find(p => p.value === priority);
  return found ? found.label : priority;
}

function removeAddPicture() {
  taskAddImageUrl.value = '';
  if (taskAddPictureRef.value) taskAddPictureRef.value.value = '';
}

function removeEditPicture() {
  taskEditImageUrl.value = '';
  if (taskEditPictureRef.value) taskEditPictureRef.value.value = '';
}

function removeExistingImage() {
  removeImageFlag.value = true;
  taskEditImageUrl.value = '';
  if (taskEditPictureRef.value) taskEditPictureRef.value.value = '';
}

function resetEditModal() {
  removeEditPicture();
  removeImageFlag.value = false;
}

onBeforeMount(async () => {
  await Promise.all([fetchTasks(), fetchColumns(), fetchStats()]);
});
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Задачи</h2>

      <form @submit.prevent.stop="onTaskAdd" class="mb-4">
        <div class="row g-2 align-items-end">

          <div class="col-md-2">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="taskToAdd.title" required>
              <label>Название задачи</label>
            </div>
          </div>

          <div class="col-md-2">
            <div class="form-floating">
              <select class="form-select" v-model="taskToAdd.column" required>
                <option :value="col.id" v-for="col in columns">{{ col.name }}</option>
              </select>
              <label>Колонка</label>
            </div>
          </div>

          <div class="col-md-2">
            <div class="form-floating">
              <select class="form-select" v-model="taskToAdd.priority">
                <option value="medium">Средний</option>
                <option value="low">Низкий</option>
                <option value="high">Высокий</option>
              </select>
              <label>Приоритет</label>
            </div>
          </div>

          <div class="col-md-2">
            <div class="form-floating">
              <select class="form-select" v-model="taskToAdd.status">
                <option value="todo">К выполнению</option>
                <option value="in_progress">В работе</option>
                <option value="review">На проверке</option>
                <option value="done">Выполнено</option>
              </select>
              <label>Статус</label>
            </div>
          </div>

          <div class="col-md-2">
            <div class="form-floating">
              <input type="date" class="form-control" v-model="taskToAdd.due_date">
              <label>Срок выполнения</label>
            </div>
          </div>

          <div class="col-md-2">
            <div class="input-group">
              <input class="form-control" type="file" ref="taskAddPictureRef" @change="taskAddPictureChange"
                accept="image/*">
              <button v-if="taskAddImageUrl" type="button" class="btn btn-outline-secondary" @click="removeAddPicture"
                title="Удалить изображение">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>

          <div class="col-auto">
            <div v-if="taskAddImageUrl" class="position-relative">
              <img :src="taskAddImageUrl" style="max-height: 60px;" class="img-thumbnail clickable-image" alt=""
                @click="openImageViewModal(taskAddImageUrl)" title="Нажмите для увеличения">
              <div class="image-hint">Нажмите</div>
            </div>
          </div>

          <div class="col-md-12 mt-2">
            <div class="form-floating">
              <textarea class="form-control" v-model="taskToAdd.description" placeholder="Описание задачи"
                style="height: 60px"></textarea>
              <label>Описание задачи</label>
            </div>
          </div>

          <div class="col-md-12 mt-2">
            <button class="btn btn-primary">Добавить задачу</button>
          </div>
        </div>
      </form>

      <!-- Панель фильтров -->
      <div class="filters-panel mb-4">
        <h5>Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-3">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterTitle"
                v-model="filters.title"
                placeholder="Введите название"
              >
              <label for="filterTitle">По названию</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterColumn"
                v-model="filters.column"
              >
                <option value="">Все колонки</option>
                <option :value="col.id" v-for="col in columns">{{ col.name }}</option>
              </select>
              <label for="filterColumn">По колонке</label>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterStatus"
                v-model="filters.status"
              >
                <option value="">Все статусы</option>
                <option v-for="status in statusOptions" :value="status.value">
                  {{ status.label }}
                </option>
              </select>
              <label for="filterStatus">По статусу</label>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterPriority"
                v-model="filters.priority"
              >
                <option value="">Все приоритеты</option>
                <option v-for="priority in priorityOptions" :value="priority.value">
                  {{ priority.label }}
                </option>
              </select>
              <label for="filterPriority">По приоритету</label>
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
          Показано: <b>{{ filteredTasks.length }}</b> из <b>{{ tasks.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small">
        Всего задач: <strong>{{ stats.count }}</strong>
      </div>


      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <div v-else>
        <!-- Сообщение если ничего не найдено -->
        <div v-if="filteredTasks.length === 0" class="alert alert-info">
          Задачи не найдены
        </div>
        
        <div v-for="task in filteredTasks" :key="task.id" class="task-item card mb-2">
          <div class="card-body">
            <div class="row align-items-center">

              <div class="col-auto">
                <div v-if="task.picture" class="position-relative">
                  <img :src="task.picture" style="max-height: 60px; max-width: 60px;"
                    class="img-thumbnail clickable-image" alt="Изображение задачи"
                    @click="openImageViewModal(task.picture)" title="Нажмите для увеличения">
                  <div class="image-hint">Нажмите</div>
                </div>
                <div v-else class="text-muted small">
                  Нет изображения
                </div>
              </div>

              <div class="col-md-3">
                <h6 class="card-title">{{ task.title }}</h6>
                <p class="card-text mb-1">{{ task.description }}</p>
                <small class="text-muted">{{ task.column_name }}</small>
              </div>

              <div class="col-md-2">
                <span class="badge" :class="{
                  'bg-secondary': task.status === 'todo',
                  'bg-primary': task.status === 'in_progress',
                  'bg-warning': task.status === 'review',
                  'bg-success': task.status === 'done'
                }">
                  {{ getStatusLabel(task.status) }}
                </span>
              </div>
              <div class="col-md-2">
                <span class="badge" :class="{
                  'bg-success': task.priority === 'low',
                  'bg-warning': task.priority === 'medium',
                  'bg-danger': task.priority === 'high'
                }">
                  {{ getPriorityLabel(task.priority) }}
                </span>
              </div>

              <div class="col-md-2">
                <small class="text-muted">
                  Срок: {{ task.due_date ? new Date(task.due_date).toLocaleDateString() : 'Не указан' }}
                </small>
                <br>
                <small class="text-muted">
                  Создана: {{ new Date(task.created_at).toLocaleDateString() }}
                </small>
              </div>

              <div class="col-md-2 text-end">
                <button type="button" class="btn btn-success btn-sm" @click="onTaskEditClick(task)"
                  data-bs-toggle="modal" data-bs-target="#editTaskModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-danger btn-sm ms-1" @click="onRemoveClick(task)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editTaskModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать задачу</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12" v-if="taskToEdit.picture && !removeImageFlag">
                <div class="text-center mb-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <p class="text-muted mb-0">Текущее изображение:</p>
                    <button type="button" class="btn btn-outline-danger btn-sm" @click="removeExistingImage"
                      title="Удалить изображение">
                      <i class="bi bi-trash"></i> Удалить
                    </button>
                  </div>
                  <div class="position-relative d-inline-block">
                    <img :src="taskToEdit.picture" style="max-height: 100px;" class="img-thumbnail clickable-image"
                      alt="Текущее изображение" @click="openImageViewModal(taskToEdit.picture)"
                      title="Нажмите для увеличения">
                    <div class="image-hint">Нажмите</div>
                  </div>
                  <div v-if="removeImageFlag" class="alert alert-warning mt-2 small">
                    Изображение будет удалено при сохранении
                  </div>
                </div>
              </div>

              <div class="col-12">
                <div class="mb-3">
                  <label class="form-label">Новое изображение</label>
                  <div class="input-group">
                    <input class="form-control" type="file" ref="taskEditPictureRef" @change="taskEditPictureChange"
                      accept="image/*">
                    <button v-if="taskEditImageUrl" type="button" class="btn btn-outline-secondary"
                      @click="removeEditPicture">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>

                <div class="text-center mb-3" v-if="taskEditImageUrl && taskEditPictureRef?.files?.length">
                  <p class="text-muted mb-1">Предпросмотр нового изображения:</p>
                  <div class="position-relative d-inline-block">
                    <img :src="taskEditImageUrl" style="max-height: 100px;" class="img-thumbnail clickable-image"
                      alt="Новое изображение" @click="openImageViewModal(taskEditImageUrl)"
                      title="Нажмите для увеличения">
                    <div class="image-hint">Нажмите</div>
                  </div>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <input type="text" class="form-control" v-model="taskToEdit.title" required>
                  <label>Название задачи</label>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" v-model="taskToEdit.column">
                    <option :value="col.id" v-for="col in columns">{{ col.name }}</option>
                  </select>
                  <label>Колонка</label>
                </div>
              </div>

              <div class="col-md-6">
                <div class="form-floating">
                  <select class="form-select" v-model="taskToEdit.status">
                    <option :value="status.value" v-for="status in statusOptions">
                      {{ status.label }}
                    </option>
                  </select>
                  <label>Статус</label>
                </div>
              </div>

              <div class="col-md-6">
                <div class="form-floating">
                  <select class="form-select" v-model="taskToEdit.priority">
                    <option :value="priority.value" v-for="priority in priorityOptions">
                      {{ priority.label }}
                    </option>
                  </select>
                  <label>Приоритет</label>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <input type="date" class="form-control" v-model="taskToEdit.due_date">
                  <label>Срок выполнения</label>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <textarea class="form-control" v-model="taskToEdit.description" style="height: 100px"></textarea>
                  <label>Описание</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="resetEditModal">
              Закрыть
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal"
              @click="onUpdateTask">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imageViewModal" tabindex="-1" style="display: none;">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Просмотр изображения</h5>
            <button type="button" class="btn-close" @click="closeImageViewModal"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="imageViewUrl" class="img-fluid" style="max-height: 70vh; object-fit: contain;"
              v-if="imageViewUrl">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeImageViewModal">
              Закрыть
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

.task-item {
  transition: box-shadow 0.2s;
}

.task-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.img-thumbnail {
  border: 1px solid #dee2e6;
  padding: 2px;
}

.clickable-image {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.clickable-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.position-relative {
  position: relative;
}

.image-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 10px;
  text-align: center;
  padding: 1px 2px;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 0 0 4px 4px;
}

.position-relative:hover .image-hint {
  opacity: 1;
}

#imageViewModal {
  z-index: 1060;
}

.vr {
  width: 1px;
  height: 2.5rem;
  background-color: #dee2e6;
}
</style>