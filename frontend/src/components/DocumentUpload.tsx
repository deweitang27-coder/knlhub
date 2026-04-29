import { useState, useCallback } from 'react'
import { Upload, FileText, CheckCircle, X, AlertCircle, CloudUpload, File, Shield } from 'lucide-react'
import { uploadDocument } from '../api/auth'

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

interface UploadFile {
  file: File
  name: string
  size: number
  status: UploadStatus
  progress: number
}

function DocumentUpload() {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<UploadFile[]>([])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(Array.from(e.target.files))
  }

  const addFiles = (newFiles: File[]) => {
    const uploadFiles: UploadFile[] = newFiles.map((file) => ({
      file, name: file.name, size: file.size, status: 'idle', progress: 0,
    }))
    setFiles((prev) => [...prev, ...uploadFiles])
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const uploadSingleFile = async (index: number, fileObj: UploadFile) => {
    setFiles((prev) => prev.map((f, i) => i === index ? { ...f, status: 'uploading', progress: 0 } : f))
    try {
      const progressTimer = setInterval(() => {
        setFiles((prev) => prev.map((f, i) => i !== index || f.status !== 'uploading' ? f : { ...f, progress: Math.min(f.progress + 20, 90) }))
      }, 500)
      await uploadDocument(fileObj.file)
      clearInterval(progressTimer)
      setFiles((prev) => prev.map((f, i) => i === index ? { ...f, progress: 100, status: 'success' } : f))
    } catch {
      setFiles((prev) => prev.map((f, i) => i === index ? { ...f, status: 'error', progress: 0 } : f))
    }
  }

  const handleStartUpload = async () => {
    const idleFiles = files.map((f, i) => ({ file: f, index: i })).filter((item) => item.file.status === 'idle')
    for (const { index, file: fileObj } of idleFiles) await uploadSingleFile(index, fileObj)
  }

  const hasIdleFiles = files.some((f) => f.status === 'idle')

  return (
    <div className="flex flex-col h-full bg-[#fafafa]">
      {/* 标题栏 */}
      <div className="header-bar bg-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center">
            <Upload className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900">上传文件</h2>
            <p className="text-xs text-gray-400">支持 PDF、Word、Markdown 等格式</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-2xl mx-auto space-y-6 animate-scale-in">
          {/* 拖拽区域 */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`drop-zone ${isDragging ? 'drop-zone-active' : ''}`}
          >
            <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CloudUpload className="w-7 h-7 text-emerald-600" />
            </div>
            <h3 className="text-base font-semibold text-gray-900 mb-1">拖拽文件到此处</h3>
            <p className="text-sm text-gray-400 mb-4">或点击下方按钮选择文件</p>
            <label className="btn-primary inline-flex items-center gap-2 cursor-pointer">
              <FileText className="w-4 h-4" />
              <span>选择文件</span>
              <input type="file" multiple accept=".pdf,.doc,.docx,.md,.txt,.csv,.xlsx,.pptx" onChange={handleFileInput} className="hidden" />
            </label>
          </div>

          {/* 文件列表 */}
          {files.length > 0 && (
            <div className="space-y-3 animate-fade-in-up">
              <h4 className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <File className="w-4 h-4" />
                已选择 <span className="text-emerald-600 font-semibold">{files.length}</span> 个文件
              </h4>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 card animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      file.status === 'success' ? 'bg-emerald-50' : file.status === 'error' ? 'bg-red-50' : 'bg-gray-100'
                    }`}>
                      <FileText className={`w-5 h-5 ${
                        file.status === 'success' ? 'text-emerald-600' : file.status === 'error' ? 'text-red-600' : 'text-gray-400'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-gray-400">{formatFileSize(file.size)}</span>
                        {file.status === 'uploading' && (
                          <div className="flex items-center gap-2">
                            <div className="w-24 progress-bar">
                              <div className="progress-bar-fill" style={{ width: `${file.progress}%` }} />
                            </div>
                            <span className="text-xs text-emerald-600 font-medium">{Math.round(file.progress)}%</span>
                          </div>
                        )}
                        {file.status === 'success' && (
                          <span className="status-badge status-completed"><CheckCircle className="w-3 h-3" />完成</span>
                        )}
                        {file.status === 'error' && (
                          <span className="status-badge status-failed"><X className="w-3 h-3" />失败</span>
                        )}
                      </div>
                    </div>
                    {file.status === 'idle' && (
                      <button onClick={() => removeFile(index)} className="p-1.5 hover:bg-red-50 rounded-lg transition-colors">
                        <X className="w-4 h-4 text-gray-400 hover:text-red-500" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {hasIdleFiles && (
                <button onClick={handleStartUpload} className="btn-primary w-full flex items-center justify-center gap-2">
                  <Upload className="w-4 h-4" />
                  <span>开始上传并处理</span>
                </button>
              )}
            </div>
          )}

          {/* 说明 */}
          <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-xl animate-fade-in" style={{ animationDelay: '100ms' }}>
            <AlertCircle className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-gray-600">
              <p className="font-semibold text-gray-900 mb-1">上传说明</p>
              <ul className="space-y-1">
                <li className="flex items-start gap-2"><span className="w-1 h-1 bg-emerald-400 rounded-full mt-2 flex-shrink-0" /><span>单个文件最大 50MB</span></li>
                <li className="flex items-start gap-2"><span className="w-1 h-1 bg-emerald-400 rounded-full mt-2 flex-shrink-0" /><span>上传后将自动解析和处理内容</span></li>
                <li className="flex items-start gap-2"><span className="w-1 h-1 bg-emerald-400 rounded-full mt-2 flex-shrink-0" /><span>处理完成后可在知识问答中查询</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentUpload
