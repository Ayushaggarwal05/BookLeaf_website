import React from 'react';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { LoadingSpinner } from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: ('author' | 'admin')[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  allowedRoles = ['author'] 
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-cream-50 flex flex-col items-center justify-center p-4">
        <LoadingSpinner size="lg" message="Validating BookLeaf session..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role authorization
  if (user && !allowedRoles.includes(user.role as 'author' | 'admin')) {
    // If admin tried to visit author route, redirect seamlessly to admin portal
    if (user.role === 'admin' && !allowedRoles.includes('admin')) {
      return <Navigate to="/admin" replace />;
    }

    // If author tried to visit admin route, show access denied
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-white p-8 rounded-xl shadow-soft border border-rose-200 max-w-md">
          <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-700 flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-serif font-bold text-gray-900 mb-2">
            Administrative Access Restricted
          </h2>
          <p className="text-xs text-gray-600 mb-6 leading-relaxed">
            Your account ({user.email}) is registered with author privileges. Access to administrative queues and confidential publishing operations is restricted to BookLeaf staff.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-700 hover:bg-brand-800 text-white font-medium text-xs rounded-lg shadow-soft transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Author Portal</span>
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
