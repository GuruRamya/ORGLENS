import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Network, Eye, EyeOff } from 'lucide-react'
import { login, register } from '../lib/auth'

export default function Auth({ mode = 'login' }) {
  const navigate = useNavigate()
  const [tab, setTab] = useState(mode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (tab === 'login') {
        await login(email, password)
      } else {
        await register(email, password, name)
      }
      navigate('/organizations')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center gap-2.5 justify-center mb-10">
          <div className="w-10 h-10 rounded-xl bg-maroon-600 flex items-center justify-center shadow-neo-md">
            <Network size={20} className="text-white" />
          </div>
          <span className="font-display text-2xl font-bold">
            <span className="text-neutral-900">Org</span>
            <span className="text-maroon-600">Lens</span>
          </span>
        </div>

        <div className="rounded-2xl border border-neutral-200 bg-white p-8 shadow-neo-lg">
          {/* Tab switch */}
          <div className="flex gap-1 p-1 bg-neutral-100 rounded-xl mb-8">
            {['login', 'register'].map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  tab === t ? 'bg-white text-neutral-900 shadow-neo-sm' : 'text-neutral-500'
                }`}
              >
                {t === 'login' ? 'Sign in' : 'Create account'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === 'register' && (
              <div>
                <label className="text-sm font-semibold text-neutral-700 block mb-1.5">Full name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Sarah Chen"
                  className="input-field"
                />
              </div>
            )}
            <div>
              <label className="text-sm font-semibold text-neutral-700 block mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="text-sm font-semibold text-neutral-700 block mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Min 8 characters"
                  className="input-field pr-10"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-maroon-600 text-white font-bold rounded-xl hover:bg-maroon-700 disabled:opacity-50 transition-all shadow-neo-md hover:shadow-neo-lg"
            >
              {loading ? 'Please wait…' : tab === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          {tab === 'login' && (
            <p className="text-center text-sm text-neutral-500 mt-6">
              New to OrgLens?{' '}
              <button onClick={() => setTab('register')} className="text-maroon-600 font-semibold hover:underline">
                Create an account
              </button>
            </p>
          )}
        </div>

        <p className="text-center text-xs text-neutral-400 mt-6">
          All analysis data is encrypted and isolated per organization.
        </p>
      </div>
    </div>
  )
}