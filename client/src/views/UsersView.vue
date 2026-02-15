<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import axios from 'axios';

const loading = ref(false);
const users = ref([]);
const UserToAdd = ref({});
const UserToEdit = ref({});
const error = ref(null);
const successMessage = ref('');
const stats = ref(null);

// Фильтры
const filters = ref({
  username: '',
  name: '',
  email: '',
  type: ''
});

const userTypes = [
  { value: 'admin', label: 'Администратор' },
  { value: 'manager', label: 'Менеджер проекта' },
  { value: 'developer', label: 'Разработчик' },
  { value: 'viewer', label: 'Наблюдатель' }
];

// Отфильтрованные пользователи
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    // Фильтр по имени пользователя
    const matchesUsername = user.username?.toLowerCase().includes(filters.value.username.toLowerCase()) ?? true;
    
    // Фильтр по полному имени
    const matchesName = user.name?.toLowerCase().includes(filters.value.name.toLowerCase()) ?? true;
    
    // Фильтр по email
    const matchesEmail = user.email?.toLowerCase().includes(filters.value.email.toLowerCase()) ?? true;
    
    // Фильтр по типу пользователя
    const matchesType = !filters.value.type || user.type === filters.value.type;
    
    return matchesUsername && matchesName && matchesEmail && matchesType;
  });
});

// Сброс фильтров
function resetFilters() {
  filters.value = {
    username: '',
    name: '',
    email: '',
    type: ''
  };
}

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

async function fetchUsers() {
  loading.value = true;
  error.value = null;
  try {
    const r = await api.get("/users/");
    users.value = r.data;
  } catch (err) {
    handleError(err, 'загрузки пользователей');
  } finally {
    loading.value = false;
  }
}

async function fetchStats() {
  try {
    const r = await api.get("/users/stats/");
    stats.value = r.data;
  } catch (error) {
    console.error('Ошибка загрузки статистики пользователей:', error);
  }
}

async function onUserEditClick(user) {
  error.value = null;
  UserToEdit.value = {
    ...user,
    username: user.username || '',
    email: user.email || '',
    name: user.name || '',
    birthday: user.birthday || null,
    type: user.type || ''
  };
}

async function onUpdateUser() {
  error.value = null;
  try {
    const updateData = {
      username: UserToEdit.value.username,
      email: UserToEdit.value.email || '',
      name: UserToEdit.value.name,
      birthday: UserToEdit.value.birthday,
      type: UserToEdit.value.type
    };

    if (UserToEdit.value.new_password) {
      updateData.password = UserToEdit.value.new_password;
    }

    await api.put(`/users/${UserToEdit.value.id}/`, updateData);
    successMessage.value = 'Пользователь успешно обновлен';
    await Promise.all([fetchUsers(), fetchStats()]);

    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (err) {
    handleError(err, 'обновления пользователя');
  }
}

async function onUserAdd() {
  error.value = null;
  try {
    const userData = {
      username: UserToAdd.value.username,
      password: UserToAdd.value.password,
      email: UserToAdd.value.email || '',
      name: UserToAdd.value.name,
      birthday: UserToAdd.value.birthday,
      type: UserToAdd.value.type
    };

    await api.post("/users/", userData);
    successMessage.value = 'Пользователь успешно создан';
    await Promise.all([fetchUsers(), fetchStats()]);

    UserToAdd.value = {};

    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (err) {
    handleError(err, 'создания пользователя');
  }
}

async function onRemoveClick(user) {
  if (!confirm(`Удалить пользователя ${user.username || user.id}?`)) {
    return;
  }

  error.value = null;
  try {
    await api.delete(`/users/${user.id}/`);
    successMessage.value = 'Пользователь успешно удален';
    await Promise.all([fetchUsers(), fetchStats()]);

    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (err) {
    handleError(err, 'удаления пользователя');
  }
}

function handleError(err, context) {
  console.error(`Ошибка ${context}:`, err);

  if (err.response) {
    const status = err.response.status;
    const data = err.response.data;

    if (status === 400) {
      if (typeof data === 'object' && data !== null) {
        const errors = [];
        for (const [field, messages] of Object.entries(data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`);
          } else {
            errors.push(`${field}: ${messages}`);
          }
        }
        error.value = `Ошибка валидации: ${errors.join('; ')}`;
      } else if (typeof data === 'string') {
        if (data.includes('<!DOCTYPE html>')) {
          error.value = 'Сервер вернул HTML вместо JSON. Проверьте авторизацию или права доступа.';
        } else {
          error.value = data;
        }
      } else {
        error.value = `Ошибка ${status}: ${JSON.stringify(data)}`;
      }
    } else if (status === 403) {
      error.value = 'Доступ запрещен. У вас нет прав для выполнения этой операции.';
    } else if (status === 401) {
      error.value = 'Требуется авторизация. Пожалуйста, войдите в систему.';
    } else if (status === 404) {
      error.value = 'Ресурс не найден.';
    } else if (status === 500) {
      error.value = 'Внутренняя ошибка сервера.';
    } else {
      error.value = `Ошибка ${status}: ${JSON.stringify(data)}`;
    }
  } else if (err.request) {
    error.value = 'Нет ответа от сервера. Проверьте подключение к интернету.';
  } else {
    error.value = `Ошибка: ${err.message}`;
  }
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU');
}

function getUserTypeLabel(type) {
  const found = userTypes.find(t => t.value === type);
  return found ? found.label : type;
}

onBeforeMount(async () => {
  await Promise.all([fetchUsers(), fetchStats()]);
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h2>Пользователи</h2>
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        <strong>Ошибка!</strong> {{ error }}
        <button type="button" class="btn-close" @click="error = null"></button>
      </div>

      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        <strong>Успех!</strong> {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>

      <div v-if="error && error.includes('HTML')" class="alert alert-warning">
        <small>
          <strong>Отладка:</strong> Если вы видите эту ошибку, возможно:
          <ul class="mb-0">
            <li>Вы не авторизованы в системе</li>
            <li>У вас нет прав доступа к API пользователей</li>
            <li>Сервер настроен неправильно</li>
          </ul>
        </small>
      </div>

      <form @submit.prevent.stop="onUserAdd">
        <div class="row g-2 mb-3">
          <div class="col-md-3">
            <div class="form-floating">
              <input type="text" class="form-control" id="addUserName" v-model="UserToAdd.username" required
                placeholder="Имя пользователя">
              <label for="addUserName">Имя пользователя *</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input type="password" class="form-control" id="addUserPassword" v-model="UserToAdd.password" required
                placeholder="Пароль">
              <label for="addUserPassword">Пароль *</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input type="email" class="form-control" id="addUserEmail" v-model="UserToAdd.email" placeholder="Email">
              <label for="addUserEmail">Email</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <select class="form-select" id="addUserType" v-model="UserToAdd.type" required>
                <option value="" disabled selected>Выберите тип *</option>
                <option v-for="type in userTypes" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
              <label for="addUserType">Тип пользователя *</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <input type="text" class="form-control" id="addProfileName" v-model="UserToAdd.name"
                placeholder="Полное имя">
              <label for="addProfileName">Полное имя</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input type="date" class="form-control" id="addUserBirthday" v-model="UserToAdd.birthday"
                placeholder="Дата рождения">
              <label for="addUserBirthday">Дата рождения</label>
            </div>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary h-100 w-100">Добавить</button>
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
                id="filterUsername"
                v-model="filters.username"
                placeholder="Введите имя пользователя"
              >
              <label for="filterUsername">По имени пользователя</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterName"
                v-model="filters.name"
                placeholder="Введите полное имя"
              >
              <label for="filterName">По полному имени</label>
            </div>
          </div>
          <div class="col-md-3">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="filterEmail"
                v-model="filters.email"
                placeholder="Введите email"
              >
              <label for="filterEmail">По email</label>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="filterType"
                v-model="filters.type"
              >
                <option value="">Все типы</option>
                <option v-for="type in userTypes" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
              <label for="filterType">По типу</label>
            </div>
          </div>
          <div class="col-md-1 d-flex align-items-center">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle"></i>
            </button>
          </div>
        </div>
        
        <!-- Информация о количестве отфильтрованных записей -->
        <div class="filter-info mt-2 text-muted small">
          Показано: <b>{{ filteredUsers.length }}</b> из <b>{{ users.length }}</b>
        </div>
      </div>

      <div v-if="stats" class="mb-3 text-muted small">
        Всего пользователей: <strong>{{ stats.count }}</strong>
      </div>

      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="alert alert-info">
        Пользователи не найдены
      </div>

      <div v-else>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Имя пользователя</th>
                <th>Email</th>
                <th>Полное имя</th>
                <th>Тип</th>
                <th>Дата рождения</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <strong>{{ user.username || 'N/A' }}</strong>
                </td>
                <td>{{ user.email || '—' }}</td>
                <td>{{ user.name || '—' }}</td>
                <td>{{ getUserTypeLabel(user.type) || '—' }}</td>
                <td>{{ formatDate(user.birthday) || '—' }}</td>
                <td>
                  <button type="button" class="btn btn-success btn-sm" @click="onUserEditClick(user)"
                    data-bs-toggle="modal" data-bs-target="#editUserModal">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-danger btn-sm ms-1" @click="onRemoveClick(user)">
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editUserModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать пользователя</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <div class="form-floating">
                  <input type="text" class="form-control" id="editUserName" v-model="UserToEdit.username" required>
                  <label for="editUserName">Имя пользователя *</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating">
                  <input type="email" class="form-control" id="editUserEmail" v-model="UserToEdit.email">
                  <label for="editUserEmail">Email</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating">
                  <input type="password" class="form-control" id="editUserPassword" v-model="UserToEdit.new_password"
                    placeholder="Новый пароль">
                  <label for="editUserPassword">Новый пароль</label>
                  <div class="form-text small">Оставьте пустым, если не хотите менять пароль</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating">
                  <select class="form-select" id="editUserType" v-model="UserToEdit.type" required>
                    <option value="" disabled>Выберите тип *</option>
                    <option v-for="type in userTypes" :value="type.value">
                      {{ type.label }}
                    </option>
                  </select>
                  <label for="editUserType">Тип пользователя *</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating">
                  <input type="text" class="form-control" id="editProfileName" v-model="UserToEdit.name">
                  <label for="editProfileName">Полное имя</label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-floating">
                  <input type="date" class="form-control" id="editUserBirthday" v-model="UserToEdit.birthday">
                  <label for="editUserBirthday">Дата рождения</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateUser">
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

.alert {
  margin-bottom: 1rem;
}

.form-text {
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
</style>