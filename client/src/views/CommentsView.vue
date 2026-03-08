<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const comments = ref([]);
const tasks = ref([]);
const commentToAdd = ref({});
const commentToEdit = ref({});
const commentsPictureRef = ref(null);
const commentAddImageUrl = ref('');
const commentEditPictureRef = ref(null);
const commentEditImageUrl = ref('');
const commentToEditOriginal = ref(null);
const removeImageFlag = ref(false);
const imageViewUrl = ref('');
const imageViewModal = ref(null);
const stats = ref(null);

const filters = ref({
  text: '',
  task: ''
});

const filteredComments = computed(() => {
  return comments.value.filter(comment => {
    const matchesText = comment.text.toLowerCase().includes(filters.value.text.toLowerCase());
    const matchesTask = !filters.value.task || comment.task === parseInt(filters.value.task);
    return matchesText && matchesTask;
  });
});

function resetFilters() {
  filters.value = {
    text: '',
    task: ''
  };
}

async function fetchComments() {
  loading.value = true;
  const r = await axios.get("/api/comments/");
  comments.value = r.data;
  loading.value = false;
}

async function fetchTasks() {
  const r = await axios.get("/api/tasks/");
  tasks.value = r.data;
}

async function fetchStats() {
  const r = await axios.get("/api/comments/stats/");
  stats.value = r.data;
}

function commentsAddPictureChange() {
  if (commentsPictureRef.value.files[0]) {
    commentAddImageUrl.value = URL.createObjectURL(commentsPictureRef.value.files[0]);
  } else {
    commentAddImageUrl.value = '';
  }
}

function commentsEditPictureChange() {
  if (commentEditPictureRef.value.files[0]) {
    commentEditImageUrl.value = URL.createObjectURL(commentEditPictureRef.value.files[0]);
    removeImageFlag.value = false;
  } else {
    commentEditImageUrl.value = '';
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

async function onCommentAdd() {
  const formData = new FormData();

  if (commentsPictureRef.value.files[0]) {
    formData.append('picture', commentsPictureRef.value.files[0]);
  }

  for (const key in commentToAdd.value) {
    if (commentToAdd.value[key] !== undefined && commentToAdd.value[key] !== null) {
      formData.append(key, commentToAdd.value[key]);
    }
  }

  await axios.post("/api/comments/", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  commentToAdd.value = {};
  commentAddImageUrl.value = '';
  if (commentsPictureRef.value) commentsPictureRef.value.value = '';

  await Promise.all([fetchComments(), fetchStats()]);
}

async function onCommentEditClick(comment) {
  commentToEdit.value = { ...comment };
  commentToEditOriginal.value = { ...comment };
  commentEditImageUrl.value = comment.picture || '';
  removeImageFlag.value = false;

  if (commentEditPictureRef.value) {
    commentEditPictureRef.value.value = '';
  }
}

async function onUpdateComment() {
  const formData = new FormData();

  if (commentEditPictureRef.value.files[0]) {
    formData.append('picture', commentEditPictureRef.value.files[0]);
  } else if (removeImageFlag.value && commentToEditOriginal.value?.picture) {
    formData.append('picture', '');
  }

  formData.append('text', commentToEdit.value.text);
  formData.append('task', commentToEdit.value.task);

  await axios.patch(`/api/comments/${commentToEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  commentEditImageUrl.value = '';
  commentToEdit.value = {};
  commentToEditOriginal.value = null;
  removeImageFlag.value = false;

  if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';

  await Promise.all([fetchComments(), fetchStats()]);
}

async function onRemoveClick(comment) {
  if (confirm('Вы уверены, что хотите удалить комментарий?')) {
    await axios.delete(`/api/comments/${comment.id}/`);
    await Promise.all([fetchComments(), fetchStats()]);
  }
}

function removeAddPicture() {
  commentAddImageUrl.value = '';
  if (commentsPictureRef.value) commentsPictureRef.value.value = '';
}

function removeEditPicture() {
  commentEditImageUrl.value = '';
  if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';
}

function removeExistingImage() {
  removeImageFlag.value = true;
  commentEditImageUrl.value = '';
  if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';
}

function resetEditModal() {
  removeEditPicture();
  removeImageFlag.value = false;
}

onBeforeMount(async () => {
  await Promise.all([fetchComments(), fetchTasks(), fetchStats()]);
});
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Комментарии</h2>

      <form @submit.prevent.stop="onCommentAdd" class="mb-4">
        <div class="row g-2 align-items-end">
          <div class="col-12">
            <div class="form-floating">
              <select class="form-select" id="add-comment-task" v-model="commentToAdd.task" required>
                <option :value="task.id" v-for="task in tasks" :key="task.id">
                  {{ task.title }}
                </option>
              </select>
              <label for="add-comment-task">Задача</label>
            </div>
          </div>

          <div class="col-12">
            <div class="input-group">
              <input class="form-control" type="file" id="add-comment-picture" ref="commentsPictureRef"
                @change="commentsAddPictureChange" accept="image/*">
              <label class="input-group-text" for="add-comment-picture">Выбрать файл</label>
              <button v-if="commentAddImageUrl" type="button" class="btn btn-outline-secondary"
                @click="removeAddPicture" title="Удалить изображение" aria-label="Удалить изображение">
                <i class="bi bi-x" aria-hidden="true"></i>
              </button>
            </div>
          </div>

          <div class="col-12">
            <div v-if="commentAddImageUrl" class="position-relative">
              <img :src="commentAddImageUrl" style="max-height: 60px;" class="img-thumbnail clickable-image"
                alt="Предпросмотр изображения" @click="openImageViewModal(commentAddImageUrl)"
                title="Нажмите для увеличения" role="button" tabindex="0"
                @keydown.enter="openImageViewModal(commentAddImageUrl)">
              <div class="image-hint">Нажмите для увеличения</div>
            </div>
          </div>

          <div class="col-12">
            <div class="form-floating">
              <textarea class="form-control" id="add-comment-text" v-model="commentToAdd.text" required
                placeholder="Текст комментария" style="height: 60px"></textarea>
              <label for="add-comment-text">Текст комментария</label>
            </div>
          </div>

          <div class="col-12">
            <button class="btn btn-primary h-100 w-100" type="submit">Добавить комментарий</button>
          </div>
        </div>
      </form>

      <div class="filters-panel mb-4">
        <h5>Фильтры</h5>
        <div class="row g-3">
          <div class="col-md-5">
            <div class="form-floating">
              <input type="text" class="form-control" id="filterText" v-model="filters.text"
                placeholder="Введите текст">
              <label for="filterText">По тексту комментария</label>
            </div>
          </div>
          <div class="col-md-5">
            <div class="form-floating">
              <select class="form-select" id="filterTask" v-model="filters.task">
                <option value="">Все задачи</option>
                <option :value="task.id" v-for="task in tasks" :key="task.id">{{ task.title }}</option>
              </select>
              <label for="filterTask">По задаче</label>
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-center">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters" type="button">
              <i class="bi bi-x-circle" aria-hidden="true"></i> Сбросить
            </button>
          </div>
        </div>

        <div class="filter-info mt-2 text-muted small" aria-live="polite" aria-atomic="true">
          Показано: <b>{{ filteredComments.length }}</b> из <b>{{ comments.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small" aria-live="polite">
        Всего комментариев: <strong>{{ stats.count }}</strong>
      </div>

      <div v-if="loading" class="text-center" role="status" aria-live="polite">
        <div class="spinner-border" aria-hidden="true">
          <span class="visually-hidden">Загрузка комментариев...</span>
        </div>
      </div>

      <div v-else>
        <div v-if="filteredComments.length === 0" class="alert alert-info" role="status">
          Комментарии не найдены
        </div>

        <div v-for="comment in filteredComments" :key="comment.id" class="comment-item card mb-2">
          <div class="card-body row align-items-center">
            <!-- Картинка комментария -->
            <div class="col-auto" v-if="comment.picture">
              <img :src="comment.picture" class="img-thumbnail" style="max-width: 60px; max-height: 60px;"
                alt="Изображение к комментарию" @click="openImageViewModal(comment.picture)">
            </div>

            <!-- Текст и автор -->
            <div class="col">
              <p class="card-text mb-1">{{ comment.text }}</p>
              <small class="text-muted d-block">Автор: {{ comment.user_name || 'Неизвестный автор' }}</small>
              <small class="text-muted d-block">Задача: {{ comment.task_title }}</small>
              <small class="text-muted d-block">Создан: {{ new Date(comment.created_at).toLocaleString() }}</small>
            </div>

            <!-- Кнопки редактирования/удаления -->
            <div class="col-auto text-end">
              <button type="button" class="btn btn-success btn-sm" @click="onCommentEditClick(comment)"
                data-bs-toggle="modal" data-bs-target="#editCommentModal">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-danger btn-sm ms-1" @click="onRemoveClick(comment)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editCommentModal" tabindex="-1" aria-labelledby="editCommentModalTitle"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editCommentModalTitle">Редактировать комментарий</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetEditModal"
              aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">

              <div class="col-12" v-if="commentToEdit.picture && !removeImageFlag">
                <div class="text-center mb-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <p class="text-muted mb-0" id="current-image-label">Текущее изображение:</p>
                    <button type="button" class="btn btn-outline-danger btn-sm" @click="removeExistingImage"
                      aria-describedby="current-image-label">
                      <i class="bi bi-trash" aria-hidden="true"></i> Удалить
                    </button>
                  </div>
                  <div class="position-relative d-inline-block">
                    <img :src="commentToEdit.picture" style="max-height: 100px;" class="img-thumbnail clickable-image"
                      alt="Текущее изображение" @click="openImageViewModal(commentToEdit.picture)"
                      title="Нажмите для увеличения" role="button" tabindex="0"
                      @keydown.enter="openImageViewModal(commentToEdit.picture)">
                    <div class="image-hint">Нажмите для увеличения</div>
                  </div>
                  <div v-if="removeImageFlag" class="alert alert-warning mt-2 small" role="alert">
                    Изображение будет удалено при сохранении
                  </div>
                </div>
              </div>

              <div class="col-12">
                <div class="mb-3">
                  <label for="edit-comment-picture" class="form-label">Новое изображение</label>
                  <div class="input-group">
                    <input class="form-control" type="file" id="edit-comment-picture" ref="commentEditPictureRef"
                      @change="commentsEditPictureChange" accept="image/*" aria-describedby="edit-picture-help">
                    <button v-if="commentEditImageUrl" type="button" class="btn btn-outline-secondary"
                      @click="removeEditPicture" aria-label="Удалить выбранное изображение">
                      <i class="bi bi-x" aria-hidden="true"></i>
                    </button>
                  </div>
                  <div id="edit-picture-help" class="form-text">Оставьте пустым, чтобы оставить текущее изображение
                  </div>
                </div>

                <div class="text-center mb-3" v-if="commentEditImageUrl && commentEditPictureRef?.files?.length">
                  <p class="text-muted mb-1">Предпросмотр нового изображения:</p>
                  <div class="position-relative d-inline-block">
                    <img :src="commentEditImageUrl" style="max-height: 100px;" class="img-thumbnail clickable-image"
                      alt="Предпросмотр нового изображения" @click="openImageViewModal(commentEditImageUrl)"
                      title="Нажмите для увеличения" role="button" tabindex="0"
                      @keydown.enter="openImageViewModal(commentEditImageUrl)">
                    <div class="image-hint">Нажмите для увеличения</div>
                  </div>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <textarea class="form-control" id="edit-comment-text" v-model="commentToEdit.text"
                    style="height: 100px" required></textarea>
                  <label for="edit-comment-text">Текст комментария</label>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" id="edit-comment-task" v-model="commentToEdit.task" required>
                    <option :value="task.id" v-for="task in tasks" :key="task.id">
                      {{ task.title }}
                    </option>
                  </select>
                  <label for="edit-comment-task">Задача</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="resetEditModal">
              Закрыть
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateComment">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imageViewModal" tabindex="-1" style="display: none;"
      aria-labelledby="imageViewModalTitle" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="imageViewModalTitle">Просмотр изображения</h5>
            <button type="button" class="btn-close" @click="closeImageViewModal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="imageViewUrl" class="img-fluid" style="max-height: 70vh; object-fit: contain;"
              v-if="imageViewUrl" :alt="'Увеличенное изображение'">

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

.comment-item {
  transition: box-shadow 0.2s;
}

.comment-item:hover {
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
</style>