<!-- Tasks.vue -->
<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const tasks = ref([]);
const columns = ref([]);
const taskToAdd = ref({});
const taskToEdit = ref({});

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

async function onTaskAdd() {
  try {
    await axios.post("/api/tasks/", taskToAdd.value);
    taskToAdd.value = {};
    await fetchTasks();
  } catch (error) {
    console.error('Ошибка добавления задачи:', error);
  }
}

async function onTaskEditClick(task) {
  taskToEdit.value = { ...task };
}

async function onUpdateTask() {
  try {
    await axios.put(`/api/tasks/${taskToEdit.value.id}/`, {
      title: taskToEdit.value.title,
      description: taskToEdit.value.description,
      column: taskToEdit.value.column,
      status: taskToEdit.value.status,
      priority: taskToEdit.value.priority,
      due_date: taskToEdit.value.due_date
    });
    await fetchTasks();
  } catch (error) {
    console.error('Ошибка обновления задачи:', error);
  }
}

async function onRemoveClick(task) {
  if (confirm('Вы уверены, что хотите удалить задачу?')) {
    try {
      await axios.delete(`/api/tasks/${task.id}/`);
      await fetchTasks();
    } catch (error) {
      console.error('Ошибка удаления задачи:', error);
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

onBeforeMount(async () => {
  await Promise.all([fetchTasks(), fetchColumns()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Задачи</h2>
      
      <!-- Форма добавления -->
      <form @submit.prevent.stop="onTaskAdd" class="mb-4">
        <div class="row g-2">
          <div class="col-md-3">
            <div class="form-floating">
              <input type="text" class="form-control" v-model="taskToAdd.title" required>
              <label>Название задачи</label>
            </div>
          </div>
          <div class="col-md-3">
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
          <div class="col-md-12">
            <div class="form-floating">
              <textarea class="form-control" v-model="taskToAdd.description" placeholder="Описание задачи" style="height: 60px"></textarea>
              <label>Описание задачи</label>
            </div>
          </div>
          <div class="col-md-12 mt-2">
            <button class="btn btn-primary">Добавить задачу</button>
          </div>
        </div>
      </form>

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
              <div class="col-md-4">
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
                <button type="button" class="btn btn-success btn-sm" 
                        @click="onTaskEditClick(task)" 
                        data-bs-toggle="modal" 
                        data-bs-target="#editTaskModal">
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
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
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
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" 
                    @click="onUpdateTask">Сохранить</button>
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
</style>