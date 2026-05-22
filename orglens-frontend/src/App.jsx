import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Organizations from './pages/Organizations'
import Orgsetup from './pages/OrgSetup'
import DataUpload from './pages/DataUpload'
import Analysis from './pages/Analysis'
import Dashboard from './pages/Dashboard'
import Auth from './pages/Auth'
import { isAuthenticated } from './lib/auth'
import { Navigate } from 'react-router-dom'
import DeepDiveModal from './pages/DeepDiveModal'
import DemoPage from './pages/DemoPage'

function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />
}


export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <Routes>
        <Route path="/login" element={<Auth mode="login" />} />
        <Route path="/register" element={<Auth mode="register" />} />
        <Route path="/" element={<Home />} />
        <Route path="/organizations" element={<ProtectedRoute><Organizations /></ProtectedRoute>} />
        <Route path="/org/new" element={<ProtectedRoute><OrgSetup /></ProtectedRoute>} />
        <Route path="/org/:orgId/setup" element={<ProtectedRoute><OrgSetup /></ProtectedRoute>} />
        <Route path="/org/:orgId/upload" element={<ProtectedRoute><DataUpload /></ProtectedRoute>} />
        <Route path="/org/:orgId/analysis" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
        <Route path="/org/:orgId/analysis/:analysisId" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
        <Route path="/org/:orgId/dashboard/:analysisId" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/org/:orgId/dashboard/:analysisId/deep-dive" element={<ProtectedRoute><DeepDiveModal /></ProtectedRoute>} />
        <Route path="/demo" element={<DemoPage />} />      
      </Routes>
    </div>
  )
}
