<!-- Comments.vue -->
<script setup>
import { ref, onBeforeMount } from 'vue';
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
const removeImageFlag = ref(false); // Флаг для удаления изображения - ДОБАВЛЕНО
const imageViewUrl = ref('');
const imageViewModal = ref(null);

async function fetchComments() {
  try {
    loading.value = true;
    const r = await axios.get("/api/comments/");
    comments.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки комментариев:', error);
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
    removeImageFlag.value = false; // Сбрасываем флаг удаления если выбрано новое изображение - ДОБАВЛЕНО
  } else {
    commentEditImageUrl.value = '';
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

async function onCommentAdd() {
  try {
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
    
    await fetchComments();
  } catch (error) {
    console.error('Ошибка добавления комментария:', error);
    alert('Ошибка при добавлении комментария');
  }
}

async function onCommentEditClick(comment) {
  commentToEdit.value = { ...comment };
  commentToEditOriginal.value = { ...comment };
  // Устанавливаем текущее изображение в предпросмотр только если оно есть - ИЗМЕНЕНО
  commentEditImageUrl.value = comment.picture || '';
  removeImageFlag.value = false; // Сбрасываем флаг удаления - ДОБАВЛЕНО
  
  if (commentEditPictureRef.value) {
    commentEditPictureRef.value.value = '';
  }
}

async function onUpdateComment() {
  try {
    const formData = new FormData();
    
    // Обработка изображения - ИЗМЕНЕНО
    if (commentEditPictureRef.value.files[0]) {
      // Загружено новое изображение
      formData.append('picture', commentEditPictureRef.value.files[0]);
    } else if (removeImageFlag.value && commentToEditOriginal.value?.picture) {
      // Пользователь хочет удалить изображение
      formData.append('picture', '');
    }
    // Если ничего не выбрано и флаг удаления не установлен - изображение не меняется
    
    formData.append('text', commentToEdit.value.text);
    formData.append('task', commentToEdit.value.task);
    
    await axios.patch(`/api/comments/${commentToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    // Очищаем - ИЗМЕНЕНО
    commentEditImageUrl.value = '';
    commentToEdit.value = {};
    commentToEditOriginal.value = null;
    removeImageFlag.value = false; // Сбрасываем флаг удаления
    
    if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';
    
    await fetchComments();
  } catch (error) {
    console.error('Ошибка обновления комментария:', error);
    alert('Ошибка при обновлении комментария');
  }
}

async function onRemoveClick(comment) {
  if (confirm('Вы уверены, что хотите удалить комментарий?')) {
    try {
      await axios.delete(`/api/comments/${comment.id}/`);
      await fetchComments();
    } catch (error) {
      console.error('Ошибка удаления комментария:', error);
      alert('Ошибка при удалении комментария');
    }
  }
}

function removeAddPicture() {
  commentAddImageUrl.value = '';
  if (commentsPictureRef.value) commentsPictureRef.value.value = '';
}

function removeEditPicture() {
  // Только очищаем загруженное изображение, не устанавливаем флаг удаления - ИЗМЕНЕНО
  commentEditImageUrl.value = '';
  if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';
}

function removeExistingImage() {
  // Устанавливаем флаг удаления и очищаем предпросмотр - ДОБАВЛЕНО
  removeImageFlag.value = true;
  commentEditImageUrl.value = '';
  if (commentEditPictureRef.value) commentEditPictureRef.value.value = '';
}

// Функция для сброса состояния при закрытии модального окна - ДОБАВЛЕНО
function resetEditModal() {
  removeEditPicture();
  removeImageFlag.value = false;
}

onBeforeMount(async () => {
  await Promise.all([fetchComments(), fetchTasks()]);
});
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Комментарии</h2>
      
      <!-- Форма добавления -->
      <form @submit.prevent.stop="onCommentAdd" class="mb-4">
        <div class="row g-2 align-items-end">
          <div class="col-auto">
            <div class="form-floating">
              <select class="form-select" v-model="commentToAdd.task" required>
                <option :value="task.id" v-for="task in tasks" :key="task.id">
                  {{ task.title }}
                </option>
              </select>
              <label>Задача</label>
            </div>
          </div>
          
          <div class="col-auto">
            <div class="input-group">
              <input class="form-control" type="file" ref="commentsPictureRef" 
                     @change="commentsAddPictureChange" accept="image/*">
              <button v-if="commentAddImageUrl" type="button" 
                      class="btn btn-outline-secondary" @click="removeAddPicture"
                      title="Удалить изображение">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
          
          <div class="col-auto">
            <div v-if="commentAddImageUrl" class="position-relative">
              <img :src="commentAddImageUrl" style="max-height: 60px;" 
                   class="img-thumbnail clickable-image" alt=""
                   @click="openImageViewModal(commentAddImageUrl)"
                   title="Нажмите для увеличения">
              <div class="image-hint">Нажмите</div>
            </div>
          </div>
          
          <div class="col-auto">
            <div class="form-floating">
              <textarea class="form-control" v-model="commentToAdd.text" required 
                        placeholder="Текст комментария" style="height: 60px"></textarea>
              <label>Текст комментария</label>
            </div>
          </div>
          
          <div class="col-auto">
            <button class="btn btn-primary h-100 w-100">Добавить комментарий</button>
          </div>
        </div>
      </form>

      <!-- Список комментариев -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else>
        <div v-for="comment in comments" :key="comment.id" class="comment-item card mb-2">
          <div class="card-body">
            <div class="row align-items-center">
              <!-- Изображение комментария -->
              <div class="col-auto">
                <div v-if="comment.picture" class="position-relative">
                  <img :src="comment.picture" style="max-height: 200px; max-width: 60px;" 
                       class="img-thumbnail clickable-image" alt="Изображение"
                       @click="openImageViewModal(comment.picture)"
                       title="Нажмите для увеличения">
                  <div class="image-hint">Нажмите</div>
                </div>
              </div>
              
              <div class="col-auto">
                <strong>Задача {{ comment.task_title }}</strong>
                <p class="card-text mb-1">{{ comment.text }}</p>
                <small class="text-muted">
                  {{ new Date(comment.created_at).toLocaleString() }}
                </small>
              </div>
              
              <!-- Кнопки действий -->
              <div class="col-auto text-end">
                <button type="button" class="btn btn-success btn-sm" 
                        @click="onCommentEditClick(comment)" 
                        data-bs-toggle="modal" 
                        data-bs-target="#editCommentModal">
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
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editCommentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать комментарий</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
                    @click="resetEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <!-- Текущее изображение с кнопкой удаления - ИЗМЕНЕНО -->
              <div class="col-12" v-if="commentToEdit.picture && !removeImageFlag">
                <div class="text-center mb-3">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <p class="text-muted mb-0">Текущее изображение:</p>
                    <button type="button" class="btn btn-outline-danger btn-sm" 
                            @click="removeExistingImage"
                            title="Удалить изображение">
                      <i class="bi bi-trash"></i> Удалить
                    </button>
                  </div>
                  <div class="position-relative d-inline-block">
                    <img :src="commentToEdit.picture" style="max-height: 100px;" 
                         class="img-thumbnail clickable-image" alt="Текущее изображение"
                         @click="openImageViewModal(commentToEdit.picture)"
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
                    <input class="form-control" type="file" ref="commentEditPictureRef" 
                           @change="commentsEditPictureChange" accept="image/*">
                    <button v-if="commentEditImageUrl" type="button" 
                            class="btn btn-outline-secondary" @click="removeEditPicture">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
                
                <!-- Показываем только если выбрано новое изображение - ИЗМЕНЕНО -->
                <div class="text-center mb-3" v-if="commentEditImageUrl && commentEditPictureRef?.files?.length">
                  <p class="text-muted mb-1">Предпросмотр нового изображения:</p>
                  <div class="position-relative d-inline-block">
                    <img :src="commentEditImageUrl" style="max-height: 100px;" 
                         class="img-thumbnail clickable-image" alt="Новое изображение"
                         @click="openImageViewModal(commentEditImageUrl)"
                         title="Нажмите для увеличения">
                    <div class="image-hint">Нажмите</div>
                  </div>
                </div>
              </div>
              
              <!-- Текст комментария -->
              <div class="col-12">
                <div class="form-floating">
                  <textarea class="form-control" v-model="commentToEdit.text" 
                            style="height: 100px" required></textarea>
                  <label>Текст комментария</label>
                </div>
              </div>
              
              <!-- Задача -->
              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" v-model="commentToEdit.task" required>
                    <option :value="task.id" v-for="task in tasks" :key="task.id">
                      {{ task.title }}
                    </option>
                  </select>
                  <label>Задача</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"
                    @click="resetEditModal">
              Закрыть
            </button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" 
                    @click="onUpdateComment">
              Сохранить
            </button>
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
            <img :src="imageViewUrl" class="img-fluid" 
                 style="max-height: 70vh; object-fit: contain;"
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