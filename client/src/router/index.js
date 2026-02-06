import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '@/views/ProjectsView.vue'
import ColumnsView from '@/views/ColumnsView.vue'
import TasksView from '@/views/TasksView.vue'
import CommentsView from '@/views/CommentsView.vue'
import TimeTrackingView from '@/views/TimeTrackingView.vue'
import UsersView from '@/views/UsersView.vue'

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

export default router