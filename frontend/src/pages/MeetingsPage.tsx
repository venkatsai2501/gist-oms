import { useState, useEffect } from 'react';
import { User, Meeting, MeetingStatus, MeetingCreatePayload, Resource } from '@/types';
import { meetingsAPI } from '@/services/api';
import { Plus, Calendar, MapPin, Users, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface MeetingsPageProps {
  user: User;
}

export default function MeetingsPage({ user }: MeetingsPageProps) {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<MeetingStatus | ''>('');
  const [myMeetings, setMyMeetings] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);

  const [newMeeting, setNewMeeting] = useState<MeetingCreatePayload>({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    room_id: undefined,
    location: '',
    priority: 'medium',
    participant_ids: [],
  });

  useEffect(() => {
    loadMeetings();
    loadResources();
    loadUsers();
  }, [statusFilter, myMeetings, pendingApproval]);

  const loadMeetings = async () => {
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (myMeetings) params.my_meetings = true;
      if (pendingApproval) params.pending_approval = true;

      const data = await meetingsAPI.getMeetings(params);
      setMeetings(data);
    } catch (error) {
      console.error('Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadResources = async () => {
    try {
      const data = await meetingsAPI.getResources({ available_only: true });
      setResources(data);
    } catch (error) {
      console.error('Failed to load resources:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const handleCreateMeeting = async () => {
    try {
      await meetingsAPI.createMeeting(newMeeting);
      setShowCreateModal(false);
      setNewMeeting({
        title: '',
        description: '',
        start_time: '',
        end_time: '',
        room_id: undefined,
        location: '',
        priority: 'medium',
        participant_ids: [],
      });
      loadMeetings();
    } catch (error: any) {
      console.error('Failed to create meeting:', error);
      alert(error.response?.data?.detail || 'Failed to create meeting');
    }
  };

  const handleApproveMeeting = async (id: number) => {
    try {
      await meetingsAPI.approveMeeting(id);
      loadMeetings();
    } catch (error) {
      console.error('Failed to approve meeting:', error);
      alert('Failed to approve meeting');
    }
  };

  const handleRejectMeeting = async (id: number) => {
    try {
      await meetingsAPI.rejectMeeting(id);
      loadMeetings();
    } catch (error) {
      console.error('Failed to reject meeting:', error);
      alert('Failed to reject meeting');
    }
  };

  const toggleParticipant = (userId: number) => {
    setNewMeeting(prev => ({
      ...prev,
      participant_ids: prev.participant_ids.includes(userId)
        ? prev.participant_ids.filter(id => id !== userId)
        : [...prev.participant_ids, userId]
    }));
  };

  const toggleAllParticipants = () => {
    setNewMeeting(prev => ({
      ...prev,
      participant_ids: prev.participant_ids.length === users.length 
        ? [] 
        : users.map(u => u.id)
    }));
  };

  const getStatusIcon = (status: MeetingStatus) => {
    switch (status) {
      case MeetingStatus.APPROVED:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case MeetingStatus.REJECTED:
        return <XCircle className="w-5 h-5 text-red-500" />;
      case MeetingStatus.COMPLETED:
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: MeetingStatus) => {
    switch (status) {
      case MeetingStatus.APPROVED:
        return 'bg-green-100 text-green-800';
      case MeetingStatus.REJECTED:
        return 'bg-red-100 text-red-800';
      case MeetingStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800';
      case MeetingStatus.CANCELLED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const canApproveMeetings = user.role.hierarchy_level <= 3;
  const pendingMeetings = meetings.filter(m => m.status === MeetingStatus.PENDING);
  const upcomingMeetings = meetings.filter(m => 
    m.status === MeetingStatus.APPROVED && new Date(m.start_time) > new Date()
  );

  if (loading) {
    return <div className="text-center py-12">Loading meetings...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meetings</h1>
          <p className="text-gray-600 mt-1">Schedule and manage meetings</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Schedule Meeting
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Approval</p>
              <p className="text-2xl font-bold text-gray-900">{pendingMeetings.length}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Upcoming</p>
              <p className="text-2xl font-bold text-gray-900">{upcomingMeetings.length}</p>
            </div>
            <Calendar className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Meetings</p>
              <p className="text-2xl font-bold text-gray-900">{meetings.length}</p>
            </div>
            <Users className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-sm font-medium text-gray-700">Filters:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as MeetingStatus | '')}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Status</option>
            <option value={MeetingStatus.PENDING}>Pending</option>
            <option value={MeetingStatus.APPROVED}>Approved</option>
            <option value={MeetingStatus.REJECTED}>Rejected</option>
            <option value={MeetingStatus.COMPLETED}>Completed</option>
          </select>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={myMeetings}
              onChange={(e) => setMyMeetings(e.target.checked)}
              className="rounded"
            />
            My Meetings
          </label>
          {canApproveMeetings && (
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={pendingApproval}
                onChange={(e) => setPendingApproval(e.target.checked)}
                className="rounded"
              />
              Pending Approval
            </label>
          )}
        </div>
      </div>

      {canApproveMeetings && pendingMeetings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 font-medium">
            You have {pendingMeetings.length} meeting{pendingMeetings.length > 1 ? 's' : ''} pending approval
          </p>
        </div>
      )}

      <div className="space-y-4">
        {meetings.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
            <p className="text-gray-500">No meetings found</p>
          </div>
        ) : (
          meetings.map((meeting) => (
            <div
              key={meeting.id}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(meeting.status)}
                    <h3 className="text-lg font-semibold text-gray-900">{meeting.title}</h3>
                  </div>
                  {meeting.description && (
                    <p className="text-gray-600 mb-3">{meeting.description}</p>
                  )}
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(meeting.status)}`}>
                      {meeting.status.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded">
                      {meeting.priority.toUpperCase()}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>
                        {new Date(meeting.start_time).toLocaleString()} - {new Date(meeting.end_time).toLocaleTimeString()}
                      </span>
                    </div>
                    {meeting.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        <span>{meeting.location}</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {canApproveMeetings && meeting.status === MeetingStatus.PENDING && (
                    <>
                      <button
                        onClick={() => handleApproveMeeting(meeting.id)}
                        className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleRejectMeeting(meeting.id)}
                        className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                      >
                        Reject
                      </button>
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
          <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Schedule New Meeting</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={newMeeting.title}
                  onChange={(e) => setNewMeeting({ ...newMeeting, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Department Meeting"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newMeeting.description}
                  onChange={(e) => setNewMeeting({ ...newMeeting, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                  placeholder="Meeting agenda..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time *</label>
                  <input
                    type="datetime-local"
                    value={newMeeting.start_time}
                    onChange={(e) => setNewMeeting({ ...newMeeting, start_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time *</label>
                  <input
                    type="datetime-local"
                    value={newMeeting.end_time}
                    onChange={(e) => setNewMeeting({ ...newMeeting, end_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Venue/Room</label>
                  <select
                    value={newMeeting.room_id || ''}
                    onChange={(e) => setNewMeeting({ ...newMeeting, room_id: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Select room...</option>
                    {resources.map(r => (
                      <option key={r.id} value={r.id}>
                        {r.name} {r.capacity ? `(${r.capacity} seats)` : ''} - {r.location}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select
                    value={newMeeting.priority}
                    onChange={(e) => setNewMeeting({ ...newMeeting, priority: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location (if no room selected)</label>
                <input
                  type="text"
                  value={newMeeting.location}
                  onChange={(e) => setNewMeeting({ ...newMeeting, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Online via Zoom"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Participants *</label>
                <label className="flex items-center gap-2 py-2 px-3 bg-gray-50 border border-gray-300 rounded-t-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={users.length > 0 && newMeeting.participant_ids.length === users.length}
                    onChange={toggleAllParticipants}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Select All
                  </span>
                </label>
                <div className="border border-gray-300 border-t-0 rounded-b-lg p-3 max-h-48 overflow-y-auto">
                  {users.map(u => (
                    <label key={u.id} className="flex items-center gap-2 py-2 hover:bg-gray-50 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newMeeting.participant_ids.includes(u.id)}
                        onChange={() => toggleParticipant(u.id)}
                        className="rounded"
                      />
                      <span className="text-sm">
                        {u.full_name} ({u.role.role_name}) - {u.department}
                      </span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {newMeeting.participant_ids.length} participant{newMeeting.participant_ids.length !== 1 ? 's' : ''} selected
                </p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateMeeting}
                disabled={!newMeeting.title || !newMeeting.start_time || !newMeeting.end_time || newMeeting.participant_ids.length === 0}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
              >
                Schedule Meeting
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
    </div>
  );
}
