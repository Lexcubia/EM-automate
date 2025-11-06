import { createRouter, createWebHashHistory, type RouteRecordRaw, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router'
import type { RouteMeta } from '@/types'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Main',
    component: () => import('@/views/MainView.vue'),
    meta: {
      title: '二重螺旋自动化工具'
    } as RouteMeta
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach(
  (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext): void => {
    // 设置页面标题
    if (to.meta.title) {
      document.title = to.meta.title
    } else {
      document.title = 'EM-Automate'
    }
    next()
  }
)

// 路由错误处理
router.onError((error: Error): void => {
  console.error('路由错误:', error)
})

export default router

// 导出路由类型，供其他组件使用
export type { RouteLocationNormalized, RouteRecordRaw }