import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { login } from '../api/auth'
import { Eye, EyeOff, ArrowRight, FileText, Shield, Zap, CheckCircle, Sparkles, Github } from 'lucide-react'

function Login() {
  const navigate = useNavigate()
  const loginAuth = useAuthStore((state) => state.login)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !password) {
      setError('请输入邮箱和密码')
      return
    }

    setIsLoading(true)
    try {
      const response = await login({ email, password })
      loginAuth(response.data.access_token, response.data.user.email, response.data.user.name)
      navigate('/chat')
    } catch {
      setError('邮箱或密码错误，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-white">
      {/* 左侧品牌区 */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-emerald-600 via-emerald-700 to-teal-800 p-12 flex-col justify-between">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&h=800&fit=crop')] bg-cover bg-center opacity-10"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-emerald-900/50 via-transparent to-transparent"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">KnlHub</span>
          </div>

          <div className="space-y-5 mb-12">
            <h1 className="text-4xl font-bold text-white leading-tight">
              让知识管理<br/>
              <span className="text-emerald-200">更高效、更简单</span>
            </h1>
            <p className="text-emerald-100 text-lg leading-relaxed max-w-md">
              上传文档、智能搜索、快速分享，一站式解决你的知识管理需求
            </p>
          </div>

          <div className="space-y-6">
            {[
              { icon: FileText, title: '文档管理', desc: '支持多种格式，自动解析内容' },
              { icon: Zap, title: '智能搜索', desc: '语义检索，精准定位所需内容' },
              { icon: Shield, title: '安全可靠', desc: '数据加密存储，隐私有保障' },
            ].map((item) => (
              <div key={item.title} className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-white/20 transition-colors">
                  <item.icon className="w-5 h-5 text-emerald-100" />
                </div>
                <div>
                  <div className="font-semibold text-white">{item.title}</div>
                  <div className="text-sm text-emerald-200">{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-1.5 text-emerald-200 text-sm">
                <CheckCircle className="w-4 h-4" />
                <span>安全可靠</span>
              </div>
            ))}
          </div>
          <p className="text-emerald-200/70 text-sm">© 2024 KnlHub · 知识管理平台</p>
        </div>
      </div>

      {/* 右侧表单区 */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 relative overflow-hidden bg-white">
        {/* 背景图片 */}
        <div className="absolute inset-0" style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&h=1200&fit=crop')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}>
          <div className="absolute inset-0 bg-white/70"></div>
        </div>
        {/* 渐变光晕 */}
        <div className="absolute -top-20 -right-20 w-96 h-96 rounded-full" style={{
          background: 'radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%)',
        }}></div>
        <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full" style={{
          background: 'radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)',
        }}></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full" style={{
          background: 'radial-gradient(circle, rgba(139,92,246,0.05) 0%, transparent 60%)',
        }}></div>
        <div className="relative z-10 w-full max-w-sm animate-fade-in-up">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">KnlHub</span>
          </div>

          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <h2 className="text-2xl font-bold text-gray-900">欢迎回来</h2>
              <Sparkles className="w-5 h-5 text-amber-500" />
            </div>
            <p className="text-gray-500">登录你的账号继续操作</p>
          </div>

          <div className="card-elevated p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="input-field"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">密码</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="请输入密码"
                    className="input-field pr-12"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-1"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600 animate-fade-in flex items-center gap-2">
                  <Shield className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button type="submit" disabled={isLoading} className="btn-primary w-full flex items-center justify-center gap-2">
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>登录中...</span>
                  </>
                ) : (
                  <>
                    <span>登录</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="mt-6 text-center space-y-3">
            <p className="text-gray-500">
              还没有账号？{' '}
              <Link to="/register" className="text-emerald-600 hover:text-emerald-700 font-medium transition-colors">
                立即注册
              </Link>
            </p>
            <div className="flex items-center justify-center gap-2">
              <a
                href="https://github.com/deweitang27-coder/knlhub"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors"
                title="在 GitHub 上查看项目"
              >
                <Github className="w-5 h-5" />
                <span className="text-sm">GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
