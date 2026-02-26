export interface Role {
  id: number;
  role_name: string;
  hierarchy_level: number;
  description?: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role_id: number;
  department?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login?: string;
  role: Role;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export enum TaskStatus {
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  BLOCKED = 'blocked',
  REVIEW = 'review',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum TaskType {
  DEPARTMENT = 'department',
  CROSS_DEPARTMENT = 'cross_department',
  INSTITUTE_WIDE = 'institute_wide',
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  assigned_to_id: number;
  assigned_by_id: number;
  department: string;
  departments_involved?: string;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  is_escalated: boolean;
  escalation_reason?: string;
  escalated_at?: string;
  parent_task_id?: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface TaskCreatePayload {
  title: string;
  description?: string;
  assigned_to_id: number;
  department: string;
  task_type: TaskType;
  priority: TaskPriority;
  due_date?: string;
}

export interface TaskComment {
  id: number;
  task_id: number;
  user_id: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

export enum DocumentStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  REVISION_REQUESTED = 'revision_requested',
}

export enum ApprovalChainType {
  ROUTINE = 'routine',
  FINANCIAL = 'financial',
  STRATEGIC = 'strategic',
  CUSTOM = 'custom',
}

export interface Document {
  id: number;
  title: string;
  description?: string;
  document_type: string;
  uploader_id: number;
  department: string;
  file_path: string;
  file_size?: number;
  file_type?: string;
  approval_chain_type: ApprovalChainType;
  status: DocumentStatus;
  current_approver_id?: number;
  version: number;
  created_at: string;
  updated_at: string;
  final_approved_at?: string;
}

export enum ApprovalAction {
  APPROVED = 'approved',
  REJECTED = 'rejected',
  REVISION_REQUESTED = 'revision_requested',
}

export interface DocumentApproval {
  id: number;
  document_id: number;
  approver_id: number;
  action: ApprovalAction;
  comments?: string;
  approval_level: number;
  signature_hash?: string;
  created_at: string;
}

export interface DocumentUploadPayload {
  title: string;
  description?: string;
  document_type: string;
  department: string;
  approval_chain_type: ApprovalChainType;
  file: File;
}

export enum MeetingStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export interface Meeting {
  id: number;
  title: string;
  description?: string;
  organizer_id: number;
  start_time: string;
  end_time: string;
  room_id?: number;
  location?: string;
  status: MeetingStatus;
  priority: string;
  approved_by_id?: number;
  approved_at?: string;
  is_recurring: boolean;
  recurrence_pattern?: string;
  created_at: string;
  updated_at: string;
}

export interface MeetingCreatePayload {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  room_id?: number;
  location?: string;
  priority: string;
  participant_ids: number[];
}

export interface Resource {
  id: number;
  name: string;
  resource_type: string;
  capacity?: number;
  location?: string;
  is_available: boolean;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  related_entity_type?: string;
  related_entity_id?: number;
  action_url?: string;
  created_at: string;
  read_at?: string;
}

export interface DashboardData {
  role: string;
  [key: string]: any;
}
