import { Outlet, Link, useLocation } from 'react-router-dom';
import { FileText, Upload, MessageSquare, GraduationCap, Home } from 'lucide-react';
import { cn } from '../lib/utils';

const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Upload', href: '/upload', icon: Upload },
    { name: 'Summarize', href: '/summarize', icon: FileText },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Flashcards', href: '/flashcards', icon: GraduationCap },
];

export default function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="flex items-center space-x-2">
                            <GraduationCap className="h-8 w-8 text-primary" />
                            <h1 className="text-2xl font-bold">SummarizerAI</h1>
                        </Link>
                        <nav className="hidden md:flex space-x-1">
                            {navigation.map((item) => {
                                const Icon = item.icon;
                                const isActive = location.pathname === item.href;
                                return (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        className={cn(
                                            'flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                                            isActive
                                                ? 'bg-primary text-primary-foreground'
                                                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        <span>{item.name}</span>
                                    </Link>
                                );
                            })}
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="border-t mt-auto">
                <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
                    <p>© 2026 SummarizerAI. Powered by Deep Learning.</p>
                </div>
            </footer>
        </div>
    );
}
