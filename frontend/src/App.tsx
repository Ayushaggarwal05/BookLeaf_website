import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Navbar } from './components/common/Navbar';
import { AdminNavbar } from './components/admin/AdminNavbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { BooksPage } from './pages/BooksPage';
import { TicketsPage } from './pages/TicketsPage';
import { NewTicketPage } from './pages/NewTicketPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage';
import { AdminTicketsPage } from './pages/admin/AdminTicketsPage';
import { AdminTicketDetailPage } from './pages/admin/AdminTicketDetailPage';

const CURRENT_YEAR = new Date().getFullYear();

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const isAdmin = user?.role === 'admin';

  return (
    <div className="min-h-screen bg-cream-50 text-gray-900 flex flex-col font-sans selection:bg-brand-100 selection:text-brand-900">
      {isAuthenticated && (isAdmin ? <AdminNavbar /> : <Navbar />)}
      
      <main className="flex-1 pb-16">
        {children}
      </main>

      {isAuthenticated && (
        <footer className="border-t border-cream-300 bg-white py-6 text-center text-xs text-gray-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-brand-950">BookLeaf Publishing</span>
              <span>•</span>
              <span>{isAdmin ? 'Staff Operations Console' : 'Author Support & Royalties Portal'}</span>
            </div>
            <div className="text-gray-400 text-[11px]">
              Role-Based Tenant Isolation Active • © {CURRENT_YEAR} BookLeaf. All rights reserved.
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            {/* Public authentication route */}
            <Route path="/login" element={<LoginPage />} />

            {/* Author Portal Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute allowedRoles={['author']}>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/books"
              element={
                <ProtectedRoute allowedRoles={['author']}>
                  <BooksPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tickets"
              element={
                <ProtectedRoute allowedRoles={['author']}>
                  <TicketsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tickets/new"
              element={
                <ProtectedRoute allowedRoles={['author']}>
                  <NewTicketPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tickets/:ticketId"
              element={
                <ProtectedRoute allowedRoles={['author']}>
                  <TicketDetailPage />
                </ProtectedRoute>
              }
            />

            {/* Admin Portal Protected Routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/tickets"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminTicketsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/tickets/:ticketId"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminTicketDetailPage />
                </ProtectedRoute>
              }
            />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
