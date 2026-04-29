import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Home, FolderOpen, FilePlus, Settings as SettingsIcon, LogOut, User, FileText } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const navItems = [
  { path: '/chat', icon: Home, label: '知识问答' },
  { path: '/documents', icon: FolderOpen, label: '文档管理' },
  { path: '/upload', icon: FilePlus, label: '上传文件' },
  { path: '/settings', icon: SettingsIcon, label: '设置' },
]

function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-[#fafafa]">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col">
        <div className="px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">KnlHub</span>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`nav-item w-full ${isActive ? 'nav-item-active' : 'nav-item-inactive'}`}
              >
                <div className="nav-icon">
                  <item.icon className="w-5 h-5" />
                </div>
                {item.label}
              </button>
            )
          })}
        </nav>

        <div className="px-3 pb-4 space-y-2">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50">
            <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
              <User className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.name || '用户'}</p>
              <p className="text-xs text-gray-400 truncate">{user?.email || ''}</p>
            </div>
          </div>

          <button onClick={handleLogout} className="btn-danger w-full flex items-center justify-center gap-2">
            <LogOut className="w-4 h-4" />
            退出登录
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
