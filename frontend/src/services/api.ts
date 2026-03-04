import axios from 'axios';
import type {
  LoginCredentials,
  AuthResponse,
  User,
  Role,
  Task,
  TaskCreatePayload,
  TaskUpdatePayload,
  TaskComment,
  Document,
  Meeting,
  MeetingCreatePayload,
  Resource,
  Notification,
  DashboardData,
  DocumentUploadPayload,
  DocumentApproval,
  UserCreatePayload,
  UserUpdatePayload,
} from '@/types';
import { ApprovalAction } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API Error:', error.message, error.response?.status, error.config?.url);
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
  },
};

export const tasksAPI = {
  getTasks: async (params?: any): Promise<Task[]> => {
    const response = await api.get<Task[]>('/tasks/', { params });
    return response.data;
  },
  
  getTask: async (id: number): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },
  
  createTask: async (task: TaskCreatePayload): Promise<Task> => {
    const response = await api.post<Task>('/tasks/', task);
    return response.data;
  },
  
  updateTask: async (id: number, task: TaskUpdatePayload): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}`, task);
    return response.data;
  },
  
  escalateTask: async (id: number, reason: string): Promise<Task> => {
    const response = await api.post<Task>(`/tasks/${id}/escalate`, { escalation_reason: reason });
    return response.data;
  },
  
  deleteTask: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  getTaskComments: async (id: number): Promise<TaskComment[]> => {
    const response = await api.get<TaskComment[]>(`/tasks/${id}/comments`);
    return response.data;
  },

  addTaskComment: async (id: number, comment: string): Promise<TaskComment> => {
    const response = await api.post<TaskComment>(`/tasks/${id}/comments`, { comment });
    return response.data;
  },
};

export const documentsAPI = {
  getDocuments: async (params?: { status?: string; department?: string; my_uploads?: boolean; pending_approval?: boolean }): Promise<Document[]> => {
    const response = await api.get<Document[]>('/documents/', { params });
    return response.data;
  },

  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  getApprovals: async (id: number): Promise<DocumentApproval[]> => {
    const response = await api.get<DocumentApproval[]>(`/documents/${id}/approvals`);
    return response.data;
  },

  createDocument: async (payload: DocumentUploadPayload): Promise<Document> => {
    const formData = new FormData();
    formData.append('title', payload.title);
    formData.append('document_type', payload.document_type);
    formData.append('department', payload.department);
    formData.append('approval_chain_type', payload.approval_chain_type);
    formData.append('file', payload.file);
    if (payload.description) {
      formData.append('description', payload.description);
    }

    const response = await api.post<Document>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  downloadDocument: async (id: number): Promise<Blob> => {
    const response = await api.get(`/documents/${id}/download`, { responseType: 'blob' });
    return response.data;
  },

  approveDocument: async (
    id: number,
    action: ApprovalAction,
    comments?: string
  ): Promise<DocumentApproval> => {
    const response = await api.post<DocumentApproval>(`/documents/${id}/approve`, {
      action,
      comments,
    });
    return response.data;
  },
};

export const meetingsAPI = {
  getMeetings: async (params?: any): Promise<Meeting[]> => {
    const response = await api.get<Meeting[]>('/meetings/', { params });
    return response.data;
  },
  
  getMeeting: async (id: number): Promise<Meeting> => {
    const response = await api.get<Meeting>(`/meetings/${id}`);
    return response.data;
  },
  
  createMeeting: async (meeting: MeetingCreatePayload): Promise<Meeting> => {
    const response = await api.post<Meeting>('/meetings/', meeting);
    return response.data;
  },
  
  approveMeeting: async (id: number): Promise<Meeting> => {
    const response = await api.post<Meeting>(`/meetings/${id}/approve`);
    return response.data;
  },
  
  rejectMeeting: async (id: number): Promise<Meeting> => {
    const response = await api.post<Meeting>(`/meetings/${id}/reject`);
    return response.data;
  },

  getResources: async (params?: { available_only?: boolean }): Promise<Resource[]> => {
    const response = await api.get<Resource[]>('/meetings/resources/', { params });
    return response.data;
  },

  getParticipants: async (id: number): Promise<User[]> => {
    const response = await api.get<User[]>(`/meetings/${id}/participants`);
    return response.data;
  },
};

export const usersAPI = {
  getUsers: async (params?: { department?: string }): Promise<User[]> => {
    const cleanParams = params?.department ? { department: params.department } : {};
    const response = await api.get<User[]>('/users/', { params: cleanParams });
    return response.data;
  },

  createUser: async (user: UserCreatePayload): Promise<User> => {
    const response = await api.post<User>('/users/', user);
    return response.data;
  },

  updateUser: async (id: number, user: UserUpdatePayload): Promise<User> => {
    const response = await api.put<User>(`/users/${id}`, user);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`);
  },
};

export const rolesAPI = {
  getRoles: async (): Promise<Role[]> => {
    const response = await api.get<Role[]>('/roles/');
    return response.data;
  },
};

export const notificationsAPI = {
  getNotifications: async (params?: { unread_only?: boolean }): Promise<Notification[]> => {
    const response = await api.get<Notification[]>('/notifications/', { params });
    return response.data;
  },
  
  getUnreadCount: async (): Promise<number> => {
    const response = await api.get<{ unread_count: number }>('/notifications/unread-count');
    return response.data.unread_count;
  },
  
  markAsRead: async (ids: number[]): Promise<void> => {
    await api.post('/notifications/mark-read', { notification_ids: ids });
  },
  
  markAllAsRead: async (): Promise<void> => {
    await api.post('/notifications/mark-all-read');
  },
};

export const reportsAPI = {
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/reports/dashboard');
    return response.data;
  },
  
  getTaskCompletionReport: async (params?: any): Promise<any> => {
    const response = await api.get('/reports/task-completion', { params });
    return response.data;
  },
  
  getApprovalTimelineReport: async (params?: any): Promise<any> => {
    const response = await api.get('/reports/approval-timeline', { params });
    return response.data;
  },
};

export default api;
