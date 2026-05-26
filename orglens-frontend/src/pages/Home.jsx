import { Link, useNavigate } from 'react-router-dom'
import { Network, BarChart3, Users, Shield, ArrowRight, Zap, Microscope, Brain, TrendingUp, Target, Eye, Activity } from 'lucide-react'
import { useState, useEffect } from 'react'
import { isAuthenticated } from '../lib/auth'

const DEMO_ORG_ID      = import.meta.env.VITE_DEMO_ORG_ID
const DEMO_ANALYSIS_ID = import.meta.env.VITE_DEMO_ANALYSIS_ID

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

const DEEP_DIVE_SECTIONS = [
  {
    num: '01',
    icon: <TrendingUp size={20} className="text-white" />,
    title: 'Temporal Evolution',
    desc: 'See exactly how trust, health, and burnout risk have shifted week-by-week. Pinpoint inflection points and understand the events that caused them.',
    color: 'bg-blue-600',
    tags: ['12-week trend', 'Burnout detection', 'Event mapping'],
  },
  {
    num: '02',
    icon: <Network size={20} className="text-white" />,
    title: 'Full Communication Network',
    desc: 'Every person, every connection — visualized. See how authority and influence actually flow versus how the org chart says they should.',
    color: 'bg-purple-600',
    tags: ['All nodes', 'Influence scoring', 'Interactive tooltips'],
  },
  {
    num: '03',
    icon: <Users size={20} className="text-white" />,
    title: 'Manager Effectiveness',
    desc: 'Complete breakdown of every manager: team trust, psychological safety score, burnout risk, and decision delays they contribute.',
    color: 'bg-emerald-600',
    tags: ['Trust metrics', 'Burnout risk', 'Delay attribution'],
  },
  {
    num: '04',
    icon: <Activity size={20} className="text-white" />,
    title: 'Burnout Detection',
    desc: 'Department-by-department burnout risk analysis using behavioral signals: after-hours messaging, urgency language, hedging phrases.',
    color: 'bg-red-600',
    tags: ['All departments', 'Behavioral signals', 'Fatigue language'],
  },
  {
    num: '05',
    icon: <Brain size={20} className="text-white" />,
    title: 'Psychological Safety Index',
    desc: 'Six-dimension radar chart comparing your org against healthy benchmarks — upward feedback, open challenges, idea sharing, and more.',
    color: 'bg-amber-600',
    tags: ['Radar chart', 'Benchmark comparison', 'Escalation rate'],
  },
  {
    num: '06',
    icon: <Eye size={20} className="text-white" />,
    title: 'Evidence Chains',
    desc: 'Every finding traced back to raw signals. See exactly which messages and behavioral patterns led to each conclusion.',
    color: 'bg-neutral-700',
    tags: ['Full evidence', 'ML signals', 'Source quotes'],
  },
  {
    num: '07',
    icon: <Target size={20} className="text-white" />,
    title: 'Executive Summaries',
    desc: 'Role-specific intelligence for CHRO, CTO, and CEO — tailored action items, risks, and priorities for each leadership perspective.',
    color: 'bg-maroon-600',
    tags: ['CHRO view', 'CTO view', 'CEO briefing'],
  },
  {
    num: '08',
    icon: <Zap size={20} className="text-white" />,
    title: 'Scenario Simulations',
    desc: 'Model "what if" scenarios — what happens to health, trust and resilience if a key person leaves, compensation is fixed, or a reorg happens.',
    color: 'bg-orange-600',
    tags: ['5 scenarios', 'Impact modeling', 'Before/after view'],
  },
]

export default function Home() {
  const navigate = useNavigate()
  const [isScrolled, setIsScrolled] = useState(false)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const authed = isAuthenticated()

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    const handleMouseMove = (e) => setMousePos({ x: e.clientX, y: e.clientY })
    window.addEventListener('scroll', handleScroll)
    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [])

  function handleAuthGatedClick(destination) {
    if (authed) {
      navigate(destination)
    } else {
      navigate('/login')
    }
  }

  return (
    <main className="relative overflow-hidden bg-white">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-maroon-100/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-40 right-20 w-80 h-80 bg-neutral-100/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute -bottom-20 left-1/2 w-96 h-96 bg-neutral-50/40 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* Cursor light */}
      <div
        className="fixed pointer-events-none w-96 h-96 rounded-full blur-3xl opacity-10 transition-all duration-300"
        style={{
          background: 'radial-gradient(circle, rgba(139, 58, 58, 0.2) 0%, transparent 70%)',
          left: `${mousePos.x - 192}px`,
          top: `${mousePos.y - 192}px`,
        }}
      />

      <div className="relative max-w-7xl mx-auto px-6 pt-32 pb-40">

        {/* ── Hero ── */}
        <div className="text-center mb-32 space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-maroon-50 border border-maroon-200 text-maroon-700 text-xs font-bold tracking-widest uppercase animate-fadeIn shadow-neo-sm">
            <span className="w-2 h-2 rounded-full bg-maroon-600 animate-pulse shadow-lg shadow-maroon-600/50" />
            Organizational Dynamics Intelligence
          </div>

          <div className="space-y-4 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
            <h1 className="font-display text-7xl md:text-8xl lg:text-9xl text-neutral-900 leading-none tracking-tight">
              Understand Your
              <br />
              <span className="text-maroon-600">Organization.</span>
            </h1>
            <p className="text-neutral-600 text-lg md:text-xl max-w-3xl mx-auto leading-relaxed">
              Analyze communication patterns, power dynamics, and organizational health.
              <br />
              <span className="text-maroon-700/70">Real insights. No politics.</span>
            </p>
          </div>

          <div className="flex items-center justify-center gap-4 pt-4 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            <button
              onClick={() => handleAuthGatedClick('/organizations')}
              className="group relative px-8 py-4 bg-maroon-600 text-white font-bold rounded-xl overflow-hidden shadow-neo-md hover:shadow-neo-lg hover:bg-maroon-700 transition-all duration-300"
            >
              <span className="relative flex items-center gap-2">
                Get Started
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </span>
            </button>

            {/* Demo — no auth needed, use Link directly */}
            <Link
              to={`/org/${DEMO_ORG_ID}/dashboard/${DEMO_ANALYSIS_ID}`}
              className="group inline-flex px-8 py-4 rounded-xl border border-neutral-300 text-neutral-900 font-bold hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 transition-all duration-300 shadow-neo-sm hover:shadow-neo-md items-center gap-2"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              View Live Demo
            </Link>
          </div>
        </div>

        {/* ── Features Grid ──*/}
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

        {/* ── How It Works ──*/}
        <div className="mb-32 space-y-12">
          <div className="text-center space-y-2">
            <p className="text-maroon-700 text-sm font-bold tracking-widest uppercase">Process</p>
            <h2 className="font-display text-5xl text-neutral-900">How OrgLens Works</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {STEPS.map(({ num, title, desc }, i) => (
              <div key={num} className="relative group animate-fadeIn" style={{ animationDelay: `${0.6 + i * 0.1}s` }}>
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

        {/* ── Analysis Cards ──*/}
        <div id="cards" className="space-y-12 mb-32">
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

        {/* ── Deep Dive Analysis Section ── */}
        <div id="deep-dive" className="mb-32 space-y-12">
          <div className="text-center space-y-4">
            <p className="text-maroon-700 text-sm font-bold tracking-widest uppercase">Advanced Intelligence</p>
            <h2 className="font-display text-5xl text-neutral-900">
              Deep Dive Analysis
            </h2>
            <p className="text-neutral-600 text-base max-w-2xl mx-auto leading-relaxed">
              Beyond the dashboard — a full organizational story told through 13 immersive sections.
              Every finding explained, every signal traced, every risk simulated.
            </p>
          </div>

          {/* Preview banner */}
          <div className="relative rounded-3xl overflow-hidden border border-neutral-200 shadow-neo-lg">
            <div className="absolute inset-0 bg-gradient-to-br from-neutral-50 to-white" />
            <div className="relative px-10 py-12 flex flex-col md:flex-row items-center gap-8">
              <div className="flex-1 text-center md:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-100 border border-neutral-200 text-neutral-500 text-xs font-semibold mb-4">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Available after analysis
                </div>
                <h3 className="font-display text-3xl text-neutral-900 font-bold mb-3">
                  13 Deep-Dive Modules
                </h3>
                <p className="text-neutral-500 text-sm leading-relaxed max-w-lg">
                  From temporal evolution charts to scenario simulations — unlock the complete organizational story when you run your first analysis.
                </p>
              </div>
              <div className="grid grid-cols-4 gap-2 flex-shrink-0">
                {['📈', '🕸️', '👥', '🔥', '🛡️', '🔗', '👔', '⚡'].map((icon, i) => (
                  <div key={i} className="w-12 h-12 rounded-xl bg-neutral-100 border border-neutral-200 flex items-center justify-center text-xl hover:bg-maroon-50 hover:border-maroon-200 transition-all duration-200">
                    {icon}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Deep dive cards grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {DEEP_DIVE_SECTIONS.map(({ num, icon, title, desc, color, tags }, i) => (
              <div
                key={num}
                className="group relative p-6 rounded-2xl border border-neutral-200 bg-white hover:border-maroon-200 hover:shadow-neo-md shadow-neo-sm transition-all duration-300 animate-fadeIn"
                style={{ animationDelay: `${1.2 + i * 0.06}s` }}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center flex-shrink-0 shadow-sm group-hover:shadow-md transition-all`}>
                    {icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-neutral-400">{num}</span>
                      <h3 className="font-bold text-sm text-neutral-900">{title}</h3>
                    </div>
                    <p className="text-neutral-600 text-xs leading-relaxed mb-3">{desc}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {tags.map(tag => (
                        <span key={tag} className="text-xs px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-600 border border-neutral-200 font-medium">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Run analysis CTA */}
          <div className="text-center pt-4">
            <button
              onClick={() => handleAuthGatedClick('/organizations')}
              className="group inline-flex items-center gap-3 px-8 py-4 bg-neutral-900 text-white font-bold rounded-xl hover:bg-neutral-800 transition-all duration-300 shadow-neo-md hover:shadow-neo-lg"
            >
              <span className="text-lg">⚡</span>
              Run Your First Analysis
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <p className="text-xs text-neutral-400 mt-3">
              Deep Dive unlocks automatically after analysis completes
            </p>
          </div>
        </div>

        {/* ── Final CTA ── */}
        <div className="mt-8 relative rounded-3xl border border-neutral-200 bg-gradient-to-br from-maroon-50 to-white p-12 text-center overflow-hidden shadow-neo-lg">
          <div className="relative space-y-4">
            <h3 className="font-display text-3xl font-bold text-neutral-900">Ready to Analyze Your Organization?</h3>
            <p className="text-neutral-600 max-w-2xl mx-auto">
              Upload your communication data and get instant insights into organizational dynamics, power structures, and improvement opportunities.
            </p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <button
                onClick={() => handleAuthGatedClick('/organizations')}
                className="inline-flex items-center gap-2 px-8 py-4 bg-maroon-600 text-white font-bold rounded-xl hover:bg-maroon-700 transition-all duration-300 shadow-neo-md hover:shadow-neo-lg"
              >
                Start Your Analysis →
              </button>
              <Link
                to={`/org/${DEMO_ORG_ID}/dashboard/${DEMO_ANALYSIS_ID}`}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-xl border border-neutral-300 text-neutral-700 font-bold hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 transition-all duration-300 shadow-neo-sm"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                View Demo First
              </Link>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-32 pt-12 border-t border-neutral-200 text-center space-y-3">
          <p className="text-neutral-600 text-sm">
            Built with precision by <span className="text-maroon-600 font-bold">OrgLens</span>
          </p>
          <p className="text-xs text-neutral-500">
            Organizational analysis tool for executives and HR leaders.
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.8s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </main>
  )
}
