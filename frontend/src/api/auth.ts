import apiClient from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    email: string
    name: string
  }
}

export const login = (data: LoginRequest) => {
  const formData = new FormData()
  formData.append('username', data.email)
  formData.append('password', data.password)

  return apiClient.post<AuthResponse>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export const register = (data: RegisterRequest) =>
  apiClient.post<AuthResponse>('/auth/register', data)

export interface DocumentItem {
  id: string
  filename: string
  status: string
  created_at: string
  chunk_count: number
}

export interface QueryRequest {
  message: string
  doc_id?: string
}

export interface QueryResponse {
  answer: string
  sources: { content: string; similarity: number }[]
}

export const uploadDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post<DocumentItem>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const listDocuments = () =>
  apiClient.get<DocumentItem[]>('/documents/')

export const deleteDocument = (docId: string) =>
  apiClient.delete<void>(`/documents/${docId}`)

export const sendQuery = (data: QueryRequest) =>
  apiClient.post<QueryResponse>('/query/', data)
