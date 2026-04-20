import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '../layouts/DefaultLayout.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ManagerView from '../views/ManagerView.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminView from '../views/admin/AdminView.vue'
import BattleRoomManagerView from '../views/admin/BattleRoomManagerView.vue'

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
        path: 'login',
        name: 'login',
        component: LoginView,
      },
      {
        path: 'manager',
        name: 'manager',
        component: ManagerView,
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
        path: 'admin/battleroom',
        name: 'admin-room',
        component: BattleRoomManagerView,
        beforeEnter: requireAdminKey,
      },
    ],
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
