import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Network, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { isAuthenticated, logout, getUser } from '../lib/auth'

const DEMO_ORG_ID      = import.meta.env.VITE_DEMO_ORG_ID
const DEMO_ANALYSIS_ID = import.meta.env.VITE_DEMO_ANALYSIS_ID

export default function Navbar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const authed = isAuthenticated()
  const user = getUser()

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  function handleLogout() {
    logout()
    navigate('/')
  }

  const navItems = [
    { to: '/', label: 'Home' },
    ...(authed ? [{ to: '/organizations', label: 'Organizations' }] : []),
  ]

  return (
    <header className={`sticky top-0 z-50 transition-all duration-500 ${
      isScrolled
        ? 'border-b border-neutral-200 bg-white/95 backdrop-blur-2xl shadow-neo-md'
        : 'border-b border-neutral-100 bg-white/40 backdrop-blur-xl'
    }`}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="group relative z-10">
          <div className="absolute -inset-2 bg-maroon-500 rounded-xl opacity-0 group-hover:opacity-5 blur-xl transition-opacity duration-500" />
          <div className="relative flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-maroon-600 flex items-center justify-center group-hover:shadow-neo-md transition-all duration-300">
              <Network size={16} className="text-white" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">
              <span className="text-neutral-900">Org</span><span className="text-maroon-600">Lens</span>
            </span>
            <span className="hidden sm:inline-block text-xs text-neutral-400 font-medium border-l border-neutral-200 pl-2.5 ml-0.5">
              Organizational Intelligence
            </span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1.5">
          {navItems.map(({ to, label }) => {
            const active = pathname === to
            return (
              <Link
                key={to}
                to={to}
                className={`group relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  active
                    ? 'text-maroon-600'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                {active && (
                  <div className="absolute inset-0 bg-neutral-100 rounded-lg shadow-neo-sm" />
                )}
                <div className="absolute inset-0 bg-neutral-50 group-hover:bg-neutral-100 rounded-lg transition-all duration-300 opacity-0 group-hover:opacity-100" />
                <span className="relative">{label}</span>
              </Link>
            )
          })}

          {/* Demo — always visible, no auth needed */}
          <button
            onClick={() => navigate(`/org/${DEMO_ORG_ID}/dashboard/${DEMO_ANALYSIS_ID}`)}
            className="group relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 text-neutral-600 hover:text-neutral-900"
          >
            <div className="absolute inset-0 bg-neutral-50 group-hover:bg-neutral-100 rounded-lg transition-all duration-300 opacity-0 group-hover:opacity-100" />
            <span className="relative flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Demo
            </span>
          </button>
        </nav>

        {/* Right side — auth actions */}
        <div className="hidden md:flex items-center gap-3">
          {authed ? (
            <>
              {/* User pill */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-neutral-100 border border-neutral-200 shadow-neo-sm">
                <div className="w-5 h-5 rounded-full bg-maroon-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {user?.email?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
                <span className="text-xs text-neutral-600 font-medium max-w-[120px] truncate">
                  {user?.email}
                </span>
              </div>

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-neutral-600 hover:text-red-600 hover:bg-red-50 border border-neutral-200 hover:border-red-200 transition-all duration-300 shadow-neo-sm"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg text-sm font-semibold text-neutral-600 hover:text-maroon-600 hover:bg-maroon-50 transition-all duration-300"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg text-sm font-bold text-white bg-maroon-600 hover:bg-maroon-700 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden relative z-20 p-2 rounded-lg hover:bg-neutral-100 transition-colors text-neutral-900"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`md:hidden absolute top-16 left-0 right-0 bg-white/95 backdrop-blur-xl border-b border-neutral-200 overflow-hidden transition-all duration-300 ${
        isOpen ? 'max-h-96' : 'max-h-0'
      }`}>
        <nav className="p-4 space-y-2">
          {navItems.map(({ to, label }) => {
            const active = pathname === to
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 ${
                  active
                    ? 'bg-neutral-100 text-maroon-600 shadow-neo-sm'
                    : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                }`}
              >
                {label}
              </Link>
            )
          })}

          {/* Demo */}
          <button
            onClick={() => { setIsOpen(false); navigate(`/org/${DEMO_ORG_ID}/dashboard/${DEMO_ANALYSIS_ID}`) }}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Demo
          </button>

          <div className="pt-2 border-t border-neutral-100">
            {authed ? (
              <button
                onClick={() => { setIsOpen(false); handleLogout() }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-all duration-300 font-semibold"
              >
                Logout
              </button>
            ) : (
              <div className="flex gap-2">
                <Link
                  to="/login"
                  onClick={() => setIsOpen(false)}
                  className="flex-1 text-center px-4 py-3 rounded-lg text-neutral-600 hover:bg-neutral-50 transition-all font-semibold"
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  onClick={() => setIsOpen(false)}
                  className="flex-1 text-center px-4 py-3 rounded-lg bg-maroon-600 text-white font-bold hover:bg-maroon-700 transition-all shadow-neo-sm"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  )
}
