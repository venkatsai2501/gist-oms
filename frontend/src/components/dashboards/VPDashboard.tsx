import { useEffect, useState } from 'react';
import { AlertTriangle, Clock, Calendar, TrendingUp } from 'lucide-react';
import { reportsAPI } from '@/services/api';
import type { DashboardData } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function VPDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsAPI.getDashboardData()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading dashboard..." />;
  if (!data) return <div className="text-center py-12">Failed to load dashboard data</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Vice Principal Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Cross-department coordination and oversight</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Tasks</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">{data.total_tasks}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Escalated Tasks</p>
              <p className="text-3xl font-bold text-orange-600 mt-1">{data.escalated_tasks}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Overdue Tasks</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{data.overdue_tasks}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending Meetings</p>
              <p className="text-3xl font-bold text-purple-600 mt-1">{data.pending_meetings}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Task Status Distribution</h2>
        <div className="space-y-3">
          {data.task_by_status && Object.entries(data.task_by_status).map(([status, count]) => (
            <div key={status} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">{status.replace('_', ' ')}</span>
              <span className="text-2xl font-bold text-blue-600">{count as number}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
