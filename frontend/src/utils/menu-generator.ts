import type { RouteRecordRaw } from 'vue-router'
import type { RouteMeta } from '@/types'

/**
 * 菜单项接口
 */
export interface MenuItemFromRoute {
  key: string
  name: string
  path: string
  icon?: string
  order: number
}

/**
 * 从路由配置生成菜单数据
 */
export const generateMenuFromRoutes = (routes: RouteRecordRaw[]): MenuItemFromRoute[] => {
  const menuItems: MenuItemFromRoute[] = []

  // 查找根路由的子路由
  const rootRoute = routes.find(route => route.path === '/' && !route.name)

  if (rootRoute?.children) {
    rootRoute.children
      .filter(child => child.meta?.menuKey && child.path !== '') // 过滤掉重定向路由
      .forEach(child => {
        const meta = child.meta as RouteMeta
        if (meta.menuKey) {
          menuItems.push({
            key: meta.menuKey,
            name: getMenuDisplayName(meta.menuKey),
            path: `/${child.path}`, // 确保路径以 / 开头
            icon: meta.icon,
            order: meta.menuOrder || 999
          })
        }
      })
  }

  // 按照order排序
  return menuItems.sort((a, b) => a.order - b.order)
}

/**
 * 根据菜单键获取显示名称
 */
const getMenuDisplayName = (key: string): string => {
  const nameMap: Record<string, string> = {
    training: '历练',
    keyboard: '键盘映射',
    macro: '自定义宏',
    fishing: '钓鱼',
    about: '关于'
  }

  return nameMap[key] || key
}

/**
 * 根据当前路径获取对应的菜单键
 */
export const getMenuKeyFromPath = (path: string, menuItems: MenuItemFromRoute[]): string => {
  const menuItem = menuItems.find(item => item.path === path)
  return menuItem?.key || ''
}

/**
 * 根据菜单键获取对应的路径
 */
export const getPathFromMenuKey = (menuKey: string, menuItems: MenuItemFromRoute[]): string => {
  const menuItem = menuItems.find(item => item.key === menuKey)
  return menuItem?.path || '/training'
}