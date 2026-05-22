import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { triggerAnalysis, getAnalysisStatus, listAnalyses, getOrganization } from '../api'
import { PageHeader, AnalyzeButton, AlertBox } from '../components/Shared'

export default function Analysis() {
  const { orgId } = useParams()
  const navigate = useNavigate()

  const [org, setOrg] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyses, setAnalyses] = useState([])
  const [currentAnalysis, setCurrentAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')

  // Bug 3 fix: ref so the interval closure always sees latest value
  const currentAnalysisRef = useRef(null)

  function setCurrentAnalysisAndRef(data) {
    currentAnalysisRef.current = data
    setCurrentAnalysis(data)
  }

  useEffect(() => {
    loadData()
    const interval = setInterval(pollAnalysisStatus, 2000)
    return () => clearInterval(interval)
  }, [orgId])

  async function loadData() {
    try {
      const [orgData, analysesData] = await Promise.all([
        getOrganization(orgId),
        listAnalyses(orgId),
      ])
      setOrg(orgData)
      const list = Array.isArray(analysesData) ? analysesData : analysesData.analyses || []
      setAnalyses(list)

      const pending = list.find(a => a.status === 'processing' || a.status === 'queued')
      if (pending) {
        setCurrentAnalysisAndRef(pending)
      }
    } catch (err) {
      setError('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  // Bug 2 + 3 fix: use ref, handle both id and analysis_id field names
  async function pollAnalysisStatus() {
    if (!currentAnalysisRef.current) return

    const id = currentAnalysisRef.current.analysis_id || currentAnalysisRef.current.id
    if (!id) return

    try {
      const status = await getAnalysisStatus(id)
      setCurrentAnalysisAndRef(status)

      if (status.status === 'completed') {
        const analysisId = status.id || status.analysis_id
        setAnalyses(prev => prev.map(a =>
          (a.analysis_id || a.id) === analysisId ? status : a
        ))
        setTimeout(() => {
          navigate(`/org/${orgId}/dashboard/${analysisId}`)
        }, 2000)
      } else if (status.status === 'failed') {
        setError(`Analysis failed: ${status.message || 'Unknown error'}`)
        setCurrentAnalysisAndRef(null)
      }
    } catch (err) {
      console.error('Poll error:', err)
    }
  }

  async function handleTriggerAnalysis() {
    setAnalyzing(true)
    setError('')

    try {
      const result = await triggerAnalysis(orgId)
      setCurrentAnalysisAndRef(result)  // Bug 3 fix: use the ref setter
      setAnalyzing(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to trigger analysis')
      setAnalyzing(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-[400px]" />
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="text-green-600" size={20} />
      case 'processing': return <div className="animate-spin"><Clock className="text-maroon-600" size={20} /></div>
      case 'failed': return <AlertCircle className="text-red-600" size={20} />
      default: return <Clock className="text-neutral-500" size={20} />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-50 border-green-200 text-green-700'
      case 'processing': return 'bg-blue-50 border-blue-200 text-blue-700'
      case 'failed': return 'bg-red-50 border-red-200 text-red-700'
      default: return 'bg-neutral-50 border-neutral-200 text-neutral-700'
    }
  }

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-maroon-100/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-neutral-100/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-4xl mx-auto px-6 py-12">
        <button
          onClick={() => navigate('/organizations')}
          className="group mb-8 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-neutral-600 hover:text-maroon-600 hover:bg-maroon-50 transition-all duration-300 shadow-neo-sm"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
          Back to Organizations
        </button>

        <PageHeader
          icon="🔍"
          title="Run"
          highlight="Analysis"
          subtitle={`For ${org?.name || 'your organization'} — Start analyzing communication patterns and organizational dynamics.`}
        />

        <div className="space-y-6">
          {currentAnalysis && (
            <div className={`rounded-2xl border p-8 ${getStatusColor(currentAnalysis.status)} shadow-neo-md`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(currentAnalysis.status)}
                  <div>
                    <p className="font-bold text-lg capitalize">{currentAnalysis.status}</p>
                    <p className="text-sm mt-1">
                      {currentAnalysis.status === 'completed' && 'Analysis complete! Redirecting to dashboard...'}
                      {currentAnalysis.status === 'processing' && `${currentAnalysis.progress || 0}% complete`}
                      {currentAnalysis.status === 'failed' && (currentAnalysis.message || 'Analysis failed')}
                      {currentAnalysis.status === 'queued' && 'Waiting to start...'}
                    </p>
                  </div>
                </div>
              </div>

              {currentAnalysis.status === 'processing' && (
                <div className="mt-4">
                  <div className="w-full h-2 rounded-full bg-neutral-300 overflow-hidden">
                    <div
                      className="h-full bg-maroon-600 transition-all duration-500"
                      style={{ width: `${currentAnalysis.progress || 0}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {(!currentAnalysis || currentAnalysis.status === 'failed') && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                  🚀
                </div>
                <h3 className="font-bold text-lg text-neutral-900">Start New Analysis</h3>
              </div>
              <p className="text-neutral-600 text-sm mb-6">
                This will analyze all uploaded communication data and generate comprehensive insights.
              </p>
              <AnalyzeButton
                onClick={handleTriggerAnalysis}
                loading={analyzing}
                label="Start Analysis"
                icon="🔍"
              />
            </div>
          )}

          {error && <AlertBox type="error" title="Error" message={error} />}

          {analyses.length > 0 && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                  📊
                </div>
                <h3 className="font-bold text-lg text-neutral-900">Previous Analyses</h3>
              </div>

              <div className="space-y-3">
                {analyses.map(analysis => {
                  const id = analysis.analysis_id || analysis.id
                  return (
                    <button
                      key={id}
                      onClick={() => {
                        if (analysis.status === 'completed') {
                          navigate(`/org/${orgId}/dashboard/${id}`)
                        }
                      }}
                      disabled={analysis.status !== 'completed'}
                      className={`w-full text-left p-4 rounded-xl border transition-all ${
                        analysis.status === 'completed'
                          ? 'border-green-200 bg-green-50 hover:shadow-neo-md cursor-pointer'
                          : 'border-neutral-200 bg-neutral-50 cursor-not-allowed opacity-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(analysis.status)}
                          <div>
                            <p className="font-semibold text-neutral-900">
                              {new Date(analysis.created_at).toLocaleString()}
                            </p>
                            <p className="text-sm text-neutral-600 mt-1">
                              {analysis.messages_analyzed ?? 0} messages analyzed
                            </p>
                          </div>
                        </div>
                        {analysis.status === 'completed' && (
                          <span className="text-sm font-semibold text-green-700">View →</span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {analyses.length === 0 && !currentAnalysis && (
            <AlertBox
              type="info"
              title="No analyses yet"
              message="Create your first analysis to see results. Make sure you've uploaded communication data first."
            />
          )}
        </div>
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