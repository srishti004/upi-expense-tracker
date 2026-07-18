import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './components/AppLayout'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import LandingPage from './pages/LandingPage'
import { DashboardPage, TransactionsPage, ParsePage, BudgetsPage } from './pages/index.jsx'

function ProtectedLayout({ children }) {
  return (
    <ProtectedRoute>
      <AppLayout>{children}</AppLayout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Landing */}
          <Route path="/" element={<LandingPage />} />

          {/* Public */}
          <Route path="/login"  element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected */}
          <Route path="/dashboard"    element={<ProtectedLayout><DashboardPage /></ProtectedLayout>} />
          <Route path="/transactions" element={<ProtectedLayout><TransactionsPage /></ProtectedLayout>} />
          <Route path="/parse"        element={<ProtectedLayout><ParsePage /></ProtectedLayout>} />
          <Route path="/budgets"      element={<ProtectedLayout><BudgetsPage /></ProtectedLayout>} />

          {/* Default */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}