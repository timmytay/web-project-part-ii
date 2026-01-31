<!-- Comments.vue -->
<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const comments = ref([]);
const tasks = ref([]);
const commentToAdd = ref({});
const commentToEdit = ref({});

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

async function onCommentAdd() {
  try {
    await axios.post("/api/comments/", commentToAdd.value);
    commentToAdd.value = {};
    await fetchComments();
  } catch (error) {
    console.error('Ошибка добавления комментария:', error);
  }
}

async function onCommentEditClick(comment) {
  commentToEdit.value = { ...comment };
}

async function onUpdateComment() {
  try {
    await axios.put(`/api/comments/${commentToEdit.value.id}/`, {
      text: commentToEdit.value.text,
      task: commentToEdit.value.task
    });
    await fetchComments();
  } catch (error) {
    console.error('Ошибка обновления комментария:', error);
  }
}

async function onRemoveClick(comment) {
  if (confirm('Вы уверены, что хотите удалить комментарий?')) {
    try {
      await axios.delete(`/api/comments/${comment.id}/`);
      await fetchComments();
    } catch (error) {
      console.error('Ошибка удаления комментария:', error);
    }
  }
}

onBeforeMount(async () => {
  await Promise.all([fetchComments(), fetchTasks()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Комментарии</h2>
      
      <!-- Форма добавления -->
      <form @submit.prevent.stop="onCommentAdd" class="mb-4">
        <div class="row g-2 align-items-end">
          <div class="col-md-4">
            <div class="form-floating">
              <select class="form-select" v-model="commentToAdd.task" required>
                <option :value="task.id" v-for="task in tasks">{{ task.title }}</option>
              </select>
              <label>Задача</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <textarea class="form-control" v-model="commentToAdd.text" required 
                        placeholder="Текст комментария" style="height: 60px"></textarea>
              <label>Текст комментария</label>
            </div>
          </div>
          <div class="col-md-2">
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
              <div class="col-md-2">
                <small class="text-muted">К задаче: {{ comment.task_title }}</small>
              </div>
              <div class="col-md-7">
                <p class="card-text mb-1">{{ comment.text }}</p>
                <small class="text-muted">
                  {{ new Date(comment.created_at).toLocaleString() }}
                </small>
              </div>
              <div class="col-md-3 text-end">
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

    <!-- Модальное окно редактирования комментария -->
    <div class="modal fade" id="editCommentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать комментарий</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <div class="form-floating">
                  <textarea class="form-control" v-model="commentToEdit.text" 
                            style="height: 100px" required></textarea>
                  <label>Текст комментария</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" v-model="commentToEdit.task" required>
                    <option :value="task.id" v-for="task in tasks">{{ task.title }}</option>
                  </select>
                  <label>Задача</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" 
                    @click="onUpdateComment">Сохранить</button>
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
</style>