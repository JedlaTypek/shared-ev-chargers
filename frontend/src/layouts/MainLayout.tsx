import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';

export default function MainLayout() {
    const { isAuthenticated, user } = useAuth();

    return (
        <div className="flex flex-col h-screen">
            <header className="h-16 border-b flex items-center justify-between px-6 bg-white z-10 relative shadow-sm">
                <Link to="/" className="flex items-center gap-2">
                    <img src="/logo.png" alt="Voltuj.cz" className="h-10 w-auto" />
                </Link>

                <nav className="flex items-center gap-4">
                    {isAuthenticated ? (
                        <Link to="/admin/dashboard">
                            <Button>Dashboard ({user?.name})</Button>
                        </Link>
                    ) : (
                        <>
                            <Link to="/login">
                                <Button variant="ghost">Login</Button>
                            </Link>
                            <Link to="/register">
                                <Button>Register</Button>
                            </Link>
                        </>
                    )}
                </nav>
            </header>
            <main className="flex-1 relative">
                <Outlet />
            </main>
        </div>
    );
}
