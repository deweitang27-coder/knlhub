import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Search, User, FileText, HelpCircle, Lightbulb, MessageSquare } from 'lucide-react'
import { sendQuery, type QueryResponse } from '../api/auth'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await sendQuery({ message: userMessage.content })
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，请求失败，请稍后重试。',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#fafafa]">
      {/* 标题栏 */}
      <div className="header-bar bg-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900">知识问答</h2>
            <p className="text-xs text-gray-400">搜索并查询知识库内容</p>
          </div>
        </div>
      </div>

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mb-4">
                <Lightbulb className="w-8 h-8 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">欢迎使用 KnlHub</h3>
              <p className="text-gray-400 text-sm max-w-sm mb-6">
                上传文档后，可以在这里查询相关内容
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  { icon: FileText, text: '查看文档库' },
                  { icon: HelpCircle, text: '如何上传文件' },
                  { icon: Search, text: '搜索已有内容' },
                ].map((item) => (
                  <button
                    key={item.text}
                    onClick={() => setInput(item.text)}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-white border border-gray-200 rounded-lg text-xs text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50 transition-all"
                  >
                    <item.icon className="w-3.5 h-3.5" />
                    {item.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MessageSquare className="w-4 h-4 text-white" />
                  </div>
                )}
                <div className={msg.role === 'user' ? 'message-user' : 'message-assistant'}>
                  {msg.content}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-gray-500" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 justify-start animate-fade-in-up">
                <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                </div>
                <div className="message-assistant">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t bg-white">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你想查询的内容...（Shift + Enter 换行）"
            className="flex-1 resize-none px-4 py-2.5 input-field text-sm"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary px-5 py-2.5 flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatWindow
