<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';

const loading = ref(false);
const columns = ref([]);
const projects = ref([]);
const ColumnToAdd = ref({});
const ColumnToEdit = ref({});

const projectsByID = computed(() => {
  return _.keyBy(projects.value, x => x.id)
})

async function fetchProjects() {
  const r = await axios.get("/api/projects/");
  console.log(r.data)
  projects.value = r.data;
}

async function fetchColumns() {
  loading.value = true;
  const r = await axios.get("/api/columns/");
  console.log(r.data)
  columns.value = r.data;
  loading.value = false;
}

async function onColumnEditClick(column) {
  ColumnToEdit.value = { ...column };
}

async function onUpdateColumn() {
  await axios.put(`/api/columns/${ColumnToEdit.value.id}/`, {
    ...ColumnToEdit.value
  });
  await fetchColumns();
}

async function onColumnAdd() {
  await axios.post("/api/columns/", {
    ...ColumnToAdd.value,
  });
  await fetchColumns();
}

async function onRemoveClick(column) {
  await axios.delete(`/api/columns/${column.id}/`);
  await fetchColumns();
}

onBeforeMount(async () => {
  await fetchColumns();
  await fetchProjects();
})
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <!-- Форма добавления -->
      <form @submit.prevent.stop="onColumnAdd">
        <div class="row">
          <div class="col">
            <div class="form-floating">
              <input 
                type="text" 
                class="form-control" 
                id="addColumnName"
                v-model="ColumnToAdd.name" 
                required
              >
              <label for="addColumnName">Название</label>
            </div>
          </div>
          <div class="col-auto">
            <div class="form-floating">
              <select 
                class="form-select" 
                id="addColumnProject"
                v-model="ColumnToAdd.project" 
                required
              >
                <option :value="p.id" v-for="p in projects">{{ p.name }}</option>
              </select>
              <label for="addColumnProject">Проект</label>
            </div>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary">Добавить</button>
          </div>
        </div>
      </form>

      <!-- Список колонок -->
      <div>
        <div v-for="item in columns" class="column-item">
          <div>{{ item.name }}</div>
          <div>{{ projectsByID[item.project]?.name }}</div>
          <button 
            type="button" 
            class="btn btn-success" 
            @click="onColumnEditClick(item)" 
            data-bs-toggle="modal"
            data-bs-target="#editColumnModal"
          >
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-danger" @click="onRemoveClick(item)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editColumnModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать колонку</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col">
                <div class="form-floating">
                  <input 
                    type="text" 
                    class="form-control" 
                    id="editColumnName"
                    v-model="ColumnToEdit.name"
                  >
                  <label for="editColumnName">Название</label>
                </div>
              </div>
              <div class="col-auto">
                <div class="form-floating">
                  <select 
                    class="form-select" 
                    id="editColumnProject"
                    v-model="ColumnToEdit.project"
                  >
                    <option :value="p.id" v-for="p in projects">{{ p.name }}</option>
                  </select>
                  <label for="editColumnProject">Проект</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              data-bs-dismiss="modal"
              @click="onUpdateColumn"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.column-item {
  padding: 0.5rem;
  border: 1px solid silver;
  border-radius: 8px;
  margin: 0.5rem 0;
  display: grid;
  grid-template-columns: 1fr 1fr auto auto auto;
  gap: 16px;
  justify-content: space-between;
  align-content: center;
  align-items: center;
}
</style>