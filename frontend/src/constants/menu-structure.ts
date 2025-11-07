import type { MenuSection } from '@/types'

/**
 * 菜单结构配置
 */
export const MENU_STRUCTURE_CONFIG: {
  commission: MenuSection
} = {
  commission: {
    displayName: "委托",
    children: {
      daily_commission: {
        key: "daily_commission",
        displayName: "委托",
        missions: [],
      },
      night_sailing_manual: {
        key: "night_sailing_manual",
        displayName: "夜航手册",
        missions: [],
      },
      commission_letter: {
        key: "commission_letter",
        displayName: "委托密函",
        missions: [],
      },
    },
  },
}