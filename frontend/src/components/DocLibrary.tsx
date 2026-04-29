import { useState, useEffect } from 'react'
import { FileText, FolderOpen, Plus, Trash2, RefreshCw, Calendar, Layers, AlertCircle } from 'lucide-react'
import { listDocuments, deleteDocument, uploadDocument } from '../api/auth'

interface DocumentItem {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  chunk_count: number
}

const statusConfig = {
  pending: { label: '待处理', class: 'status-pending' },
  processing: { label: '处理中', class: 'status-processing' },
  completed: { label: '已完成', class: 'status-completed' },
  failed: { label: '失败', class: 'status-failed' },
}

function DocLibrary() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchDocuments = async () => {
    setIsLoading(true)
    try {
      const response = await listDocuments()
      setDocuments(response.data)
    } catch {
      setDocuments([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
    const interval = setInterval(fetchDocuments, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleDelete = async (docId: string) => {
    if (!confirm('确认删除该文档？')) return
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      if (selectedDoc?.id === docId) setSelectedDoc(null)
    } catch {
      alert('删除失败')
    }
  }

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    handleUploadFiles(Array.from(files))
  }

  const handleUploadFiles = async (files: File[]) => {
    for (const file of files) {
      try {
        await uploadDocument(file)
        fetchDocuments()
      } catch {
        alert(`文件 ${file.name} 上传失败`)
      }
    }
  }

  return (
    <div className="flex h-full">
      {/* 左侧列表 */}
      <div className="w-80 bg-white border-r border-gray-100 flex flex-col">
        <div className="header-bar">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-emerald-600" />
              <div>
                <h2 className="text-base font-bold text-gray-900">文档管理</h2>
                <p className="text-xs text-gray-400">共 {documents.length} 个文档</p>
              </div>
            </div>
            <button onClick={fetchDocuments} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="刷新">
              <RefreshCw className={`w-4 h-4 text-gray-400 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {documents.map((doc) => {
            const status = statusConfig[doc.status]
            const isSelected = selectedDoc?.id === doc.id
            return (
              <button
                key={doc.id}
                onClick={() => setSelectedDoc(doc)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  isSelected
                    ? 'bg-emerald-50 border border-emerald-200'
                    : 'hover:bg-gray-50 border border-transparent hover:border-gray-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-emerald-100' : 'bg-gray-100'
                  }`}>
                    <FileText className={`w-5 h-5 ${isSelected ? 'text-emerald-600' : 'text-gray-400'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium truncate ${isSelected ? 'text-gray-900' : 'text-gray-700'}`}>
                      {doc.filename}
                    </p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={`status-badge ${status.class}`}>{status.label}</span>
                      <span className="text-xs text-gray-400">{new Date(doc.created_at).toLocaleDateString('zh-CN')}</span>
                    </div>
                  </div>
                </div>
              </button>
            )
          })}

          {documents.length === 0 && !isLoading && (
            <div className="text-center py-10">
              <div className="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <FileText className="w-7 h-7 text-gray-300" />
              </div>
              <p className="text-gray-400 text-sm">暂无文档</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-100">
          <label className="btn-primary w-full flex items-center justify-center gap-2 cursor-pointer">
            <Plus className="w-4 h-4" />
            <span>上传文档</span>
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.md,.txt,.csv,.xlsx,.pptx"
              onChange={handleUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* 右侧详情 */}
      <div className="flex-1 p-8 overflow-y-auto bg-[#fafafa]">
        {selectedDoc ? (
          <div className="max-w-xl mx-auto animate-fade-in-up">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{selectedDoc.filename}</h3>
                  <p className="text-sm text-gray-400 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(selectedDoc.created_at).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
              <button onClick={() => handleDelete(selectedDoc.id)} className="btn-danger" title="删除">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="card-elevated divide-y divide-gray-100">
              <div className="flex items-center justify-between p-5">
                <span className="text-sm text-gray-500 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  处理状态
                </span>
                <span className={`status-badge ${statusConfig[selectedDoc.status].class}`}>
                  {statusConfig[selectedDoc.status].label}
                </span>
              </div>
              <div className="flex items-center justify-between p-5">
                <span className="text-sm text-gray-500 flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  文本块数量
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {selectedDoc.chunk_count > 0 ? `${selectedDoc.chunk_count} 块` : '—'}
                </span>
              </div>
              <div className="flex items-center justify-between p-5">
                <span className="text-sm text-gray-500">文档 ID</span>
                <span className="text-xs text-gray-400 font-mono bg-gray-50 px-2 py-1 rounded">{selectedDoc.id}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
              <FolderOpen className="w-8 h-8 text-gray-300" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-1">选择文档</h3>
            <p className="text-gray-400 text-sm max-w-xs">从左侧列表中选择文档查看详情</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocLibrary
