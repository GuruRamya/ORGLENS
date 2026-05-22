import axios from 'axios'
import { getToken, logout } from './lib/auth'
const API_BASE = import.meta.env.VITE_API_URL || ''
const BASE = `${API_BASE}/api`

// Add auth interceptor
axios.interceptors.request.use(config => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
axios.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) logout()
    return Promise.reject(err)
  }
)

// Organization APIs
export async function createOrganization(data) {
  const { data: response } = await axios.post(`${BASE}/organizations`, data)
  return response
}

export async function getOrganizations() {
  try {
    const { data } = await axios.get(`${BASE}/organizations`)
    return data
  } catch (err) {
    if (err.response && err.response.status === 404) {
      return []   // ✅ no orgs → return empty list
    }
    throw err
  }
}

export async function getOrganization(orgId) {
  const { data } = await axios.get(`${BASE}/organizations/${orgId}`)
  return data
}

export async function updateOrganization(orgId, data) {
  const { data: response } = await axios.put(`${BASE}/organizations/${orgId}`, data)
  return response
}

// Data Upload APIs
export async function uploadZip(orgId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('org_id', orgId)
  const { data } = await axios.post(`${BASE}/upload/zip`, formData)
  return data
}

export async function uploadEmployeeCSV(orgId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('org_id', orgId)
  const { data } = await axios.post(`${BASE}/upload/csv-employees`, formData)
  return data
}

export async function uploadSlackExport(orgId, file, channelName) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('org_id', orgId)
  formData.append('channel_name', channelName)
  const { data } = await axios.post(`${BASE}/upload/slack-export`, formData)
  return data
}

export async function syncSlackData(orgId) {
  const { data } = await axios.post(`${BASE}/upload/sync-slack/${orgId}`)
  return data
}

export async function uploadGmailExport(orgId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('org_id', orgId)
  const { data } = await axios.post(`${BASE}/upload/gmail-export`, formData)
  return data
}

export async function syncGmailData(orgId) {
  const { data } = await axios.post(`${BASE}/upload/sync-gmail/${orgId}`)
  return data
}

// Analysis APIs
export async function triggerAnalysis(orgId) {
  const { data } = await axios.post(`${BASE}/analysis/trigger/${orgId}`)
  return data
}

export async function getAnalysisStatus(analysisId) {
  const { data } = await axios.get(`${BASE}/analysis/status/${analysisId}`)
  return data
}

export async function getLatestAnalysis(orgId) {
  const { data } = await axios.get(`${BASE}/analysis/latest/${orgId}`)
  return data
}

export async function listAnalyses(orgId, limit = 10) {
  const { data } = await axios.get(`${BASE}/analysis/list/${orgId}`, {
    params: { limit }
  })
  return data
}

// Dashboard APIs
export async function getDashboardReport(analysisId) {
  const { data } = await axios.get(`${BASE}/dashboard/report/${analysisId}`)
  return data
}

export async function getDashboardCard(analysisId, cardType) {
  const { data } = await axios.get(`${BASE}/dashboard/card/${analysisId}/${cardType}`)
  return data
}

// OAuth APIs
export async function getSlackAuthUrl(orgId) {
  const { data } = await axios.get(`${BASE}/auth/slack/authorize`, {
    params: { org_id: orgId }
  })
  return data
}

export async function getGmailAuthUrl(orgId) {
  const { data } = await axios.get(`${BASE}/auth/gmail/authorize`, {
    params: { org_id: orgId }
  })
  return data
}

export async function disconnectSlack(orgId) {
  const { data } = await axios.post(`${BASE}/auth/disconnect/slack/${orgId}`)
  return data
}

export async function disconnectGmail(orgId) {
  const { data } = await axios.post(`${BASE}/auth/disconnect/gmail/${orgId}`)
  return data
}

export async function classifyPowerNodes(nodes) {
  const { data } = await axios.post(`${BASE}/dashboard/classify-nodes`, { nodes })
  return data.nodes
}

export async function chatWithAnalysis(analysisId, messages, context) {
  const { data } = await axios.post(`${BASE}/dashboard/chat/${analysisId}`, { 
    messages, context 
  })
  return data.reply
}

export async function deleteOrganization(orgId) {
  await axios.delete(`${BASE}/organizations/${orgId}`)
}

export default {
  // Organizations
  createOrganization,
  getOrganizations,
  getOrganization,
  updateOrganization,
  
  // Upload
  uploadZip,
  uploadEmployeeCSV,
  uploadSlackExport,
  syncSlackData,
  uploadGmailExport,
  syncGmailData,
  
  // Analysis
  triggerAnalysis,
  getAnalysisStatus,
  getLatestAnalysis,
  listAnalyses,
  
  // Dashboard
  getDashboardReport,
  getDashboardCard,
  
  // Auth
  getSlackAuthUrl,
  getGmailAuthUrl,
  disconnectSlack,
  disconnectGmail,
}