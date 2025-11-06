import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MenuConfig, Mission, SubCategory } from '@/types'
import { DEFAULT_MENU_CONFIG } from '@/types'

export const useMenuStore = defineStore('menu', () => {
  // 状态
  const loading = ref<boolean>(false)
  const config = ref<MenuConfig | null>(null)
  const error = ref<string | null>(null)

  // 计算属性
  const missionTypes = computed(() => config.value?.missionTypes || {})

  const mainMenuSections = computed(() => {
    if (!config.value?.menu) return []

    return Object.entries(config.value.menu).map(([key, section]) => ({
      key,
      displayName: section.displayName,
      ...section
    }))
  })

  const getSubCategories = computed<(mainKey: string) => SubCategory[]>(() => {
    return (mainKey: string) => {
      if (!config.value?.menu) return []

      const mainSection = (config.value.menu as any)[mainKey]
      if (!mainSection?.children) return []

      return Object.entries(mainSection.children).map(([key, subCategory]) => ({
        key,
        displayName: subCategory.displayName,
        missions: subCategory.missions
      }))
    }
  })

  const getMissionTypeDisplay = computed(() => {
    return (type: string): string => {
      return missionTypes.value[type] || type
    }
  })

  // 方法
  const loadMenuConfig = async (): Promise<void> => {
    // 如果已经加载过，直接返回
    if (config.value) {
      return
    }

    try {
      loading.value = true
      error.value = null

      // 从静态文件加载配置
      const response = await fetch('/menu_config.json')

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: MenuConfig = await response.json()

      // 验证数据格式
      if (!data.missionTypes || !data.menu?.commission) {
        throw new Error('菜单配置格式错误')
      }

      config.value = data
      console.log('菜单配置加载成功:', data)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载菜单配置失败'
      console.error('加载菜单配置失败:', err)
      error.value = errorMessage

      // 使用默认配置作为降级方案
      console.warn('使用默认菜单配置')
      config.value = DEFAULT_MENU_CONFIG

    } finally {
      loading.value = false
    }
  }

  const ensureConfigLoaded = async (): Promise<MenuConfig> => {
    if (!config.value) {
      await loadMenuConfig()
    }
    return config.value || DEFAULT_MENU_CONFIG
  }

  const ensureSubCategoriesLoaded = async (mainCategory: string): Promise<SubCategory[]> => {
    await ensureConfigLoaded()
    return getSubCategories.value(mainCategory)
  }

  const getSubCategoryByKey = computed<(mainKey: string, subKey: string) => SubCategory | undefined>(() => {
    return (mainKey: string, subKey: string) => {
      return getSubCategories.value(mainKey).find(sub => sub.key === subKey)
    }
  })

  const clearError = (): void => {
    error.value = null
  }

  const reset = (): void => {
    loading.value = false
    config.value = null
    error.value = null
  }

  // 重新加载配置（用于调试或刷新）
  const reloadConfig = async (): Promise<void> => {
    config.value = null
    await loadMenuConfig()
  }

  return {
    // 状态
    loading,
    config,
    error,

    // 计算属性
    missionTypes,
    mainMenuSections,
    getSubCategories,
    getSubCategoryByKey,
    getMissionTypeDisplay,

    // 方法
    loadMenuConfig,
    ensureConfigLoaded,
    ensureSubCategoriesLoaded,
    clearError,
    reset,
    reloadConfig
  }
})