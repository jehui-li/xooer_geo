import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { API_CONFIG, logConfig } from '@/lib/config/env'

// ============================================
// API 配置（从统一配置读取）
// ============================================
const API_BASE_URL = API_CONFIG.baseURL
const API_KEY = API_CONFIG.apiKey

// 在开发环境下打印配置信息
logConfig()

// ============================================
// 创建 axios 实例
// ============================================
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // 只在 API_KEY 存在时添加认证头
    ...(API_KEY && { 'X-API-Key': API_KEY }),
  },
  timeout: 30000, // 30 秒超时
})

// ============================================
// 请求拦截器（在发送请求前执行）
// ============================================
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加请求日志、修改请求配置等
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      })
    }
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// ============================================
// 响应拦截器（在收到响应后执行）
// ============================================
apiClient.interceptors.response.use(
  (response) => {
    // 成功响应：可以在这里添加日志、处理响应数据等
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      })
    }
    return response
  },
  (error: AxiosError) => {
    // ============================================
    // 统一错误处理
    // ============================================
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status
      const data = error.response.data as any

      // 根据不同的状态码进行处理
      switch (status) {
        case 401:
          console.error('❌ 未授权：请检查 API Key 是否正确')
          // 可以在这里触发登录页面跳转或显示错误提示
          break
        case 403:
          console.error('❌ 禁止访问：没有权限执行此操作')
          break
        case 404:
          console.error('❌ 资源未找到：请求的接口或数据不存在')
          break
        case 422:
          console.error('❌ 请求参数错误：', data?.detail || data?.error)
          break
        case 500:
          console.error('❌ 服务器内部错误：请稍后重试')
          break
        case 503:
          console.error('❌ 服务暂时不可用：服务器可能正在维护')
          break
        default:
          console.error(`❌ 请求失败 (${status})：`, data?.detail || data?.error || error.message)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应（网络错误、超时等）
      console.error('❌ 网络错误：无法连接到服务器，请检查网络连接和服务器状态')
    } else {
      // 其他错误（请求配置错误等）
      console.error('❌ 请求错误：', error.message)
    }

    // 返回错误，让调用方处理
    return Promise.reject(error)
  }
)

// ============================================
// 导出 API 客户端实例
// ============================================
export default apiClient

// 导出配置信息（方便调试）
export { API_CONFIG } from '@/lib/config/env'

