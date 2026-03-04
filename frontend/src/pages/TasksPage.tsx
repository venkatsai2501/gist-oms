import { useState, useEffect } from 'react';
import { User, Task, TaskStatus, TaskPriority, TaskType, TaskCreatePayload } from '@/types';
import { tasksAPI, usersAPI } from '@/services/api';
import { Plus, Filter, AlertCircle, CheckCircle, Clock, XCircle, MessageSquare, TrendingUp } from 'lucide-react';
import LoadingSpinner from '@/components/LoadingSpinner';

interface TasksPageProps {
  user: User;
}

export default function TasksPage({ user }: TasksPageProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | ''>('');
  const [assignedToMe, setAssignedToMe] = useState(false);
  const [escalatedOnly, setEscalatedOnly] = useState(false);

  const [newTask, setNewTask] = useState<TaskCreatePayload>({
    title: '',
    description: '',
    assigned_to_id: 0,
    department: user.department || '',
    task_type: TaskType.DEPARTMENT,
    priority: TaskPriority.MEDIUM,
    due_date: '',
  });

  const [taskUpdate, setTaskUpdate] = useState({
    status: TaskStatus.ASSIGNED,
    progress_percentage: 0,
  });

  const [escalationReason, setEscalationReason] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTasks();
    loadUsers();
  }, [statusFilter, assignedToMe, escalatedOnly]);

  const loadTasks = async () => {
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (assignedToMe) params.assigned_to_me = true;
      if (escalatedOnly) params.escalated_only = true;

      const data = await tasksAPI.getTasks(params);
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const data = await usersAPI.getUsers();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const handleCreateTask = async () => {
    try {
      await tasksAPI.createTask(newTask);
      setShowCreateModal(false);
      setError('');
      setNewTask({
        title: '',
        description: '',
        assigned_to_id: 0,
        department: user.department || '',
        task_type: TaskType.DEPARTMENT,
        priority: TaskPriority.MEDIUM,
        due_date: '',
      });
      loadTasks();
    } catch (error: any) {
      console.error('Failed to create task:', error);
      setError(error.response?.data?.detail || 'Failed to create task');
    }
  };

  const handleUpdateTask = async () => {
    if (!selectedTask) return;
    try {
      await tasksAPI.updateTask(selectedTask.id, taskUpdate);
      setShowUpdateModal(false);
      setSelectedTask(null);
      loadTasks();
    } catch (error: any) {
      console.error('Failed to update task:', error);
      setError(error.response?.data?.detail || 'Failed to update task');
    }
  };

  const handleEscalateTask = async () => {
    if (!selectedTask) return;
    try {
      await tasksAPI.escalateTask(selectedTask.id, escalationReason);
      setShowEscalateModal(false);
      setSelectedTask(null);
      setEscalationReason('');
      loadTasks();
    } catch (error: any) {
      console.error('Failed to escalate task:', error);
      setError(error.response?.data?.detail || 'Failed to escalate task');
    }
  };

  const openUpdateModal = (task: Task) => {
    setSelectedTask(task);
    setTaskUpdate({
      status: task.status,
      progress_percentage: task.progress_percentage,
    });
    setShowUpdateModal(true);
  };

  const openEscalateModal = (task: Task) => {
    setSelectedTask(task);
    setShowEscalateModal(true);
  };

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case TaskStatus.IN_PROGRESS:
        return <Clock className="w-5 h-5 text-blue-500" />;
      case TaskStatus.BLOCKED:
        return <XCircle className="w-5 h-5 text-red-500" />;
      case TaskStatus.REVIEW:
        return <MessageSquare className="w-5 h-5 text-purple-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case TaskStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-800';
      case TaskStatus.BLOCKED:
        return 'bg-red-100 text-red-800';
      case TaskStatus.REVIEW:
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return 'bg-red-100 text-red-800';
      case TaskPriority.HIGH:
        return 'bg-orange-100 text-orange-800';
      case TaskPriority.MEDIUM:
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const canCreateTask = user.role.hierarchy_level <= 4;
  const myTasks = tasks.filter(t => t.assigned_to_id === user.id);
  const escalatedTasks = tasks.filter(t => t.is_escalated);

  if (loading) {
    return <LoadingSpinner text="Loading tasks..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-600 mt-1">Manage and track tasks</p>
        </div>
        {canCreateTask && (
          <button
            onClick={() => { setShowCreateModal(true); setError(''); }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Create Task
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError('')} className="text-red-500 hover:text-red-700 ml-4 font-bold">&times;</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">My Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{myTasks.length}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">
                {tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length}
              </p>
            </div>
            <Clock className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Escalated</p>
              <p className="text-2xl font-bold text-gray-900">{escalatedTasks.length}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as TaskStatus | '')}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Status</option>
            <option value={TaskStatus.ASSIGNED}>Assigned</option>
            <option value={TaskStatus.IN_PROGRESS}>In Progress</option>
            <option value={TaskStatus.BLOCKED}>Blocked</option>
            <option value={TaskStatus.REVIEW}>Review</option>
            <option value={TaskStatus.COMPLETED}>Completed</option>
          </select>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={assignedToMe}
              onChange={(e) => setAssignedToMe(e.target.checked)}
              className="rounded"
            />
            Assigned to me
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={escalatedOnly}
              onChange={(e) => setEscalatedOnly(e.target.checked)}
              className="rounded"
            />
            Escalated only
          </label>
        </div>
      </div>

      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
            <p className="text-gray-500">No tasks found</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(task.status)}
                    <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                    {task.is_escalated && (
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
                        ESCALATED
                      </span>
                    )}
                  </div>
                  {task.description && (
                    <p className="text-gray-600 mb-3">{task.description}</p>
                  )}
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(task.priority)}`}>
                      {task.priority.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">
                      {task.department}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>Progress: {task.progress_percentage}%</span>
                    {task.due_date && (
                      <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                    )}
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${task.progress_percentage}%` }}
                    />
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {task.assigned_to_id === user.id && (
                    <>
                      <button
                        onClick={() => openUpdateModal(task)}
                        className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Update
                      </button>
                      {!task.is_escalated && task.status !== TaskStatus.COMPLETED && (
                        <button
                          onClick={() => openEscalateModal(task)}
                          className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                        >
                          Escalate
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Create New Task</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., NBA Documentation"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                  placeholder="Task details..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Assign To *</label>
                  <select
                    value={newTask.assigned_to_id}
                    onChange={(e) => setNewTask({ ...newTask, assigned_to_id: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value={0}>Select user...</option>
                    {users
                      .filter(u => u.role.hierarchy_level >= user.role.hierarchy_level)
                      .map(u => (
                        <option key={u.id} value={u.id}>
                          {u.full_name} ({u.role.role_name})
                        </option>
                      ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                  <input
                    type="text"
                    value={newTask.department}
                    onChange={(e) => setNewTask({ ...newTask, department: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select
                    value={newTask.priority}
                    onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as TaskPriority })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value={TaskPriority.LOW}>Low</option>
                    <option value={TaskPriority.MEDIUM}>Medium</option>
                    <option value={TaskPriority.HIGH}>High</option>
                    <option value={TaskPriority.URGENT}>Urgent</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    value={newTask.task_type}
                    onChange={(e) => setNewTask({ ...newTask, task_type: e.target.value as TaskType })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value={TaskType.DEPARTMENT}>Department</option>
                    <option value={TaskType.CROSS_DEPARTMENT}>Cross Department</option>
                    <option value={TaskType.INSTITUTE_WIDE}>Institute Wide</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                <input
                  type="datetime-local"
                  value={newTask.due_date}
                  onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateTask}
                disabled={!newTask.title || !newTask.assigned_to_id}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
              >
                Create Task
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {showUpdateModal && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Update Task</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={taskUpdate.status}
                  onChange={(e) => setTaskUpdate({ ...taskUpdate, status: e.target.value as TaskStatus })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value={TaskStatus.ASSIGNED}>Assigned</option>
                  <option value={TaskStatus.IN_PROGRESS}>In Progress</option>
                  <option value={TaskStatus.REVIEW}>Review</option>
                  <option value={TaskStatus.COMPLETED}>Completed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Progress: {taskUpdate.progress_percentage}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={taskUpdate.progress_percentage}
                  onChange={(e) => setTaskUpdate({ ...taskUpdate, progress_percentage: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleUpdateTask}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Update
              </button>
              <button
                onClick={() => setShowUpdateModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {showEscalateModal && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Escalate Task</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Escalation *</label>
                <textarea
                  value={escalationReason}
                  onChange={(e) => setEscalationReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={4}
                  placeholder="Explain why this task needs to be escalated..."
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleEscalateTask}
                disabled={escalationReason.length < 10}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300"
              >
                Escalate
              </button>
              <button
                onClick={() => setShowEscalateModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
