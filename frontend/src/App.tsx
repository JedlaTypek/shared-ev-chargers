import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/auth/Login';
import RegisterPage from './pages/auth/Register';
import MainLayout from './layouts/MainLayout';
import AdminLayout from './layouts/AdminLayout';
import PublicMap from './pages/public/Map';
import CardsPage from './pages/admin/Cards';
import HistoryPage from './pages/admin/History';
import ProfilePage from './pages/admin/Profile';
import ChargersPage from './pages/admin/Chargers';
import UsersPage from './pages/admin/Users';
import BecomeOwnerPage from './pages/user/BecomeOwner';

// Protected Route Wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  return isAuthenticated ? <AdminLayout>{children}</AdminLayout> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="" element={<Navigate to="/map" replace />} />
          <Route path="map" element={<PublicMap />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>

        <Route path="/admin" element={<ProtectedRoute><Outlet /></ProtectedRoute>}>
          <Route path="dashboard" element={<div><h1>Analytics Dashboard</h1><p>Welcome back!</p></div>} />
          <Route path="users" element={<UsersPage />} />
          <Route path="cards" element={<CardsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="chargers" element={<ChargersPage />} />
          <Route path="all-chargers" element={<ChargersPage mode="all" />} />
          <Route path="all-logs" element={<HistoryPage />} />
          <Route path="become-owner" element={<BecomeOwnerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
