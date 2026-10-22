import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Inbox, 
  LayoutDashboard, 
  LogOut, 
  Menu, 
  X, 
  User as UserIcon
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const AdminNavbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { name: 'Operations Overview', path: '/admin', icon: LayoutDashboard },
    { name: 'Ticket Queue', path: '/admin/tickets', icon: Inbox },
  ];

  const isActive = (path: string) => {
    if (path === '/admin') {
      return location.pathname === '/admin';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-brand-950 text-white border-b border-brand-900 sticky top-0 z-40 shadow-soft">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/admin" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-soft group-hover:bg-emerald-500 transition">
                <ShieldCheck className="w-5 h-5 text-emerald-100" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-serif text-lg font-bold tracking-tight text-white block leading-tight">
                    BookLeaf
                  </span>
                  <span className="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono uppercase font-bold rounded">
                    Admin
                  </span>
                </div>
                <span className="text-[10px] tracking-wider uppercase font-semibold text-brand-300 block">
                  Support & Operations Console
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex ml-10 space-x-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const active = isActive(link.path);
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg transition ${
                      active
                        ? 'bg-brand-900 text-white shadow-inner border border-brand-800'
                        : 'text-brand-200 hover:text-white hover:bg-brand-900/60'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-emerald-400' : 'text-brand-300'}`} />
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* User profile & Logout */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-brand-900 border border-brand-800 text-xs text-white">
              <div className="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold">
                <UserIcon className="w-3.5 h-3.5" />
              </div>
              <span className="font-medium text-brand-100">{user?.full_name}</span>
              <span className="px-1.5 py-0.5 rounded bg-brand-800 text-[10px] font-mono text-emerald-300 border border-brand-700 font-semibold uppercase">
                Staff
              </span>
            </div>

            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-brand-300 hover:text-rose-300 hover:bg-rose-950/40 px-2.5 py-1.5 rounded-md transition"
              title="Sign out of Admin Console"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign out</span>
            </button>
          </div>

          {/* Mobile hamburger button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-brand-300 hover:text-white hover:bg-brand-900"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-brand-900 bg-brand-950 px-4 pt-3 pb-4 space-y-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.path);
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 text-xs rounded-lg font-medium ${
                  active ? 'bg-brand-900 text-white font-bold' : 'text-brand-200 hover:bg-brand-900'
                }`}
              >
                <Icon className="w-5 h-5 text-emerald-400" />
                {link.name}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-brand-900 flex items-center justify-between">
            <div className="text-xs text-brand-200">
              <span className="font-semibold block text-white">{user?.full_name}</span>
              <span className="text-[11px] text-brand-400">{user?.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1 text-xs text-rose-300 font-medium px-2 py-1 rounded bg-rose-950/60 border border-rose-900"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};
