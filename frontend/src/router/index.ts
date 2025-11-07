import { createRouter, createWebHashHistory, type RouteRecordRaw, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '二重螺旋自动化工具'
    },
    children: [
      {
        path: '',
        redirect: '/training'
      },
      {
        path: 'training',
        name: 'Training',
        component: () => import('@/components/TrainingPanel.vue'),
        meta: {
          title: '历练 - EM-Automate',
          icon: 'RocketOutlined',
          menuKey: 'training',
          menuOrder: 1
        }
      },
      {
        path: 'keyboard',
        name: 'Keyboard',
        component: () => import('@/components/KeyboardPanel.vue'),
        meta: {
          title: '键盘映射 - EM-Automate',
          icon: 'ControlOutlined',
          menuKey: 'keyboard',
          menuOrder: 2
        }
      },
      {
        path: 'macro',
        name: 'Macro',
        component: () => import('@/components/MacroPanel.vue'),
        meta: {
          title: '自定义宏 - EM-Automate',
          icon: 'FileTextOutlined',
          menuKey: 'macro',
          menuOrder: 3
        }
      },
      {
        path: 'fishing',
        name: 'Fishing',
        component: () => import('@/components/FishingPanel.vue'),
        meta: {
          title: '钓鱼 - EM-Automate',
          icon: 'ExperimentOutlined',
          menuKey: 'fishing',
          menuOrder: 4
        }
      },
      {
        path: 'about',
        name: 'About',
        component: () => import('@/components/AboutPanel.vue'),
        meta: {
          title: '关于 - EM-Automate',
          icon: 'InfoCircleOutlined',
          menuKey: 'about',
          menuOrder: 5
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach(
  (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext): void => {
    // 设置页面标题
    if (to.meta.title) {
      document.title = to.meta.title as string
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