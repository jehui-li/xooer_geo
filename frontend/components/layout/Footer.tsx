/**
 * Footer 组件
 */
export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t bg-background">
      <div className="container py-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* 关于 */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">关于</h3>
            <p className="text-sm text-muted-foreground">
              GEO Agent 是一个自动化检测品牌在生成式引擎中表现的智能代理系统。
            </p>
          </div>

          {/* 链接 */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">快速链接</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="/audits"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  检测列表
                </a>
              </li>
              <li>
                <a
                  href="/audits/new"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  创建检测
                </a>
              </li>
            </ul>
          </div>

          {/* 文档 */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">文档</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  API 文档
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  使用指南
                </a>
              </li>
            </ul>
          </div>

          {/* 联系 */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">联系</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  支持
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* 版权信息 */}
        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>© {currentYear} GEO Agent. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

