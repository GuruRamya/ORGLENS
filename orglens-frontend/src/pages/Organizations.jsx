import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Loader2,
  Network,
  ChevronRight,
  Trash2
} from 'lucide-react'

import {
  getOrganizations,
  deleteOrganization
} from '../api'

import { PageHeader } from '../components/Shared'

const DEMO_ORG_ID = import.meta.env.VITE_DEMO_ORG_ID
const DEMO_ANALYSIS_ID = import.meta.env.VITE_DEMO_ANALYSIS_ID

export default function Organizations() {
  const [orgs, setOrgs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    loadOrganizations()
  }, [])

  async function loadOrganizations() {
    try {
      setLoading(true)
      setError('')

      const data = await getOrganizations()

      let orgList = []

      if (Array.isArray(data)) {
        orgList = data
      } else if (data && Array.isArray(data.organizations)) {
        orgList = data.organizations
      }

      setOrgs(orgList)

    } catch (err) {
      console.error(err)

      if (err.response?.status >= 500) {
        setError('Server error. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(e, orgId, orgName) {
    e.preventDefault()
    e.stopPropagation()

    const confirmed = window.confirm(
      `Delete "${orgName}"?\n\nThis will permanently remove all analyses, messages, and organizational data.`
    )

    if (!confirmed) return

    setDeletingId(orgId)

    try {
      await deleteOrganization(orgId)

      setOrgs(prev =>
        prev.filter(org => org.id !== orgId)
      )

    } catch (err) {
      console.error(err)

      alert('Failed to delete organization. Please try again.')

    } finally {
      setDeletingId(null)
    }
  }
  
  function getOrgLink(orgId) {
    if (orgId === DEMO_ORG_ID && DEMO_ANALYSIS_ID) {
      return `/org/${orgId}/dashboard/${DEMO_ANALYSIS_ID}`
    }
    return `/org/${orgId}/upload`
  }

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">

      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-maroon-100/20 rounded-full blur-3xl animate-pulse" />

        <div
          className="absolute bottom-20 right-1/4 w-96 h-96 bg-neutral-100/30 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: '1s' }}
        />
      </div>

      <div className="relative max-w-6xl mx-auto px-6 py-12">

        <PageHeader
          icon="🏢"
          title="Your"
          highlight="Organizations"
          subtitle="Create and manage organizational analysis projects."
        />

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2
                size={48}
                className="text-maroon-600 animate-spin mx-auto mb-4"
              />

              <p className="text-neutral-600">
                Loading organizations...
              </p>
            </div>
          </div>

        ) : (
          <div className="space-y-6">

            <Link
              to="/org/new"
              className="flex items-center justify-between p-6 rounded-2xl border border-dashed border-maroon-300 bg-maroon-50 hover:bg-maroon-100 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md group"
            >
              <div className="flex items-center gap-3">

                <div className="w-12 h-12 rounded-lg bg-maroon-600 flex items-center justify-center group-hover:shadow-neo-md transition-all">
                  <Plus size={24} className="text-white" />
                </div>

                <div>
                  <p className="font-bold text-maroon-900">
                    Create New Organization
                  </p>

                  <p className="text-maroon-700/70 text-sm">
                    Start analyzing a new organization
                  </p>
                </div>
              </div>

              <ChevronRight className="text-maroon-600 group-hover:translate-x-1 transition-transform" />
            </Link>

            {orgs.length === 0 ? (
              <div className="text-center py-20">

                <Network
                  size={48}
                  className="text-neutral-300 mx-auto mb-4"
                />

                <p className="text-neutral-600 text-lg mb-4">
                  No organizations yet
                </p>

                <p className="text-neutral-500 text-sm">
                  Create your first organization to get started
                </p>
              </div>

            ) : (

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {orgs.map(org => (

                  <div
                    key={org.id}
                    className="relative group"
                  >

                    <Link
                      to={getOrgLink(org.id)}
                      className="block p-6 rounded-2xl border border-neutral-200 bg-white hover:border-maroon-300 hover:shadow-neo-lg shadow-neo-sm transition-all duration-300"
                    >

                      <div className="flex items-start justify-between mb-4 pb-4 border-b border-neutral-200">

                        <div className="flex-1 min-w-0 pr-4">
                          <h3 className="font-bold text-lg text-neutral-900 group-hover:text-maroon-600 transition-colors truncate">
                            {org.name}
                          </h3>

                          <p className="text-neutral-500 text-sm mt-1">
                            {org.industry || 'General Organization'}
                          </p>
                        </div>

                        <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center group-hover:shadow-neo-md transition-all flex-shrink-0">
                          <Network size={18} className="text-white" />
                        </div>
                      </div>

                      <div className="space-y-3 mb-4">

                        <div className="flex items-center gap-2">
                          <span className="text-xs text-neutral-500">
                            Size:
                          </span>

                          <span className="text-sm font-semibold text-neutral-900">
                            {org.size_estimate
                              ? `~${org.size_estimate} people`
                              : 'Not specified'}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-xs text-neutral-500">
                            Integrations:
                          </span>

                          <div className="flex gap-2">

                            {org.slack_connected && (
                              <span className="text-xs px-2.5 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">
                                Slack ✓
                              </span>
                            )}

                            {org.gmail_connected && (
                              <span className="text-xs px-2.5 py-1 rounded-full bg-red-100 text-red-700 font-medium">
                                Gmail ✓
                              </span>
                            )}

                            {!org.slack_connected &&
                              !org.gmail_connected && (
                                <span className="text-xs text-neutral-500 italic">
                                  None connected
                                </span>
                              )}
                          </div>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-neutral-200 flex items-center justify-between">

                        <p className="text-xs text-neutral-500">
                          Created{' '}
                          {new Date(org.created_at).toLocaleDateString()}
                        </p>

                        <ChevronRight
                          size={16}
                          className="text-maroon-600 group-hover:translate-x-1 transition-transform"
                        />
                      </div>
                    </Link>

                    {org.id !== DEMO_ORG_ID && (
                      <button
                        onClick={(e) =>
                          handleDelete(e, org.id, org.name)
                        }

                        disabled={deletingId === org.id}

                        className="absolute top-4 right-16 opacity-0 group-hover:opacity-100 transition-all duration-200 p-2 rounded-lg bg-white border border-red-200 text-red-500 hover:bg-red-50 hover:border-red-400 shadow-neo-sm disabled:opacity-50"
                        title="Delete organization"
                      >
                        {deletingId === org.id ? (
                          <Loader2
                            size={15}
                            className="animate-spin"
                          />
                        ) : (
                          <Trash2 size={15} />
                        )}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 text-sm flex items-start gap-3 mt-6 shadow-neo-sm">

            <span className="text-lg flex-shrink-0">
              ⚠️
            </span>

            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
