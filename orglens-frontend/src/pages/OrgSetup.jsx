import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Building2, AlertCircle } from 'lucide-react'
import { createOrganization, getOrganization } from '../api'
import { PageHeader, AnalyzeButton, AlertBox } from '../components/Shared'

export default function OrgSetup() {
  const { orgId } = useParams()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(!!orgId)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    size_estimate: '',
    mission_statement: '',
  })

  useEffect(() => {
    if (orgId) {
      loadOrganization()
    }
  }, [orgId])

  async function loadOrganization() {
    try {
      const data = await getOrganization(orgId)
      setFormData(data)
    } catch (err) {
      setError('Failed to load organization')
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!formData.name.trim()) {
      setError('Organization name is required')
      return
    }

    setSaving(true)
    setError('')
    
    try {
      const result = await createOrganization({
        name: formData.name,
        industry: formData.industry || null,
        size_estimate: formData.size_estimate ? parseInt(formData.size_estimate) : null,
        mission_statement: formData.mission_statement || null,
      })

      navigate(`/org/${result.id}/upload`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save organization')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-maroon-600 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-neutral-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-maroon-100/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-neutral-100/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-3xl mx-auto px-6 py-12">
        {/* Back Button */}
        <button
          onClick={() => navigate('/organizations')}
          className="group mb-8 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-neutral-600 hover:text-maroon-600 hover:bg-maroon-50 transition-all duration-300 shadow-neo-sm"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
          Back to Organizations
        </button>

        <PageHeader
          icon="🏢"
          title={orgId ? 'Edit' : 'Create'}
          highlight="Organization"
          subtitle={orgId 
            ? 'Update your organization details and settings.' 
            : 'Set up a new organization to analyze. You can connect data sources next.'
          }
        />

        {error && (
          <AlertBox type="error" title="Error" message={error} />
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Organization Name */}
          <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
            <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
              <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                1️⃣
              </div>
              <h3 className="font-bold text-lg text-neutral-900">Organization Name</h3>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-semibold text-neutral-700">
                Organization Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., TechCorp Inc, StartUp XYZ"
                className="input-field"
                required
              />
              <p className="text-xs text-neutral-500">This will be the main identifier for your analysis</p>
            </div>
          </div>

          {/* Organization Details */}
          <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
            <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
              <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                2️⃣
              </div>
              <h3 className="font-bold text-lg text-neutral-900">Organization Details</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-neutral-700">
                  Industry
                </label>
                <input
                  type="text"
                  value={formData.industry}
                  onChange={e => setFormData({ ...formData, industry: e.target.value })}
                  placeholder="e.g., Technology, Finance, Healthcare"
                  className="input-field"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-neutral-700">
                  Employee Count
                </label>
                <input
                  type="number"
                  value={formData.size_estimate}
                  onChange={e => setFormData({ ...formData, size_estimate: e.target.value })}
                  placeholder="e.g., 150"
                  className="input-field"
                  min="1"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-neutral-700">
                Mission Statement
              </label>
              <textarea
                value={formData.mission_statement}
                onChange={e => setFormData({ ...formData, mission_statement: e.target.value })}
                placeholder="What is your organization's mission and stated values?"
                className="input-field resize-none"
                rows={4}
              />
              <p className="text-xs text-neutral-500">This helps identify alignment between claims and reality</p>
            </div>
          </div>

          {/* Info Box */}
          <AlertBox 
            type="info"
            title="What happens next?"
            message="After creating your organization, you'll upload communication data (Slack, Gmail, or CSV files) and run the analysis to generate insights."
          />

          {/* Submit Button */}
          <AnalyzeButton
            onClick={() => {}} // Form will handle submission
            loading={saving}
            label={orgId ? 'Update Organization' : 'Create Organization'}
            icon="✓"
          />
        </form>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        div {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  )
}
