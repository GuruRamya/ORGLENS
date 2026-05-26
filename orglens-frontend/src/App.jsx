import { Routes, Route, useParams } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Organizations from './pages/Organizations'
import OrgSetup from './pages/OrgSetup'
import DataUpload from './pages/DataUpload'
import Analysis from './pages/Analysis'
import Dashboard from './pages/Dashboard'
import Auth from './pages/Auth'
import { isAuthenticated } from './lib/auth'
import { Navigate } from 'react-router-dom'
import DeepDiveModal from './pages/DeepDiveModal'
import DemoPage from './pages/DemoPage'

const DEMO_ORG_ID = import.meta.env.VITE_DEMO_ORG_ID
const DEMO_ANALYSIS_ID = import.meta.env.VITE_DEMO_ANALYSIS_ID

function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />
}

function DashboardRoute() {
  const { orgId, analysisId } = useParams()
  const isDemoOrg =
    String(orgId) === String(DEMO_ORG_ID) &&
    String(analysisId) === String(DEMO_ANALYSIS_ID)
  
  if (!isDemoOrg && !isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  
  return <Dashboard isDemoOrg={isDemoOrg} />
}

function DeepDiveRoute() {
  const { orgId, analysisId } = useParams()
  const isDemoOrg =
    String(orgId) === String(DEMO_ORG_ID) &&
    String(analysisId) === String(DEMO_ANALYSIS_ID)
  
  if (!isDemoOrg && !isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  
  return <DeepDiveModal isDemoOrg={isDemoOrg} />
}

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <Routes>
        {/* Public routes — no login needed */}
        <Route path="/login" element={<Auth mode="login" />} />
        <Route path="/register" element={<Auth mode="register" />} />
        <Route path="/" element={<Home />} />
        <Route path="/demo" element={<DemoPage />} />

        {/* Dashboard routes — public for demo, protected for user orgs */}
        <Route path="/org/:orgId/dashboard/:analysisId" element={<DashboardRoute />} />
        <Route path="/org/:orgId/dashboard/:analysisId/deep-dive" element={<DeepDiveRoute />} />

        {/* Protected routes — login required */}
        <Route path="/organizations" element={<ProtectedRoute><Organizations /></ProtectedRoute>} />
        <Route path="/org/new" element={<ProtectedRoute><OrgSetup /></ProtectedRoute>} />
        <Route path="/org/:orgId/setup" element={<ProtectedRoute><OrgSetup /></ProtectedRoute>} />
        <Route path="/org/:orgId/upload" element={<ProtectedRoute><DataUpload /></ProtectedRoute>} />
        <Route path="/org/:orgId/analysis" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
        <Route path="/org/:orgId/analysis/:analysisId" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
      </Routes>
    </div>
  )
}
