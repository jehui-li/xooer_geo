'use client'

import { useState, KeyboardEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createAudit } from '@/lib/api'
import type { AuditRequest } from '@/types/api'

/**
 * 表单验证 Schema
 */
const auditFormSchema = z.object({
  brand_name: z.string().min(1, '品牌名称不能为空').max(100, '品牌名称不能超过100个字符'),
  keywords: z
    .array(z.string().min(1, '关键词不能为空').max(50, '关键词不能超过50个字符'))
    .min(1, '至少需要一个关键词')
    .max(20, '关键词数量不能超过20个'),
  target_website: z
    .string()
    .refine(
      (val) => !val || val === '' || z.string().url().safeParse(val).success,
      '请输入有效的 URL（例如：https://example.com）'
    )
    .optional()
    .or(z.literal('')),
  ground_truth_json: z
    .string()
    .optional()
    .refine(
      (val) => {
        if (!val || val.trim() === '') return true
        try {
          JSON.parse(val)
          return true
        } catch {
          return false
        }
      },
      'Ground Truth 必须是有效的 JSON 格式'
    ),
})

type AuditFormData = z.infer<typeof auditFormSchema>

/**
 * 创建检测页
 */
export default function NewAuditPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [keywordInput, setKeywordInput] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<AuditFormData>({
    resolver: zodResolver(auditFormSchema),
    defaultValues: {
      brand_name: '',
      keywords: [],
      target_website: '',
      ground_truth_json: '',
    },
  })

  // 监听关键词数组
  const keywords = watch('keywords')

  // 添加关键词（标签输入）
  const handleKeywordKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const value = keywordInput.trim()
      if (value && !keywords.includes(value)) {
        if (keywords.length < 20) {
          setValue('keywords', [...keywords, value])
          setKeywordInput('')
        }
      }
    } else if (e.key === 'Backspace' && keywordInput === '' && keywords.length > 0) {
      // 删除最后一个关键词
      setValue('keywords', keywords.slice(0, -1))
    }
  }

  // 删除关键词
  const removeKeyword = (index: number) => {
    setValue(
      'keywords',
      keywords.filter((_, i) => i !== index)
    )
  }

  // 提交表单
  const onSubmit = async (data: AuditFormData) => {
    try {
      setLoading(true)
      setError(null)
      setSuccess(false)

      // 如果还有未添加的关键词，先添加到数组中
      let finalKeywords = [...data.keywords]
      if (keywordInput.trim()) {
        const trimmedKeyword = keywordInput.trim()
        if (!finalKeywords.includes(trimmedKeyword)) {
          finalKeywords.push(trimmedKeyword)
        }
        setKeywordInput('')
        // 更新表单中的keywords字段，以便验证
        setValue('keywords', finalKeywords, { shouldValidate: true })
      }

      // 验证关键词（确保至少有一个）
      if (finalKeywords.length === 0) {
        setError('至少需要一个关键词')
        setLoading(false)
        return
      }

      // 解析 Ground Truth JSON
      let groundTruth: Record<string, any> | undefined = undefined
      if (data.ground_truth_json && data.ground_truth_json.trim()) {
        try {
          groundTruth = JSON.parse(data.ground_truth_json.trim())
          if (typeof groundTruth !== 'object' || groundTruth === null || Array.isArray(groundTruth)) {
            setError('Ground Truth 必须是一个 JSON 对象')
            setLoading(false)
            return
          }
        } catch (e) {
          setError('Ground Truth JSON 格式错误')
          setLoading(false)
          return
        }
      }

      // 构建请求数据
      // target_brand 自动设置为与 brand_name 相同
      const requestData: AuditRequest = {
        brand_name: data.brand_name.trim(),
        target_brand: data.brand_name.trim(), // 自动使用品牌名称作为目标品牌
        keywords: finalKeywords,
        target_website: data.target_website?.trim() || undefined,
        ground_truth: groundTruth,
      }

      // 调用 API
      const audit = await createAudit(requestData)

      // 显示成功提示
      setSuccess(true)

      // 延迟跳转到详情页（让用户看到成功提示）
      setTimeout(() => {
        router.push(`/audits/${audit.audit_id}`)
      }, 1000)
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail || err?.message || '创建检测失败，请稍后重试'
      setError(errorMessage)
      console.error('Failed to create audit:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container py-8">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">创建新检测</h1>
        <p className="text-muted-foreground mt-2">
          创建一个新的品牌检测任务，分析品牌在生成式引擎中的表现
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          <p>{error}</p>
        </div>
      )}

      {/* 成功提示 */}
      {success && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200">
          <p>检测任务创建成功，正在跳转到详情页...</p>
        </div>
      )}

      {/* 表单 */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="rounded-lg border bg-card p-6">
          <h2 className="mb-6 text-xl font-semibold">基本信息</h2>

          {/* 品牌名称 */}
          <div className="mb-6">
            <label
              htmlFor="brand_name"
              className="block text-sm font-medium text-foreground mb-2"
            >
              品牌名称 <span className="text-red-500">*</span>
            </label>
            <input
              id="brand_name"
              type="text"
              {...register('brand_name')}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="例如：Asana"
            />
            {errors.brand_name && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.brand_name.message}
              </p>
            )}
          </div>

          {/* 关键词 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-foreground mb-2">
              关键词 <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              {/* 已添加的关键词标签 */}
              {keywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 rounded-md bg-primary/10 px-3 py-1 text-sm text-primary"
                    >
                      {keyword}
                      <button
                        type="button"
                        onClick={() => removeKeyword(index)}
                        className="ml-1 hover:text-primary/80 focus:outline-none"
                        aria-label={`删除关键词 ${keyword}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
              {/* 关键词输入框 */}
              <input
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={handleKeywordKeyDown}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="输入关键词后按 Enter 或逗号添加（最多20个）"
                disabled={keywords.length >= 20}
              />
            </div>
            {errors.keywords && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.keywords.message || '至少需要一个关键词'}
              </p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
              已添加 {keywords.length} 个关键词（最多 20 个）
            </p>
          </div>

          {/* 目标网站 */}
          <div className="mb-6">
            <label
              htmlFor="target_website"
              className="block text-sm font-medium text-foreground mb-2"
            >
              目标网站 URL（可选）
            </label>
            <input
              id="target_website"
              type="url"
              {...register('target_website')}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="https://example.com"
            />
            {errors.target_website && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.target_website.message}
              </p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
              用于引用链接分析的官方网站地址
            </p>
          </div>
        </div>

        {/* Ground Truth 部分 */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="mb-6 text-xl font-semibold">Ground Truth（可选）</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            用于内容准确度检查的真实数据。请输入有效的 JSON 对象格式，例如：
          </p>
          <pre className="mb-4 rounded-md bg-muted p-3 text-xs overflow-x-auto">
            {`{
  "price": "99.99",
  "features": ["feature1", "feature2"],
  "description": "产品描述"
}`}
          </pre>
          <div>
            <label
              htmlFor="ground_truth_json"
              className="block text-sm font-medium text-foreground mb-2"
            >
              Ground Truth JSON
            </label>
            <textarea
              id="ground_truth_json"
              {...register('ground_truth_json')}
              rows={8}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder='{"key": "value"}'
            />
            {errors.ground_truth_json && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.ground_truth_json.message}
              </p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
              用于与 LLM 提取的内容进行对比，验证准确性
            </p>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            取消
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            {loading ? '创建中...' : '创建检测'}
          </button>
        </div>
      </form>
    </div>
  )
}

