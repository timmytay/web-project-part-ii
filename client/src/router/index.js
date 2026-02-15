import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import ProjectsView from '@/views/ProjectsView.vue'
import ColumnsView from '@/views/ColumnsView.vue'
import TasksView from '@/views/TasksView.vue'
import CommentsView from '@/views/CommentsView.vue'
import TimeTrackingView from '@/views/TimeTrackingView.vue'
import UsersView from '@/views/UsersView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/columns",
      name: "ColumnsView",
      component: ColumnsView
    },
    {
      path: "/",
      name: "ProjectsView",
      component: ProjectsView
    },
    
    {
      path: "/login",
      name: "LoginView",
      component: LoginView
    },
    {
      path: "/tasks",
      name: "TasksView", 
      component: TasksView
    },
    {
      path: "/comments",
      name: "CommentsView",
      component: CommentsView
    },
    {
      path: "/time-tracking",
      name: "TimeTrackingView",
      component: TimeTrackingView
    },
    {
      path: "/users",
      name: "UsersView",
      component: UsersView,
      props: route => ({ role: route.query.role || "" }),
    },
  ],
})

router.beforeEach(async (to, from) => {
  const authStore = useAuthStore();
  
  if (!authStore.userInfo || Object.keys(authStore.userInfo).length === 0) {
    await authStore.fetchUserInfo();
  }
  
  if (!authStore.is_authenticated && to.name !== 'LoginView') {
    return { name: 'LoginView' };
  }
  
  if (authStore.is_authenticated && to.name == 'LoginView') {
    return { name: 'ProjectsView' };
  }
})

export default router