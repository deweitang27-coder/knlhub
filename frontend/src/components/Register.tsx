import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'
import { Eye, EyeOff, ArrowRight, UserPlus, FolderOpen, Zap, Shield, CheckCircle } from 'lucide-react'

function Register() {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!name || !email || !password) {
      setError('请填写所有字段')
      return
    }

    if (password.length < 6) {
      setError('密码长度至少 6 位')
      return
    }

    setIsLoading(true)
    try {
      await register({ name, email, password })
      navigate('/login')
    } catch {
      setError('注册失败，该邮箱可能已被使用')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-white">
      {/* 左侧品牌区 */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-violet-800 p-12 flex-col justify-between">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&h=800&fit=crop')] bg-cover bg-center opacity-10"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-indigo-900/50 via-transparent to-transparent"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <UserPlus className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">KnlHub</span>
          </div>

          <div className="space-y-5 mb-12">
            <h1 className="text-4xl font-bold text-white leading-tight">
              开始你的<br/>
              <span className="text-indigo-200">知识管理之旅</span>
            </h1>
            <p className="text-indigo-100 text-lg leading-relaxed max-w-md">
              注册账号，体验高效的文档管理、智能搜索和团队协作功能
            </p>
          </div>

          <div className="space-y-6">
            {[
              { icon: FolderOpen, title: '云端存储', desc: '随时随地访问你的文档' },
              { icon: Zap, title: '快速上手', desc: '简单几步即可完成配置' },
              { icon: Shield, title: '安全可靠', desc: '数据加密，隐私有保障' },
            ].map((item) => (
              <div key={item.title} className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-white/20 transition-colors">
                  <item.icon className="w-5 h-5 text-indigo-100" />
                </div>
                <div>
                  <div className="font-semibold text-white">{item.title}</div>
                  <div className="text-sm text-indigo-200">{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-1.5 text-indigo-200 text-sm">
                <CheckCircle className="w-4 h-4" />
                <span>免费使用</span>
              </div>
            ))}
          </div>
          <p className="text-indigo-200/70 text-sm">© 2024 KnlHub · 知识管理平台</p>
        </div>
      </div>

      {/* 右侧表单区 */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-gray-50">
        <div className="w-full max-w-sm animate-fade-in-up">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <UserPlus className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">KnlHub</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">创建账号</h2>
            <p className="text-gray-500">填写信息，快速开始使用</p>
          </div>

          <div className="card-elevated p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="你的用户名"
                  className="input-field"
                  disabled={isLoading}
                />
              </div>

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
                    placeholder="至少 6 位字符"
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
                    <span>注册中...</span>
                  </>
                ) : (
                  <>
                    <span>注册</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="mt-6 text-center">
            <p className="text-gray-500">
              已有账号？{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium transition-colors">
                立即登录
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
