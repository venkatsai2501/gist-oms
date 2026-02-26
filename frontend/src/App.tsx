import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './components/layout/DashboardLayout';
import DirectorDashboard from './components/dashboards/DirectorDashboard';
import PrincipalDashboard from './components/dashboards/PrincipalDashboard';
import VPDashboard from './components/dashboards/VPDashboard';
import HODDashboard from './components/dashboards/HODDashboard';
import EmployeeDashboard from './components/dashboards/EmployeeDashboard';
import TasksPage from './pages/TasksPage';
import DocumentsPage from './pages/DocumentsPage';
import MeetingsPage from './pages/MeetingsPage';
import NotificationsPage from './pages/NotificationsPage';
import UsersPage from './pages/UsersPage';
import { authAPI } from './services/api';
import type { User } from './types';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authAPI.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('access_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  const getDashboardComponent = () => {
    if (!user) return null;
    
    switch (user.role.hierarchy_level) {
      case 1:
        return <DirectorDashboard />;
      case 2:
        return <PrincipalDashboard />;
      case 3:
        return <VPDashboard />;
      case 4:
        return <HODDashboard />;
      case 5:
        return <EmployeeDashboard />;
      default:
        return <EmployeeDashboard />;
    }
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={setUser} />
          }
        />
        {user ? (
          <Route
            path="/*"
            element={
              <DashboardLayout user={user} onLogout={() => setUser(null)}>
                <Routes>
                  <Route path="/dashboard" element={getDashboardComponent()} />
                  <Route path="/tasks" element={<TasksPage user={user} />} />
                  <Route path="/documents" element={<DocumentsPage user={user} />} />
                  <Route path="/meetings" element={<MeetingsPage user={user} />} />
                  <Route path="/users" element={<UsersPage user={user} />} />
                  <Route path="/notifications" element={<NotificationsPage />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </DashboardLayout>
            }
          />
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  );
}

export default App;
