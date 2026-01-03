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
  industry: z.string().min(1, '所属行业不能为空'),
  keywords: z.string().min(1, '关键词不能为空'),
  target_market_language: z.string().min(1, '目标市场语言不能为空'),
  ai_concerns: z.array(z.string()).optional(),
  xoobay_mall_interest: z.enum(['Yes', 'No']).nullable().optional(),
  xoorwa_interest: z.enum(['Yes', 'No']).nullable().optional(),
  contact_name: z.string().min(1, '联系人姓名不能为空').max(100, '联系人姓名不能超过100个字符'),
  company_email: z.string().min(1, '公司电子邮箱不能为空').email('请输入有效的邮箱地址'),
  company_website: z
    .string()
    .min(1, '公司官网不能为空')
    .refine(
      (val) => z.string().url().safeParse(val).success,
      '请输入有效的 URL（例如：https://example.com）'
    ),
  headquarters_location: z.string().min(1, '总部所在地不能为空').max(200, '总部所在地不能超过200个字符'),
  core_product_keywords: z
    .array(z.string().min(1, '关键词不能为空'))
    .min(1, '至少需要一个核心产品/服务关键词')
    .max(3, '最多只能输入3个关键词'),
  competitor_names: z.string().optional(),
  visibility_self_assessment: z.enum(['1', '2', '3', '4', '5']).nullable().optional(),
  monthly_budget: z.string().optional(),
  xoopay_service_need: z.enum(['Yes', 'No']).nullable().optional(),
  position: z.string().min(1, '职位不能为空').max(100, '职位不能超过100个字符'),
  contact_communication_id: z.string().min(1, '实时通讯工具号不能为空').max(100, '实时通讯工具号不能超过100个字符'),
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
      industry: '跨境电商',
      keywords: '',
      target_market_language: '英语',
      ai_concerns: [],
      xoobay_mall_interest: undefined,
      xoorwa_interest: undefined,
      contact_name: '',
      company_email: '',
      company_website: '',
      headquarters_location: '',
      core_product_keywords: [],
      competitor_names: '',
      visibility_self_assessment: undefined,
      monthly_budget: '',
      xoopay_service_need: undefined,
      position: '',
      contact_communication_id: '',
    },
  })

  // 监听核心产品关键词数组
  const coreProductKeywords = watch('core_product_keywords')
  const [coreProductKeywordInput, setCoreProductKeywordInput] = useState('')
  const [aiConcerns, setAiConcerns] = useState<string[]>([])

  // 添加核心产品关键词
  const handleCoreProductKeywordKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const value = coreProductKeywordInput.trim()
      if (value && !coreProductKeywords.includes(value)) {
        if (coreProductKeywords.length < 3) {
          setValue('core_product_keywords', [...coreProductKeywords, value])
          setCoreProductKeywordInput('')
        }
      }
    } else if (e.key === 'Backspace' && coreProductKeywordInput === '' && coreProductKeywords.length > 0) {
      setValue('core_product_keywords', coreProductKeywords.slice(0, -1))
    }
  }

  // 删除核心产品关键词
  const removeCoreProductKeyword = (index: number) => {
    setValue(
      'core_product_keywords',
      coreProductKeywords.filter((_, i) => i !== index)
    )
  }

  // 提交表单
  const onSubmit = async (data: AuditFormData) => {
    console.log('✅ Form onSubmit called with data:', data)
    
    try {
      setLoading(true)
      setError(null)
      setSuccess(false)

      // 处理关键词：将逗号分隔的字符串转换为数组
      const keywordArray = data.keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0)

      // 构建请求数据
      const requestData: AuditRequest = {
        brand_name: data.brand_name.trim(),
        target_brand: data.brand_name.trim(),
        keywords: keywordArray.length > 0 ? keywordArray : [data.brand_name.trim()],
        target_website: data.company_website.trim(),
        ground_truth: undefined,
      }

      console.log('Sending request to API:', requestData)

      // 调用 API
      const audit = await createAudit(requestData)

      // 调试日志
      console.log('Audit created successfully:', audit)

      // 检查 audit_id 是否存在
      if (!audit || !audit.audit_id) {
        console.error('Audit response missing audit_id:', audit)
        throw new Error('创建检测成功，但未返回检测ID')
      }

      // 显示成功提示
      setSuccess(true)

      // 延迟跳转到报告页面（让用户看到成功提示）
      const reportUrl = `/audits/${audit.audit_id}/report`
      console.log('Will navigate to report page:', reportUrl)
      
      setTimeout(() => {
        console.log('Navigating to report page now:', reportUrl)
        // 使用 router.push 进行客户端路由跳转
        router.push(reportUrl)
        // 如果 router.push 不工作，尝试使用 window.location
        // window.location.href = reportUrl
      }, 1000)
    } catch (err: any) {
      console.error('Error in onSubmit:', err)
      const errorMessage =
        err?.response?.data?.detail || err?.message || '创建检测失败，请稍后重试'
      setError(errorMessage)
      console.error('Failed to create audit:', err)
      
      // 确保 loading 状态被重置
      setLoading(false)
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
          <p>检测创建成功，正在跳转到报告页面...</p>
        </div>
      )}

      {/* 成功提示 */}
      {success && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200">
          <p>检测创建成功，正在跳转到报告页面...</p>
        </div>
      )}

      {/* 表单 */}
      <form 
        onSubmit={handleSubmit(
          (data) => {
            console.log('✅ Form validation passed, calling onSubmit')
            onSubmit(data)
          },
          (errors) => {
            console.error('❌ Form validation failed:', errors)
            console.log('Form errors:', Object.keys(errors))
            // 显示第一个错误
            const firstError = Object.values(errors)[0]
            if (firstError) {
              console.error('First error:', firstError)
            }
          }
        )} 
        className="space-y-6"
      >
        <div className="rounded-lg border bg-card p-6">
          <div className="grid grid-cols-2 gap-6">
            {/* 左侧列 */}
            <div className="space-y-6">
          {/* 品牌名称 */}
              <div>
            <label
              htmlFor="brand_name"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
            >
                  <span className="whitespace-nowrap">品牌名称</span>
                  <span className="text-red-500 ml-1">*</span>
            </label>
            <input
              id="brand_name"
              type="text"
              {...register('brand_name')}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请填入您的品牌名称"
            />
            {errors.brand_name && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.brand_name.message}
              </p>
            )}
          </div>

              {/* 所属行业 */}
              <div>
                <label
                  htmlFor="industry"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">所属行业</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <select
                  id="industry"
                  {...register('industry')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="跨境电商">跨境电商</option>
                  <option value="电子商务">电子商务</option>
                  <option value="制造业">制造业</option>
                  <option value="金融服务">金融服务</option>
                  <option value="科技">科技</option>
                  <option value="教育">教育</option>
                  <option value="医疗健康">医疗健康</option>
                  <option value="其他">其他</option>
                </select>
                {errors.industry && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.industry.message}
              </p>
            )}
          </div>

          {/* 关键词 */}
              <div>
                <label
                  htmlFor="keywords"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">关键词</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="keywords"
                  type="text"
                  {...register('keywords')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="例如：Dyson, XooPay"
                />
                {errors.keywords && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.keywords.message}
                  </p>
                )}
              </div>

              {/* 目标市场语言 */}
              <div>
                <label
                  htmlFor="target_market_language"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">目标市场语言</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <select
                  id="target_market_language"
                  {...register('target_market_language')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="英语">英语</option>
                  <option value="中文">中文</option>
                  <option value="日语">日语</option>
                  <option value="韩语">韩语</option>
                  <option value="西班牙语">西班牙语</option>
                  <option value="法语">法语</option>
                  <option value="德语">德语</option>
                  <option value="其他">其他</option>
                </select>
                {errors.target_market_language && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.target_market_language.message}
                  </p>
                )}
              </div>

              {/* 您最担心的 AI 问题 */}
              <div>
                <label
                  htmlFor="ai_concerns"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">您最担心的 AI 问题</span>
                </label>
                <select
                  id="ai_concerns"
                  multiple
                  {...register('ai_concerns')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-h-[80px]"
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, (option) => option.value)
                    setAiConcerns(selected)
                    setValue('ai_concerns', selected)
                  }}
                >
                  <option value="推荐排序靠后">推荐排序靠后</option>
                  <option value="完全搜不到">完全搜不到</option>
                </select>
                <p className="mt-1 text-xs text-muted-foreground">
                  按住 Ctrl (Windows) 或 Command (Mac) 键可多选
                </p>
              </div>

              {/* 您是否感兴趣将产品入驻 XOOBAY 跨境商城 */}
              <div>
                <label className="flex items-center text-sm font-medium text-foreground mb-2">
                  <span className="whitespace-nowrap">您是否感兴趣将产品入驻 XOOBAY 跨境商城？</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="Yes"
                      {...register('xoobay_mall_interest')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">Yes</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="No"
                      {...register('xoobay_mall_interest')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">No</span>
                  </label>
                </div>
              </div>

              {/* 您是否有实体资产（库存/积分）代币化融资需求（XooRWA） */}
              <div>
                <label className="flex items-center text-sm font-medium text-foreground mb-2">
                  <span className="whitespace-nowrap">您是否有实体资产（库存/积分）代币化融资需求（XooRWA）？</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="Yes"
                      {...register('xoorwa_interest')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">Yes</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="No"
                      {...register('xoorwa_interest')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">No</span>
                  </label>
                </div>
              </div>

              {/* 联系人姓名 */}
              <div>
                <label
                  htmlFor="contact_name"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">联系人姓名</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="contact_name"
                  type="text"
                  {...register('contact_name')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请填入您的姓名"
                />
                {errors.contact_name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.contact_name.message}
                  </p>
                )}
              </div>

              {/* 公司电子邮箱 */}
              <div>
                <label
                  htmlFor="company_email"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">公司电子邮箱</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="company_email"
                  type="email"
                  {...register('company_email')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请输入您的公司电子邮箱"
                />
                {errors.company_email && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.company_email.message}
                  </p>
                )}
              </div>
            </div>

            {/* 右侧列 */}
            <div className="space-y-6">
              {/* 公司官网 */}
              <div>
                <label
                  htmlFor="company_website"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">公司官网</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="company_website"
                  type="url"
                  {...register('company_website')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请输入您公司的官方网址"
                />
                {errors.company_website && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.company_website.message}
                  </p>
                )}
              </div>

              {/* 总部所在地 */}
              <div>
                <label
                  htmlFor="headquarters_location"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">总部所在地</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="headquarters_location"
                  type="text"
                  {...register('headquarters_location')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请输入您公司的总部地址"
                />
                {errors.headquarters_location && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.headquarters_location.message}
                  </p>
                )}
              </div>

              {/* 核心产品/服务关键词 */}
              <div>
                <label className="flex items-center text-sm font-medium text-foreground mb-2">
                  <span className="whitespace-nowrap">核心产品/服务关键词</span>
                  <span className="text-red-500 ml-1">*</span>
            </label>
            <div className="space-y-2">
                  {coreProductKeywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                      {coreProductKeywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 rounded-md bg-primary/10 px-3 py-1 text-sm text-primary"
                    >
                      {keyword}
                      <button
                        type="button"
                            onClick={() => removeCoreProductKeyword(index)}
                        className="ml-1 hover:text-primary/80 focus:outline-none"
                        aria-label={`删除关键词 ${keyword}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
              <input
                type="text"
                    value={coreProductKeywordInput}
                    onChange={(e) => setCoreProductKeywordInput(e.target.value)}
                    onKeyDown={handleCoreProductKeywordKeyDown}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="最多可以输入3个关键词"
                    disabled={coreProductKeywords.length >= 3}
              />
            </div>
                {errors.core_product_keywords && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.core_product_keywords.message}
              </p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
                  已添加 {coreProductKeywords.length} 个关键词（最多 3 个）
            </p>
          </div>

              {/* 主要竞争对手名称 */}
              <div>
            <label
                  htmlFor="competitor_names"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
            >
                  <span className="whitespace-nowrap">主要竞争对手名称</span>
            </label>
            <input
                  id="competitor_names"
                  type="text"
                  {...register('competitor_names')}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="请输入您的主要竞争对手名称"
                />
              </div>

              {/* 目前在 AI 搜寻中的可见度自我评估 */}
              <div>
                <label className="flex items-center text-sm font-medium text-foreground mb-2">
                  <span className="whitespace-nowrap">目前在 AI 搜寻中的可见度自我评估</span>
                </label>
                <div className="flex gap-4">
                  {['1', '2', '3', '4', '5'].map((score) => (
                    <label key={score} className="flex items-center">
                      <input
                        type="radio"
                        value={score}
                        {...register('visibility_self_assessment')}
                        className="text-primary focus:ring-primary"
                      />
                      <span className="ml-2 text-sm">{score}分</span>
                    </label>
                  ))}
          </div>
        </div>

              {/* 预计月度 GEO 优化预算 */}
              <div>
                <label
                  htmlFor="monthly_budget"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">预计月度 GEO 优化预算</span>
                </label>
                <select
                  id="monthly_budget"
                  {...register('monthly_budget')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">如：10000 元</option>
                  <option value="5000">5000 元</option>
                  <option value="10000">10000 元</option>
                  <option value="20000">20000 元</option>
                  <option value="50000">50000 元</option>
                  <option value="100000">100000 元</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              {/* 您是否需要 XooPay 提供跨境贸易担保支付服务 */}
              <div>
                <label className="flex items-center text-sm font-medium text-foreground mb-2">
                  <span className="whitespace-nowrap">您是否需要 XooPay 提供跨境贸易担保支付服务？</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="Yes"
                      {...register('xoopay_service_need')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">Yes</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="No"
                      {...register('xoopay_service_need')}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="ml-2 text-sm">No</span>
                  </label>
                </div>
              </div>

              {/* 职位 */}
              <div>
                <label
                  htmlFor="position"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
                >
                  <span className="whitespace-nowrap">职位</span>
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  id="position"
                  type="text"
                  {...register('position')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="如：产品经理"
                />
                {errors.position && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.position.message}
                  </p>
                )}
              </div>

              {/* 实时通讯工具号 */}
          <div>
            <label
                  htmlFor="contact_communication_id"
                  className="flex items-center text-sm font-medium text-foreground mb-2"
            >
                  <span className="whitespace-nowrap">实时通讯工具号</span>
                  <span className="text-red-500 ml-1">*</span>
            </label>
                <input
                  id="contact_communication_id"
                  type="text"
                  {...register('contact_communication_id')}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="可以是 WhatsApp / Telegram / WeChat 等号码"
                />
                {errors.contact_communication_id && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.contact_communication_id.message}
              </p>
            )}
              </div>
            </div>
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
            onClick={() => {
              console.log('🟢 Submit button clicked, loading:', loading)
            }}
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            {loading ? '创建中...' : '创建检测'}
          </button>
        </div>
      </form>
    </div>
  )
}

