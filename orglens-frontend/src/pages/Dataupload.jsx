import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Slack, Mail, LinkIcon } from 'lucide-react'
import { 
  uploadZip, uploadEmployeeCSV, uploadSlackExport, uploadGmailExport,
  getSlackAuthUrl, getGmailAuthUrl, syncSlackData, syncGmailData,
  getOrganizations
} from '../api'
import { PageHeader, FileDropZone, AnalyzeButton, InputMethodTabs, AlertBox } from '../components/Shared'
import { getAnalysisStatus, triggerAnalysis } from '../api'

export default function DataUpload() {
  const { orgId } = useParams()
  const navigate = useNavigate()

  const [progress, setProgress] = useState(0)
  const [analysisId, setAnalysisId] = useState(null)
  const [status, setStatus] = useState('idle')
  const [org, setOrg] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploadMethod, setUploadMethod] = useState('ZIP Archive')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [syncLoading, setSyncLoading] = useState(false)

  useEffect(() => {
    loadOrganization()
  }, [orgId])
  // Check for OAuth success/error in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const success = params.get('success')
    const error = params.get('error')

    if (success === 'slack_connected') {
      setSuccess('✅ Slack connected successfully! Now you can sync data.')
      window.history.replaceState({}, document.title, window.location.pathname)
      loadOrganization() // Reload org to show connected status
    }

    if (success === 'gmail_connected') {
      setSuccess('✅ Gmail connected successfully! Now you can sync data.')
      window.history.replaceState({}, document.title, window.location.pathname)
      loadOrganization() // Reload org to show connected status
    }

    if (error) {
      setError(`OAuth Error: ${error}. Please try again.`)
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [orgId])

  async function loadOrganization() {
    try {
      const data = await getOrganizations(orgId)
      setOrg(data)
    } catch (err) {
      setError('Failed to load organization')
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload() {
  if (!file) {
    setError('Please select a file')
    return
  }
  const validExtensions = {
    'ZIP Archive': ['.zip'],
    'Employee CSV': ['.csv', '.xlsx'],
    'Slack Export': ['.zip'],
    'Gmail Export': ['.mbox', '.zip'],
  }
  
  const allowedExts = validExtensions[uploadMethod]
  const fileExt = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!allowedExts.includes(fileExt)) {
    setError(`Invalid file type. Expected ${allowedExts.join(' or ')}, got ${fileExt}`)
    return
  }
  setUploading(true)
  setError('')
  setSuccess('')

  try {
    let uploadResult

    if (uploadMethod === 'ZIP Archive') {
      uploadResult = await uploadZip(orgId, file)
    } else if (uploadMethod === 'Employee CSV') {
      uploadResult = await uploadEmployeeCSV(orgId, file)
    } else if (uploadMethod === 'Slack Export') {
      uploadResult = await uploadSlackExport(orgId, file)
    } else if (uploadMethod === 'Gmail Export') {
      uploadResult = await uploadGmailExport(orgId, file)
    }

    if (!uploadResult || uploadResult.status !== 'success') {
      throw new Error(uploadResult?.message || 'Upload failed')
    }
    setSuccess('Data uploaded successfully! Starting analysis...')
    setFile(null)
    
    // Trigger analysis after upload
    const analysisResult = await triggerAnalysis(orgId)
    setAnalysisId(analysisResult.analysis_id)
    setStatus('running')
    setProgress(0)
    const interval = setInterval(async () => {
        try {
          const statusData = await getAnalysisStatus(analysisResult.analysis_id)
          setProgress(statusData.progress || 0)
          setStatus(statusData.status)
          
          // Analysis complete!
          if (statusData.status === 'completed') {
            clearInterval(interval)
            setProgress(100)
            setTimeout(() => {
              navigate(`/org/${orgId}/analysis/${analysisResult.analysis_id}`)
            }, 1000)
          }
        } catch (err) {
          console.error('Status check failed:', err)
        }
      }, 500)

    setTimeout(() => {
        clearInterval(interval)
        navigate(`/org/${orgId}/analysis/${analysisResult.analysis_id}`)
      }, 60000)
      
  } catch (err) {
    setSuccess('')
    setError(err.response?.data?.detail || 'Failed to upload data')
  } finally {
    setUploading(false)
  }
}

  async function handleSlackAuth() {
  setSyncLoading(true)
  setError('')
  try {
    const response = await getSlackAuthUrl(orgId)
    // Backend returns { url: "..." } not { auth_url: "..." }
    const redirectUrl = response.url || response.auth_url
    if (!redirectUrl) {
      setError('No redirect URL received from server')
      return
    }
    window.location.href = redirectUrl
  } catch (err) {
    setError('Failed to start Slack authentication')
  } finally {
    setSyncLoading(false)
  }
 }

  async function handleGmailAuth() {
  setSyncLoading(true)
  setError('')
  try {
    const response = await getGmailAuthUrl(orgId)
    const redirectUrl = response.url || response.auth_url
    if (!redirectUrl) {
      setError('No redirect URL received from server')
      return
    }
    window.location.href = redirectUrl
  } catch (err) {
    setError('Failed to start Gmail authentication')
  } finally {
    setSyncLoading(false)
  }
 }

  if (loading) {
    return <div className="flex items-center justify-center min-h-[400px]" />
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
          icon="📤"
          title="Upload Communication"
          highlight="Data"
          subtitle={`For ${org?.name || 'your organization'} — Slack, Gmail, or employee data in multiple formats.`}
        />

        <div className="space-y-6">
          {/* Upload Method Selection */}
          <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
            <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
              <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                1️⃣
              </div>
              <h3 className="font-bold text-lg text-neutral-900">Choose Upload Method</h3>
            </div>

            <InputMethodTabs
              options={['ZIP Archive', 'Employee CSV', 'Slack Export', 'Gmail Export', 'Connect Slack', 'Connect Gmail']}
              value={uploadMethod}
              onChange={setUploadMethod}
            />

            <div className="mt-6 p-4 rounded-xl bg-maroon-50 border border-maroon-200 text-maroon-800 text-sm">
              {uploadMethod === 'ZIP Archive' && (
                <p>
                  <strong>ZIP Archive:</strong> Upload a ZIP containing Slack exports (.json), Gmail exports (.mbox), and employee CSVs. Perfect for bulk imports from multiple sources.
                </p>
              )}
              {uploadMethod === 'Employee CSV' && (
                <p>
                  <strong>Employee CSV:</strong> Upload a CSV with employee info (name, email, title, department, manager, tenure). Maps communication to people.
                </p>
              )}
              {uploadMethod === 'Slack Export' && (
                <p>
                  <strong>Slack Export:</strong> Upload a .zip file from Slack's data export. Extracts channels, messages, and user information.
                </p>
              )}
              {uploadMethod === 'Gmail Export' && (
                <p>
                  <strong>Gmail Export:</strong> Upload .mbox file(s) from Gmail. Extracts email threads, metadata, and communication patterns.
                </p>
              )}
              {uploadMethod === 'Connect Slack' && (
                <p>
                  <strong>Live Slack Sync:</strong> Authorize OrgLens to access your Slack workspace in real-time. Get instant, continuous analysis.
                </p>
              )}
              {uploadMethod === 'Connect Gmail' && (
                <p>
                  <strong>Live Gmail Sync:</strong> Authorize OrgLens to access your Gmail. Continuous email analysis without manual export.
                </p>
              )}
            </div>
          </div>

          {/* File Upload / OAuth Section */}
          {['ZIP Archive', 'Employee CSV', 'Slack Export', 'Gmail Export'].includes(uploadMethod) && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                  2️⃣
                </div>
                <h3 className="font-bold text-lg text-neutral-900">Select File</h3>
              </div>

              {uploadMethod === 'ZIP Archive' && (
                <FileDropZone
                  accept=".zip"
                  label="Upload ZIP archive with communication data"
                  sublabel="Slack JSONs, Gmail .mbox files, or CSV exports"
                  onChange={setFile}
                  fileName={file?.name}
                />
              )}

              {uploadMethod === 'Employee CSV' && (
                <FileDropZone
                  accept=".csv"
                  label="Upload employee list CSV"
                  sublabel="Columns: name, email, title, department, manager, tenure_months"
                  onChange={setFile}
                  fileName={file?.name}
                />
              )}

              {uploadMethod === 'Slack Export' && (
                <FileDropZone
                  accept=".zip"
                  label="Upload Slack export .zip file"
                  sublabel="Export from Slack Workspace Settings → Data exports"
                  onChange={setFile}
                  fileName={file?.name}
                />
              )}

              {uploadMethod === 'Gmail Export' && (
                <FileDropZone
                  accept=".mbox,.zip"
                  label="Upload Gmail export file(s)"
                  sublabel=".mbox or .zip from Google Takeout"
                  onChange={setFile}
                  fileName={file?.name}
                />
              )}
            </div>
          )}

          {uploadMethod === 'Connect Slack' && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <Slack size={24} className="text-blue-600" />
                <h3 className="font-bold text-lg text-neutral-900">Authorize Slack Access</h3>
              </div>
              <p className="text-neutral-700 text-sm mb-6 leading-relaxed">
                Connect your Slack workspace to OrgLens. We'll fetch messages, channels, and user data for real-time analysis. You can revoke access anytime.
              </p>
              <button
                onClick={handleSlackAuth}
                disabled={syncLoading}
                className="w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-all shadow-neo-md hover:shadow-neo-lg"
              >
                {syncLoading ? 'Connecting...' : '🔗 Connect Slack Workspace'}
              </button>
              <p className="text-xs text-neutral-500 mt-4">
                Slack will open in a new window. Approve the permission request to continue.
              </p>
            </div>
          )}

          {uploadMethod === 'Connect Gmail' && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <Mail size={24} className="text-red-600" />
                <h3 className="font-bold text-lg text-neutral-900">Authorize Gmail Access</h3>
              </div>
              <p className="text-neutral-700 text-sm mb-6 leading-relaxed">
                Connect your Gmail account to OrgLens. We'll analyze email patterns, decision-making processes, and organizational communication. You can revoke access anytime.
              </p>
              <button
                onClick={handleGmailAuth}
                disabled={syncLoading}
                className="w-full px-6 py-3 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 disabled:opacity-50 transition-all shadow-neo-md hover:shadow-neo-lg"
              >
                {syncLoading ? 'Connecting...' : '🔗 Connect Gmail Account'}
              </button>
              <p className="text-xs text-neutral-500 mt-4">
                Google will open in a new window. Approve the permission request to continue.
              </p>
            </div>
          )}

          {/* Format Examples */}
          {['ZIP Archive', 'Employee CSV', 'Slack Export', 'Gmail Export'].includes(uploadMethod) && (
            <div className="rounded-2xl border border-neutral-200 bg-white p-8 backdrop-blur-xl shadow-neo-md">
              <div className="flex items-center gap-3 mb-6 pb-6 border-b border-neutral-200">
                <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center text-white font-bold">
                  📋
                </div>
                <h3 className="font-bold text-lg text-neutral-900">Expected Format</h3>
              </div>

              {uploadMethod === 'ZIP Archive' && (
                <div className="space-y-3 text-sm text-neutral-700">
                  <p className="font-semibold text-neutral-900">ZIP Structure:</p>
                  <pre className="bg-neutral-100 p-4 rounded-lg overflow-x-auto text-xs font-mono">
{`archive.zip/
├── employees.csv
├── slack/
│   ├── general.json
│   ├── engineering.json
│   └── sales.json
└── gmail.mbox`}
                  </pre>
                </div>
              )}

              {uploadMethod === 'Employee CSV' && (
                <div className="space-y-3 text-sm text-neutral-700">
                  <p className="font-semibold text-neutral-900">CSV Columns:</p>
                  <pre className="bg-neutral-100 p-4 rounded-lg overflow-x-auto text-xs font-mono">
{`name,email,title,department,manager,tenure_months
Sarah Chen,sarah@company.com,Sr Engineer,Engineering,John Smith,36
John Smith,john@company.com,Eng Manager,Engineering,VP Eng,60
Alice Johnson,alice@company.com,HR Lead,People,CEO,24`}
                  </pre>
                </div>
              )}

              {uploadMethod === 'Slack Export' && (
                <div className="space-y-3 text-sm text-neutral-700">
                  <p className="font-semibold text-neutral-900">How to export from Slack:</p>
                  <ol className="list-decimal list-inside space-y-2">
                    <li>Go to Workspace Settings → Analytics</li>
                    <li>Click "Export"</li>
                    <li>Choose date range and download .zip</li>
                    <li>Upload the downloaded file</li>
                  </ol>
                </div>
              )}

              {uploadMethod === 'Gmail Export' && (
                <div className="space-y-3 text-sm text-neutral-700">
                  <p className="font-semibold text-neutral-900">How to export from Gmail:</p>
                  <ol className="list-decimal list-inside space-y-2">
                    <li>Go to Google Takeout (takeout.google.com)</li>
                    <li>Select "Mail"</li>
                    <li>Download as .mbox or .zip</li>
                    <li>Upload the downloaded file</li>
                  </ol>
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          {error && <AlertBox type="error" title="Upload Error" message={error} />}
          {success && <AlertBox type="success" title="Success!" message={success} />}

          {/* Submit Button - Only for file uploads */}
          {['ZIP Archive', 'Employee CSV', 'Slack Export', 'Gmail Export'].includes(uploadMethod) && (
            <AnalyzeButton
              onClick={handleUpload}
              loading={uploading}
              label="Upload Data"
              icon="📤"
            />
          )}

          {/* Info */}
          <AlertBox 
            type="info"
            message="After upload/connection, we'll analyze communication patterns, influence networks, power dynamics, organizational health, and provide actionable recommendations."
          />
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