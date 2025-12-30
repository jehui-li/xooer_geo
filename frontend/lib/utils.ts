/**
 * 工具函数统一导出入口
 * 
 * 为了兼容 shadcn/ui 的标准导入方式 @/lib/utils
 * 同时也支持 @/lib/utils/cn 和 @/lib/utils/formatters 的导入方式
 */

export { cn } from './utils/cn'
export * from './utils/formatters'

