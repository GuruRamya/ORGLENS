import { Link } from 'react-router-dom'
import { Network, BarChart3, Users, Shield, ArrowRight, Zap, Microscope } from 'lucide-react'
import { useState, useEffect } from 'react'

const FEATURES = [
  { Icon: Network, title: 'Power Structure Analysis', desc: 'Map hidden influence and formal authority gaps' },
  { Icon: Shield, title: 'Trust Gap Detection', desc: 'Measure alignment between claims and reality' },
  { Icon: Users, title: 'Resilience Scoring', desc: 'Identify critical dependencies and risks' },
]

const STEPS = [
  { num: '01', title: 'Create Organization', desc: 'Set up your organization profile' },
  { num: '02', title: 'Upload Communication Data', desc: 'Slack, Gmail, or CSV files' },
  { num: '03', title: 'Run Analysis', desc: 'AI processes patterns and dynamics' },
  { num: '04', title: 'View Dashboard', desc: 'Get 10 detailed analysis cards' },
]

const CARDS = [
  { title: 'Org Health Score', icon: '💚', desc: 'Overall organizational vitality and function' },
  { title: 'Trust Gap', icon: '📊', desc: 'Claims vs. reality alignment analysis' },
  { title: 'Power Structure', icon: '🕸️', desc: 'Network mapping of influence flows' },
  { title: 'Top Influencers', icon: '⭐', desc: 'Hidden powers and formal leaders' },
  { title: 'Gatekeepers', icon: '🚪', desc: 'Information and decision control points' },
  { title: 'Resilience', icon: '💪', desc: 'Single points of failure analysis' },
  { title: 'Decision Velocity', icon: '⚡', desc: 'Speed of decision-making trends' },
  { title: 'System Diagnosis', icon: '🔍', desc: 'Root cause analysis of dysfunction' },
  { title: 'Predictions', icon: '🔮', desc: 'Attrition and reversal forecasts' },
  { title: 'Recommendations', icon: '💡', desc: 'Prioritized action items by impact' },
]

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('scroll', handleScroll)
    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [])

  return (
    <main className="relative overflow-hidden bg-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-maroon-100/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-40 right-20 w-80 h-80 bg-neutral-100/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute -bottom-20 left-1/2 w-96 h-96 bg-neutral-50/40 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <div
        className="fixed pointer-events-none w-96 h-96 rounded-full blur-3xl opacity-10 transition-opacity duration-300"
        style={{
          background: 'radial-gradient(circle, rgba(139, 58, 58, 0.2) 0%, transparent 70%)',
          left: `${mousePos.x - 192}px`,
          top: `${mousePos.y - 192}px`,
        }}
      />

      <div className="relative max-w-7xl mx-auto px-6 pt-32 pb-40">
        <div className="text-center mb-32 space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-maroon-50 border border-maroon-200 text-maroon-700 text-xs font-bold tracking-widest uppercase animate-fadeIn shadow-neo-sm">
            <span className="w-2 h-2 rounded-full bg-maroon-600 animate-pulse shadow-lg shadow-maroon-600/50" />
            Organizational Dynamics Intelligence
          </div>

          <div className="space-y-4 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
            <h1 className="font-display text-7xl md:text-8xl lg:text-9xl text-neutral-900 leading-none tracking-tight">
              Understand Your
              <br />
              <span className="text-maroon-600">
                Organization.
              </span>
            </h1>
            <p className="text-neutral-600 text-lg md:text-xl max-w-3xl mx-auto leading-relaxed">
              Analyze communication patterns, power dynamics, and organizational health.
              <br />
              <span className="text-maroon-700/70">Real insights. No politics.</span>
            </p>
          </div>

          <div className="flex items-center justify-center gap-4 pt-4 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            <Link
              to="/organizations"
              className="group relative px-8 py-4 bg-maroon-600 text-white font-bold rounded-xl overflow-hidden shadow-neo-md hover:shadow-neo-lg hover:bg-maroon-700 transition-all duration-300"
            >
              <span className="relative flex items-center gap-2">
                Get Started
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
            <a
              href="#cards"
              className="px-8 py-4 rounded-xl border border-neutral-300 text-neutral-900 font-bold hover:border-maroon-500 hover:bg-maroon-50 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md"
            >
              See Analysis Cards
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-32 animate-fadeIn" style={{ animationDelay: '0.3s' }}>
          {FEATURES.map(({ Icon, title, desc }, i) => (
            <div
              key={title}
              className="group relative p-6 rounded-2xl border border-neutral-200 bg-neutral-50 hover:border-maroon-300 hover:bg-maroon-50 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md"
              style={{ animationDelay: `${0.3 + i * 0.1}s` }}
            >
              <div className="relative space-y-2">
                <div className="w-10 h-10 rounded-lg bg-maroon-600 flex items-center justify-center group-hover:shadow-neo-md transition-all">
                  <Icon size={16} className="text-white" />
                </div>
                <p className="text-neutral-900 font-bold text-sm">{title}</p>
                <p className="text-neutral-600 text-xs">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-32 space-y-12">
          <div className="text-center space-y-2">
            <p className="text-maroon-700 text-sm font-bold tracking-widest uppercase">Process</p>
            <h2 className="font-display text-5xl text-neutral-900">How OrgLens Works</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {STEPS.map(({ num, title, desc }, i) => (
              <div
                key={num}
                className="relative group animate-fadeIn"
                style={{ animationDelay: `${0.6 + i * 0.1}s` }}
              >
                {i < STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-2 w-4 h-0.5 bg-gradient-to-r from-maroon-400 to-transparent" />
                )}
                <div className="relative p-6 rounded-2xl border border-neutral-200 bg-white hover:border-maroon-300 hover:shadow-neo-lg shadow-neo-sm transition-all duration-300 h-full">
                  <div className="absolute -top-3 left-6 w-6 h-6 rounded-full bg-maroon-600 border-4 border-white flex items-center justify-center text-white text-xs font-bold shadow-neo-md" />
                  <div className="pt-3 space-y-2">
                    <p className="text-neutral-500 text-xs font-mono">{num}</p>
                    <p className="text-neutral-900 font-bold text-sm">{title}</p>
                    <p className="text-neutral-600 text-xs">{desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div id="cards" className="space-y-12">
          <div className="text-center space-y-2">
            <p className="text-maroon-700 text-sm font-bold tracking-widest uppercase">Dashboard</p>
            <h2 className="font-display text-5xl text-neutral-900">10 Analysis Cards</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {CARDS.map(({ title, icon, desc }, i) => (
              <div
                key={title}
                className="group relative overflow-hidden rounded-2xl border border-neutral-200 bg-gradient-to-br from-neutral-50 to-white p-6 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md hover:border-maroon-300 animate-fadeIn"
                style={{ animationDelay: `${0.9 + i * 0.05}s` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                <div className="relative space-y-3">
                  <div className="text-3xl">{icon}</div>
                  <h3 className="font-bold text-sm text-neutral-900">{title}</h3>
                  <p className="text-neutral-600 text-xs leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-40 relative rounded-3xl border border-neutral-200 bg-gradient-to-br from-maroon-50 to-white p-12 text-center overflow-hidden shadow-neo-lg">
          <div className="relative space-y-4">
            <h3 className="font-display text-3xl font-bold text-neutral-900">Ready to Analyze Your Organization?</h3>
            <p className="text-neutral-600 max-w-2xl mx-auto">
              Upload your communication data now and get instant insights into organizational dynamics, power structures, and improvement opportunities.
            </p>
            <Link
              to="/organizations"
              className="inline-block px-8 py-4 bg-maroon-600 text-white font-bold rounded-xl hover:bg-maroon-700 hover:shadow-neo-lg transition-all duration-300 shadow-neo-md"
            >
              Start Your Analysis →
            </Link>
          </div>
        </div>

        <div className="mt-32 pt-12 border-t border-neutral-200 text-center space-y-3">
          <p className="text-neutral-600 text-sm">
            Built with precision by <span className="text-maroon-600 font-bold">OrgLens</span>
          </p>
          <p className="text-xs text-neutral-500">
            Organizational analysis tool for executives and HR leaders.
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.8s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </main>
  )
}
