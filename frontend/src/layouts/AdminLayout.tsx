import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { LogOut, LayoutDashboard, Map as MapIcon, User, Layers, History, CreditCard, FileText, Zap } from 'lucide-react';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex flex-col">
                <div className="h-16 border-b flex items-center px-6">
                    <Link to="/" className="flex items-center gap-2">
                        <img src="/logo.png" alt="Voltuj.cz" className="h-8 w-auto" />
                    </Link>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/admin/dashboard" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        <LayoutDashboard size={20} /> Dashboard
                    </Link>
                    <Link to="/map" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        <MapIcon size={20} /> Map
                    </Link>

                    {/* ADMIN NAVIGATION */}
                    {user?.role === 'admin' && (
                        <>
                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                Users
                            </div>
                            <Link to="/admin/users" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <User size={20} /> All Users
                            </Link>
                            <Link to="/admin/profile" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <User size={20} /> My Profile
                            </Link>

                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                Chargers
                            </div>
                            <Link to="/admin/all-chargers" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <Layers size={20} /> All Chargers
                            </Link>
                            <Link to="/admin/all-logs" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <History size={20} /> Charge Logs
                            </Link>

                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                RFID
                            </div>
                            <Link to="/admin/cards" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <CreditCard size={20} /> All Cards
                            </Link>
                        </>
                    )}

                    {/* USER & OWNER NAVIGATION */}
                    {user?.role !== 'admin' && (
                        <>
                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                User
                            </div>
                            <Link to="/admin/cards" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <CreditCard size={20} /> RFID Cards
                            </Link>
                            <Link to="/admin/history?view=my_charges" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <History size={20} /> Charging History
                            </Link>
                            <Link to="/admin/profile" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <User size={20} /> Profile
                            </Link>
                        </>
                    )}

                    {/* BECOME OWNER LINK (For basic users) */}
                    {user?.role === 'user' && (
                        <>
                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                Owner Section
                            </div>
                            <Link to="/admin/become-owner" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <Zap size={20} /> Become an Owner
                            </Link>
                        </>
                    )}

                    {/* OWNER ONLY */}
                    {user?.role === 'owner' && (
                        <>
                            <div className="pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                Owner
                            </div>
                            <Link to="/admin/chargers" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <Layers size={20} /> My Chargers
                            </Link>
                            <Link to="/admin/history?view=charger_logs" className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                                <FileText size={20} /> Charger Usage
                            </Link>
                        </>
                    )}
                </nav>

                <div className="p-4 border-t">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                            {user?.name?.[0]?.toUpperCase()}
                        </div>
                        <div className="overflow-hidden">
                            <p className="text-sm font-medium truncate">{user?.name}</p>
                            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                        </div>
                    </div>
                    <Button variant="outline" className="w-full flex items-center gap-2" onClick={handleLogout}>
                        <LogOut size={16} /> Logout
                    </Button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
                {children}
            </main>
        </div >
    );
}
