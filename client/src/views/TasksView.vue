<!-- Tasks.vue -->
<script setup>
import { ref, onBeforeMount } from 'vue';
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
const removeImageFlag = ref(false); // Флаг для удаления изображения
const imageViewUrl = ref('');
const imageViewModal = ref(null);
const stats = ref(null); // Добавляем статистику

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

// Обработчики для изображений
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
    removeImageFlag.value = false; // Сбрасываем флаг удаления если выбрано новое изображение
  } else {
    taskEditImageUrl.value = '';
  }
}

// Открытие модального окна с изображением
function openImageViewModal(imageUrl) {
  imageViewUrl.value = imageUrl;

  const modalElement = document.getElementById('imageViewModal');
  if (modalElement) {
    modalElement.style.display = 'block';
    modalElement.classList.add('show');

    // Добавляем backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    backdrop.id = 'imageViewModalBackdrop';
    document.body.appendChild(backdrop);

    // Обработчик закрытия по клику на backdrop
    backdrop.onclick = closeImageViewModal;

    // Обработчик клавиши ESC
    const handleEsc = (e) => e.key === 'Escape' && closeImageViewModal();
    document.addEventListener('keydown', handleEsc);

    // Сохраняем обработчики для очистки
    imageViewModal.value = { handleEsc };
  }
}

// Закрытие модального окна с изображением
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

    // Очищаем форму
    taskToAdd.value = {};
    taskAddImageUrl.value = '';
    if (taskAddPictureRef.value) taskAddPictureRef.value.value = '';

    await Promise.all([fetchTasks(), fetchStats()]); // Обновляем и задачи и статистику
  } catch (error) {
    console.error('Ошибка добавления задачи:', error);
    alert('Ошибка при добавлении задачи');
  }
}

async function onTaskEditClick(task) {
  taskToEdit.value = { ...task };
  taskToEditOriginal.value = { ...task };
  // Устанавливаем текущее изображение в предпросмотр только если оно есть
  taskEditImageUrl.value = task.picture || '';
  removeImageFlag.value = false; // Сбрасываем флаг удаления

  if (taskEditPictureRef.value) {
    taskEditPictureRef.value.value = '';
  }
}

async function onUpdateTask() {
  try {
    const formData = new FormData();

    // Обработка изображения
    if (taskEditPictureRef.value.files[0]) {
      // Загружено новое изображение
      formData.append('picture', taskEditPictureRef.value.files[0]);
    } else if (removeImageFlag.value && taskToEditOriginal.value?.picture) {
      // Пользователь хочет удалить изображение
      formData.append('picture', '');
    }
    // Если ничего не выбрано и флаг удаления не установлен - изображение не меняется

    // Добавляем остальные поля
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

    // Очищаем
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
      await Promise.all([fetchTasks(), fetchStats()]); // Обновляем и задачи и статистику
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
  // Только очищаем загруженное изображение, не устанавливаем флаг удаления
  taskEditImageUrl.value = '';
  if (taskEditPictureRef.value) taskEditPictureRef.value.value = '';
}

function removeExistingImage() {
  // Устанавливаем флаг удаления и очищаем предпросмотр
  removeImageFlag.value = true;
  taskEditImageUrl.value = '';
  if (taskEditPictureRef.value) taskEditPictureRef.value.value = '';
}

// Функция для сброса состояния при закрытии модального окна
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

      <!-- Форма добавления -->
      <form @submit.prevent.stop="onTaskAdd" class="mb-4">
        <div class="row g-2 align-items-end">
          <!-- Поля задачи -->
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

          <!-- Загрузка изображения -->
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

          <!-- Предпросмотр изображения -->
          <div class="col-auto">
            <div v-if="taskAddImageUrl" class="position-relative">
              <img :src="taskAddImageUrl" style="max-height: 60px;" class="img-thumbnail clickable-image" alt=""
                @click="openImageViewModal(taskAddImageUrl)" title="Нажмите для увеличения">
              <div class="image-hint">Нажмите</div>
            </div>
          </div>

          <!-- Описание -->
          <div class="col-md-12 mt-2">
            <div class="form-floating">
              <textarea class="form-control" v-model="taskToAdd.description" placeholder="Описание задачи"
                style="height: 60px"></textarea>
              <label>Описание задачи</label>
            </div>
          </div>

          <!-- Кнопка добавления -->
          <div class="col-md-12 mt-2">
            <button class="btn btn-primary">Добавить задачу</button>
          </div>
        </div>
      </form>

      <!-- Статистика -->
      <div v-if="stats" class="mb-3 text-muted small">
        Всего задач: <strong>{{ stats.count }}</strong>
      </div>


      <!-- Список задач -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <div v-else>
        <div v-for="task in tasks" :key="task.id" class="task-item card mb-2">
          <div class="card-body">
            <div class="row align-items-center">
              <!-- Изображение задачи -->
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

              <!-- Информация о задаче -->
              <div class="col-md-3">
                <h6 class="card-title">{{ task.title }}</h6>
                <p class="card-text mb-1">{{ task.description }}</p>
                <small class="text-muted">{{ task.column_name }}</small>
              </div>

              <!-- Статус и приоритет -->
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

              <!-- Даты -->
              <div class="col-md-2">
                <small class="text-muted">
                  Срок: {{ task.due_date ? new Date(task.due_date).toLocaleDateString() : 'Не указан' }}
                </small>
                <br>
                <small class="text-muted">
                  Создана: {{ new Date(task.created_at).toLocaleDateString() }}
                </small>
              </div>

              <!-- Кнопки действий -->
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

    <!-- Модальное окно редактирования задачи -->
    <div class="modal fade" id="editTaskModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать задачу</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <!-- Текущее изображение с кнопкой удаления -->
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

              <!-- Загрузка нового изображения -->
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

                <!-- Показываем только если выбрано новое изображение -->
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

              <!-- Поля задачи -->
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

    <!-- Модальное окно для просмотра изображения -->
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

<style scoped>
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

/* Стили для блока статистики */
.vr {
  width: 1px;
  height: 2.5rem;
  background-color: #dee2e6;
}
</style>