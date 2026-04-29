import { useState, useEffect } from 'react'
import { Key, Save, Eye, EyeOff, Database, Cpu, Settings as SettingsIcon, CheckCircle, HardDrive } from 'lucide-react'
import apiClient from '../api/client'

interface SettingsData {
  embedding_api_key: string
  llm_api_key: string
  embedding_provider: string
  llm_provider: string
  embedding_model: string
  llm_model: string
  chunk_size: number
  chunk_overlap: number
  top_k: number
  max_file_size_mb: number
}

const defaultSettings: SettingsData = {
  embedding_api_key: '',
  llm_api_key: '',
  embedding_provider: 'tongyi',
  llm_provider: 'deepseek',
  embedding_model: 'text-embedding-v3',
  llm_model: 'deepseek-chat',
  chunk_size: 512,
  chunk_overlap: 64,
  top_k: 5,
  max_file_size_mb: 50,
}

const embeddingProviders = [
  { value: 'tongyi', label: '通义千问', models: ['text-embedding-v3', 'text-embedding-v2'] },
  { value: 'zhipu', label: '智谱 AI', models: ['embedding-3', 'embedding-2'] },
]

const llmProviders = [
  { value: 'deepseek', label: 'DeepSeek', models: ['deepseek-chat', 'deepseek-reasoner'] },
  { value: 'tongyi', label: '通义千问', models: ['qwen-plus', 'qwen-max', 'qwen-turbo'] },
  { value: 'zhipu', label: '智谱 AI', models: ['glm-4', 'glm-4-flash'] },
  { value: 'kimi', label: 'Kimi', models: ['kimi-chat'] },
  { value: 'moonshot', label: '月之暗面', models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'] },
]

function Settings() {
  const [settings, setSettings] = useState<SettingsData>(defaultSettings)
  const [saved, setSaved] = useState(false)
  const [showEmbedKey, setShowEmbedKey] = useState(false)
  const [showLlmKey, setShowLlmKey] = useState(false)

  useEffect(() => {
    apiClient.get<SettingsData>('/settings/')
      .then((res) => setSettings(res.data))
      .catch(() => setSettings(defaultSettings))
  }, [])

  const update = (key: keyof SettingsData, value: string | number) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  const handleProviderChange = (field: 'embedding_provider' | 'llm_provider', value: string) => {
    const providerList = field === 'embedding_provider' ? embeddingProviders : llmProviders
    const provider = providerList.find((p) => p.value === value)
    const modelField = field === 'embedding_provider' ? 'embedding_model' : 'llm_model'

    setSettings((prev) => ({
      ...prev,
      [field]: value,
      [modelField]: provider?.models[0] || '',
    }))
    setSaved(false)
  }

  const currentEmbedModels = embeddingProviders.find((p) => p.value === settings.embedding_provider)?.models || []
  const currentLlmModels = llmProviders.find((p) => p.value === settings.llm_provider)?.models || []

  const handleSave = async () => {
    try {
      await apiClient.post<SettingsData>('/settings/', settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      alert('保存失败，请重试')
    }
  }

  const getEmbedLabel = (val: string) => embeddingProviders.find((p) => p.value === val)?.label || val
  const getLlmLabel = (val: string) => llmProviders.find((p) => p.value === val)?.label || val

  return (
    <div className="flex flex-col h-full bg-[#fafafa]">
      {/* 顶部标题栏 */}
      <div className="header-bar bg-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center">
            <SettingsIcon className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900">系统设置</h2>
            <p className="text-xs text-gray-400">配置 API 密钥和系统参数</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto space-y-6 animate-scale-in">
          {/* 保存成功提示 */}
          {saved && (
            <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-lg text-sm text-emerald-700 flex items-center gap-3 animate-fade-in">
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">设置已保存，立即生效</span>
            </div>
          )}

          {/* API 配置 */}
          <div className="card-elevated animate-fade-in">
            <div className="settings-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                  <Key className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-gray-900">API 配置</h3>
                  <p className="text-sm text-gray-400">配置 Embedding 和 LLM 模型的服务商及密钥</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Embedding 配置 */}
                <div className="p-5 bg-gray-50 rounded-lg border border-gray-100 space-y-4">
                  <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Embedding 模型
                  </h4>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">服务商</label>
                    <select
                      value={settings.embedding_provider}
                      onChange={(e) => handleProviderChange('embedding_provider', e.target.value)}
                      className="input-field"
                    >
                      {embeddingProviders.map((p) => (
                        <option key={p.value} value={p.value}>{p.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">模型</label>
                    <select
                      value={settings.embedding_model}
                      onChange={(e) => update('embedding_model', e.target.value)}
                      className="input-field"
                    >
                      {currentEmbedModels.map((m) => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">API Key</label>
                    <div className="relative">
                      <input
                        type={showEmbedKey ? 'text' : 'password'}
                        value={settings.embedding_api_key}
                        onChange={(e) => update('embedding_api_key', e.target.value)}
                        placeholder={getEmbedLabel(settings.embedding_provider) + ' API Key'}
                        className="input-field pr-10 font-mono text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => setShowEmbedKey(!showEmbedKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {showEmbedKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* LLM 配置 */}
                <div className="p-5 bg-gray-50 rounded-lg border border-gray-100 space-y-4">
                  <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Cpu className="w-4 h-4" />
                    LLM 对话模型
                  </h4>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">服务商</label>
                    <select
                      value={settings.llm_provider}
                      onChange={(e) => handleProviderChange('llm_provider', e.target.value)}
                      className="input-field"
                    >
                      {llmProviders.map((p) => (
                        <option key={p.value} value={p.value}>{p.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">模型</label>
                    <select
                      value={settings.llm_model}
                      onChange={(e) => update('llm_model', e.target.value)}
                      className="input-field"
                    >
                      {currentLlmModels.map((m) => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1.5">API Key</label>
                    <div className="relative">
                      <input
                        type={showLlmKey ? 'text' : 'password'}
                        value={settings.llm_api_key}
                        onChange={(e) => update('llm_api_key', e.target.value)}
                        placeholder={getLlmLabel(settings.llm_provider) + ' API Key'}
                        className="input-field pr-10 font-mono text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => setShowLlmKey(!showLlmKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {showLlmKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 基础设置 */}
            <div className="settings-section">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                  <HardDrive className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-gray-900">文档处理参数</h3>
                  <p className="text-sm text-gray-400">配置文本分块和检索参数</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">文本块大小</label>
                  <input
                    type="number"
                    value={settings.chunk_size}
                    onChange={(e) => update('chunk_size', parseInt(e.target.value) || 512)}
                    className="input-field"
                  />
                  <p className="text-xs text-gray-400 mt-1.5">推荐值：256 - 1024</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">文本块重叠</label>
                  <input
                    type="number"
                    value={settings.chunk_overlap}
                    onChange={(e) => update('chunk_overlap', parseInt(e.target.value) || 64)}
                    className="input-field"
                  />
                  <p className="text-xs text-gray-400 mt-1.5">推荐值：32 - 128</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">检索数量</label>
                  <input
                    type="number"
                    value={settings.top_k}
                    onChange={(e) => update('top_k', parseInt(e.target.value) || 5)}
                    className="input-field"
                  />
                  <p className="text-xs text-gray-400 mt-1.5">每次返回的相关片段数</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1.5">文件大小限制 (MB)</label>
                  <input
                    type="number"
                    value={settings.max_file_size_mb}
                    onChange={(e) => update('max_file_size_mb', parseInt(e.target.value) || 50)}
                    className="input-field"
                  />
                  <p className="text-xs text-gray-400 mt-1.5">单个文件上传上限</p>
                </div>
              </div>
            </div>

            {/* 保存按钮 */}
            <div className="px-6 pb-6">
              <button
                onClick={handleSave}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Save className="w-4 h-4" />
                <span>保存设置</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
