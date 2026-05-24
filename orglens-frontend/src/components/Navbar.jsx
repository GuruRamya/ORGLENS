import { Link, useLocation } from 'react-router-dom'
import { Network, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const { pathname } = useLocation()
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { to: '/', label: 'Home' },
    { to: '/organizations', label: 'Organizations' },
  ]

  return (
    <header className={`sticky top-0 z-50 transition-all duration-500 ${
      isScrolled 
        ? 'border-b border-neutral-200 bg-white/95 backdrop-blur-2xl shadow-neo-md' 
        : 'border-b border-neutral-100 bg-white/40 backdrop-blur-xl'
    }`}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="group relative z-10">
          <div className="absolute -inset-2 bg-maroon-500 rounded-xl opacity-0 group-hover:opacity-5 blur-xl transition-opacity duration-500" />
          <div className="relative flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-maroon-600 flex items-center justify-center group-hover:shadow-neo-md transition-all duration-300">
              <Network size={16} className="text-white" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">
              <span className="text-neutral-900">Org</span><span className="text-maroon-600">Lens</span>
            </span>
          </div>
        </Link>

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
        </nav>

        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden relative z-20 p-2 rounded-lg hover:bg-neutral-100 transition-colors text-neutral-900"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-neutral-100 border border-neutral-200 backdrop-blur-sm shadow-neo-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-maroon-600 animate-pulse shadow-lg shadow-maroon-600/50" />
          <span className="text-xs text-maroon-600 font-semibold">Live</span>
        </div>
      </div>

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
        </nav>
      </div>
    </header>
  )
}
