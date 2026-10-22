import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { BookOpen, LifeBuoy, PlusCircle, LayoutDashboard, LogOut, Menu, X, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'My Books', path: '/books', icon: BookOpen },
    { name: 'Support Queries', path: '/tickets', icon: LifeBuoy },
    { name: 'Submit Query', path: '/tickets/new', icon: PlusCircle },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-white border-b border-cream-300 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-lg bg-brand-700 flex items-center justify-center text-white shadow-soft group-hover:bg-brand-800 transition">
                <BookOpen className="w-5 h-5 text-brand-100" />
              </div>
              <div>
                <span className="font-serif text-lg font-bold tracking-tight text-brand-950 block leading-tight">
                  BookLeaf
                </span>
                <span className="text-[10px] tracking-wider uppercase font-semibold text-brand-600 block">
                  Author Support Portal
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
                    className={`inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium rounded-lg transition ${
                      active
                        ? 'bg-brand-50 text-brand-900 font-semibold'
                        : 'text-gray-600 hover:text-brand-900 hover:bg-cream-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-brand-700' : 'text-gray-400'}`} />
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* User profile & Logout */}
          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-cream-100 border border-cream-300 text-xs text-brand-950">
              <div className="w-6 h-6 rounded-full bg-brand-200 text-brand-800 flex items-center justify-center font-bold">
                <UserIcon className="w-3.5 h-3.5" />
              </div>
              <span className="font-medium text-gray-800">{user?.full_name}</span>
              {user?.author_id && (
                <span className="px-1.5 py-0.5 rounded bg-white text-[11px] font-mono text-brand-700 border border-cream-300 font-semibold">
                  {user.author_id}
                </span>
              )}
            </div>

            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-rose-700 hover:bg-rose-50 px-2.5 py-1.5 rounded-md transition"
              title="Sign out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign out</span>
            </button>
          </div>

          {/* Mobile hamburger button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-brand-900 hover:bg-cream-100"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-cream-200 bg-cream-50 px-4 pt-3 pb-4 space-y-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = isActive(link.path);
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg font-medium ${
                  active ? 'bg-brand-100 text-brand-900 font-bold' : 'text-gray-700 hover:bg-cream-200'
                }`}
              >
                <Icon className="w-5 h-5 text-brand-600" />
                {link.name}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-cream-200 flex items-center justify-between">
            <div className="text-xs text-gray-600">
              <span className="font-semibold block text-brand-900">{user?.full_name}</span>
              <span>{user?.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1 text-xs text-rose-700 font-medium px-2 py-1 rounded bg-rose-50 border border-rose-200"
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
