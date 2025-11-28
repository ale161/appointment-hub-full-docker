import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/contexts/AuthContext'
import { Toaster } from '@/components/ui/sonner'

// Layout components
import Layout from '@/components/Layout'
import PublicLayout from '@/components/PublicLayout'

// Public pages
import HomePage from '@/pages/HomePage'
import StorePage from '@/pages/StorePage'
import BookingPage from '@/pages/BookingPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'

// Protected pages
import DashboardPage from '@/pages/DashboardPage'
import BookingsPage from '@/pages/BookingsPage'
import ServicesPage from '@/pages/ServicesPage'
import StoreManagementPage from '@/pages/StoreManagementPage'
import SubscriptionPage from '@/pages/SubscriptionPage'
import ProfilePage from '@/pages/ProfilePage'
import AdminPage from '@/pages/AdminPage'
import AnalyticsPage from '@/pages/AnalyticsPage'

// Components
import ProtectedRoute from '@/components/ProtectedRoute'

import './App.css'

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="appointment-hub-theme">
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<PublicLayout />}>
                <Route index element={<HomePage />} />
                <Route path="stores/:storeSlug" element={<StorePage />} />
                <Route path="stores/:storeSlug/book/:serviceId" element={<BookingPage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
              </Route>

              {/* Protected routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<DashboardPage />} />
                <Route path="bookings" element={<BookingsPage />} />
                <Route path="services" element={<ServicesPage />} />
                <Route path="store" element={<StoreManagementPage />} />
                <Route path="subscription" element={<SubscriptionPage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="analytics" element={<AnalyticsPage />} />
                <Route path="admin" element={
                  <ProtectedRoute requiredRole="admin">
                    <AdminPage />
                  </ProtectedRoute>
                } />
              </Route>

              {/* Redirect unknown routes */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

