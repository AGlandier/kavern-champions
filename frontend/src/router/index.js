import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '../layouts/DefaultLayout.vue'
import HomeView from '../views/HomeView.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminView from '../views/admin/AdminView.vue'

function requireAdminKey(_to, _from, next) {
  const key = localStorage.getItem('kc-admin-key')
  if (!key) next({ name: 'admin-login' })
  else next()
}

const routes = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
      },
      {
        path: 'admin/login',
        name: 'admin-login',
        component: AdminLoginView,
      },
      {
        path: 'admin',
        name: 'admin',
        component: AdminView,
        beforeEnter: requireAdminKey,
      },
      {
        path: 'admin/room/:id',
        name: 'admin-room',
        component: { template: '<div>Room manager — à venir</div>' },
        beforeEnter: requireAdminKey,
      },
    ],
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
