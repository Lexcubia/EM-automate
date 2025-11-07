// 全局类型定义

// 系统信息类型
export interface SystemInfo {
  python_version: string
  platform: string
  architecture: string
  is_admin: boolean
  cpu_usage?: number
  memory_usage?: number
}

// 任务配置类型
export interface TaskConfig {
  id: string
  name: string
  type: string
  params: Record<string, any>
  priority: number
  enabled: boolean
  created_at: string
  updated_at: string
}

// 任务状态类型
export interface TaskStatus {
  id: string
  status: "pending" | "running" | "completed" | "failed" | "paused"
  progress: number
  message: string
  start_time?: string
  end_time?: string
  error?: string
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  code?: number
}

// 任务执行历史
export interface TaskHistory {
  id: string
  task_id: string
  name: string
  type: string
  status: string
  duration: number
  result: any
  created_at: string
}

// 后端配置类型
export interface BackendConfig {
  host: string
  port: number
  timeout: number
  retries: number
}

// 应用配置类型
export interface AppConfig {
  backend: BackendConfig
  theme: "light" | "dark"
  language: string
  auto_start: boolean
  minimize_to_tray: boolean
}

// 菜单项类型
export interface MenuItem {
  id: string
  name: string
  icon?: string
  description?: string
  category?: string
  enabled: boolean
  params?: Record<string, any>
}

// 任务分类类型
export interface Category {
  id: string
  name: string
  description?: string
  items: MenuItem[]
}

// 委托任务类型
export interface Mission {
  id: string
  name: string
  type: "commission" | "night_sailing" | "commission_letter"
  level: number
  description?: string
  requirements?: Record<string, any>
  rewards?: Record<string, any>
}

// 任务队列项类型
export interface QueueItem {
  id: string
  name: string
  type: string
  level?: number
  monster?: string
  priority: number
  status: TaskStatus["status"]
  progress: number
  added_at: string
  started_at?: string
  completed_at?: string
  error?: string
}

// 键盘映射类型
export interface KeyboardMapping {
  id: string
  name: string
  key: string
  action: string
  params: Record<string, any>
  enabled: boolean
}

// 宏命令类型
export interface MacroCommand {
  id: string
  name: string
  description?: string
  commands: Array<{
    type: string
    params: Record<string, any>
    delay?: number
  }>
  enabled: boolean
}

// API 错误类型
export interface ApiError extends Error {
  code?: number
  response?: {
    data?: {
      message?: string
      error?: string
    }
  }
}

// 请求配置类型
export interface RequestConfig {
  url: string
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
  data?: any
  params?: Record<string, any>
  headers?: Record<string, string>
  timeout?: number
}

// 路由元信息类型
export interface RouteMeta {
  title?: string
  icon?: string
  requiresAuth?: boolean
  keepAlive?: boolean
  menuKey?: string
  menuOrder?: number
  [key: string]: any // 允许额外的属性
}

// 组件 Props 类型通用接口
export interface BaseComponentProps {
  id?: string
  class?: string
  style?: string | Record<string, any>
}

// 事件类型
export interface ComponentEvents {
  [key: string]: any
}

// Vue 组件类型
export type VueComponent<T extends ComponentEvents = {}> = ComponentPublicInstance & T

// ==================
// 菜单配置相关类型
// ==================

// 任务等级类型
export interface MissionLevel {
  key: string
  displayName: string
}

// 任务类型
export interface Mission {
  key: string
  displayName: string
  type: string
  levels: MissionLevel[]
}

// 子分类类型
export interface SubCategory {
  key: string
  displayName: string
  missions: Mission[]
}

// 菜单区块类型
export interface MenuSection {
  displayName: string
  children: Record<string, SubCategory>
}

// 完整菜单配置类型
export interface MenuConfig {
  missionTypes: Record<string, string>
  menu: {
    commission: MenuSection
  }
}

// 重新导出常量配置（保持向后兼容）
export {
  MISSION_TYPES_CONFIG,
  MENU_STRUCTURE_CONFIG
} from '@/constants'

// 导入配置用于默认配置
import { MISSION_TYPES_CONFIG as MissionTypes, MENU_STRUCTURE_CONFIG as MenuStructure } from '@/constants'

// 默认菜单配置（用于降级）
export const DEFAULT_MENU_CONFIG: MenuConfig = {
  missionTypes: MissionTypes,
  menu: MenuStructure,
}
