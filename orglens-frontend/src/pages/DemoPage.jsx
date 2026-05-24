import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import {
  Loader2, ArrowLeft, ChevronDown, ChevronUp,
  TrendingUp, TrendingDown, Minus, Zap, Bot, X, Send, User
} from 'lucide-react'


async function fetchDemoReport() {
  const { data } = await axios.get('/api/demo/report')
  return data
}


function scoreColor(score, invert = false) {
  const s = invert ? 10 - score : score
  if (s >= 7.5) return 'text-emerald-600'
  if (s >= 5)   return 'text-amber-600'
  return 'text-red-600'
}

function scoreBg(score, invert = false) {
  const s = invert ? 10 - score : score
  if (s >= 7.5) return 'bg-emerald-50 border-emerald-200'
  if (s >= 5)   return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}

function ScoreBar({ value, max = 10, invert = false }) {
  const pct = (value / max) * 100
  const color = (() => {
    const s = invert ? 10 - value : value
    if (s >= 7.5) return 'bg-emerald-500'
    if (s >= 5)   return 'bg-amber-500'
    return 'bg-red-500'
  })()
  return (
    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

function Badge({ label, type = 'neutral' }) {
  const styles = {
    critical: 'bg-red-100 text-red-700 border-red-200',
    high:     'bg-orange-100 text-orange-700 border-orange-200',
    medium:   'bg-amber-100 text-amber-700 border-amber-200',
    low:      'bg-emerald-100 text-emerald-700 border-emerald-200',
    neutral:  'bg-neutral-100 text-neutral-600 border-neutral-200',
    info:     'bg-blue-100 text-blue-700 border-blue-200',
  }
  return (
    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${styles[type] || styles.neutral}`}>
      {label}
    </span>
  )
}


function AnalysisCard({ icon, title, subtitle, score, scoreInvert, expanded, onToggle, children }) {
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white shadow-neo-sm hover:shadow-neo-md transition-all duration-300">
      <button onClick={onToggle} className="w-full text-left p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-3xl">{icon}</span>
          <div>
            <h3 className="font-bold text-neutral-900">{title}</h3>
            <p className="text-xs text-neutral-500 mt-0.5">{subtitle}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {score !== undefined && (
            <div className={`px-3 py-1.5 rounded-lg border ${scoreBg(score, scoreInvert)}`}>
              <span className={`font-bold text-sm ${scoreColor(score, scoreInvert)}`}>
                {score.toFixed(1)}/10
              </span>
            </div>
          )}
          {expanded
            ? <ChevronUp size={18} className="text-neutral-400" />
            : <ChevronDown size={18} className="text-neutral-400" />}
        </div>
      </button>
      {expanded && (
        <div className="px-6 pb-6 border-t border-neutral-100 pt-5">
          {children}
        </div>
      )}
    </div>
  )
}


function OrgHealthCard({ data }) {
  if (!data) return null
  return (
    <div className="space-y-4">
      <p className="text-sm text-neutral-700 leading-relaxed">{data.summary}</p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(data.health_breakdown || {}).map(([key, val]) => (
          <div key={key} className="p-3 rounded-xl bg-neutral-50 border border-neutral-200">
            <p className="text-xs text-neutral-500 capitalize mb-1">{key.replace(/_/g, ' ')}</p>
            <div className="flex items-center justify-between mb-1">
              <span className={`text-base font-bold ${scoreColor(val)}`}>{Number(val).toFixed(1)}</span>
              <span className="text-xs text-neutral-400">/10</span>
            </div>
            <ScoreBar value={val} />
          </div>
        ))}
      </div>
      <div className={`p-4 rounded-xl border ${scoreBg(data.org_health_score)}`}>
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-neutral-700">Overall Grade</span>
          <span className={`text-3xl font-bold ${scoreColor(data.org_health_score)}`}>{data.grade}</span>
        </div>
      </div>
    </div>
  )
}

function TrustGapCard({ data }) {
  if (!data) return null
  const claims = data.top_gaps || []
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Gap Score</p>
          <p className={`text-xl font-bold ${scoreColor(data.trust_gap_score, true)}`}>{data.trust_gap_score?.toFixed(1)}</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Severity</p>
          <Badge label={data.severity?.toUpperCase()} type={data.severity} />
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Trend</p>
          {data.trend === 'widening' ? <TrendingUp size={18} className="text-red-500 mx-auto" /> :
           data.trend === 'narrowing' ? <TrendingDown size={18} className="text-emerald-500 mx-auto" /> :
           <Minus size={18} className="text-amber-500 mx-auto" />}
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.trend || 'stable'}</p>
        </div>
      </div>
      {claims.map((claim, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-2">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-bold text-neutral-500">Claim</p>
              <p className="text-sm text-neutral-800 mt-0.5">{claim.claim}</p>
            </div>
            <Badge label={`Gap: ${Number(claim.gap || 0).toFixed(1)}`} type={claim.gap >= 7 ? 'critical' : claim.gap >= 5 ? 'high' : 'medium'} />
          </div>
          <div>
            <p className="text-xs font-bold text-red-600">Reality</p>
            <p className="text-sm text-neutral-700 mt-0.5">{claim.reality}</p>
          </div>
          <ScoreBar value={claim.gap || 0} invert />
        </div>
      ))}
    </div>
  )
}

function PowerStructureCard({ data }) {
  if (!data) return null
  const nodes = data.nodes || []
  const LEVEL_ORDER = ['C-Suite', 'VP', 'Director', 'Manager', 'Senior IC', 'IC', '']
  const LEVEL_STYLES = {
    'C-Suite':   { bg: 'bg-red-50',     border: 'border-red-200',     dot: 'bg-red-600',     text: 'text-red-700' },
    'VP':        { bg: 'bg-blue-50',    border: 'border-blue-200',    dot: 'bg-blue-500',    text: 'text-blue-700' },
    'Director':  { bg: 'bg-purple-50',  border: 'border-purple-200',  dot: 'bg-purple-500',  text: 'text-purple-700' },
    'Manager':   { bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-500', text: 'text-emerald-700' },
    'Senior IC': { bg: 'bg-amber-50',   border: 'border-amber-200',   dot: 'bg-amber-500',   text: 'text-amber-700' },
    'IC':        { bg: 'bg-neutral-50', border: 'border-neutral-200', dot: 'bg-neutral-400', text: 'text-neutral-600' },
    '':          { bg: 'bg-neutral-50', border: 'border-neutral-200', dot: 'bg-neutral-300', text: 'text-neutral-500' },
  }
  const TYPE_ICONS = { hidden_power: '⚡', formal_leader: '👑', ignored_authority: '⚠️', gatekeeper: '🚪' }

  const byLevel = {}
  nodes.forEach(n => {
    const lvl = LEVEL_ORDER.includes(n.level) ? n.level : ''
    if (!byLevel[lvl]) byLevel[lvl] = []
    byLevel[lvl].push(n)
  })
  const presentLevels = LEVEL_ORDER.filter(l => byLevel[l]?.length > 0)

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-2">
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-center">
          <p className="text-2xl font-bold text-red-600">{data.hidden_powers || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Hidden powers</p>
        </div>
        <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-center">
          <p className="text-2xl font-bold text-blue-600">{data.ignored_authorities || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Ignored authorities</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-2xl font-bold text-neutral-700">{nodes.length}</p>
          <p className="text-xs text-neutral-600 mt-1">People mapped</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-2xl font-bold text-neutral-700">{(data.clusters || []).length}</p>
          <p className="text-xs text-neutral-600 mt-1">Clusters</p>
        </div>
      </div>
      {presentLevels.map(level => {
        const styles = LEVEL_STYLES[level] || LEVEL_STYLES['']
        return (
          <div key={level} className={`rounded-xl border p-3 ${styles.bg} ${styles.border}`}>
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${styles.dot}`} />
              <p className={`text-xs font-bold uppercase tracking-wider ${styles.text}`}>{level || 'Unknown'}</p>
              <span className="text-xs text-neutral-400">({byLevel[level].length})</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {byLevel[level].map((n, i) => {
                const icon = TYPE_ICONS[n.type || n.power_type] || ''
                return (
                  <div key={i} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border bg-white border-neutral-200 text-neutral-700">
                    {icon && <span>{icon}</span>}
                    <span className="font-semibold">{n.name}</span>
                    {n.title && <span className="text-neutral-400">· {n.title}</span>}
                    {n.actual_influence != null && (
                      <span className={`ml-1 font-bold ${scoreColor(n.actual_influence)}`}>
                        {n.actual_influence.toFixed(1)}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function InfluencersCard({ data }) {
  if (!data) return null
  return (
    <div className="space-y-4">
      {(data.influencers || []).map((inf, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-3">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-bold text-neutral-900">{inf.name}</p>
              <p className="text-xs text-neutral-500">{inf.title}</p>
            </div>
            <div className="flex gap-2 items-center">
              <Badge label={inf.type?.replace(/_/g, ' ')} type={inf.type === 'hidden_power' ? 'critical' : 'neutral'} />
              <span className={`text-lg font-bold ${scoreColor(inf.influence_score)}`}>{inf.influence_score?.toFixed(1)}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-neutral-400 mb-1">Formal Authority</p>
              <ScoreBar value={inf.formal_authority || 0} />
              <p className="text-xs text-neutral-600 mt-0.5">{inf.formal_authority?.toFixed(1)}/10</p>
            </div>
            <div>
              <p className="text-xs text-neutral-400 mb-1">Actual Influence</p>
              <ScoreBar value={inf.influence_score || 0} />
              <p className="text-xs text-neutral-600 mt-0.5">{inf.influence_score?.toFixed(1)}/10</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function GatekeepersCard({ data }) {
  if (!data || !data.gatekeepers?.length) return <p className="text-sm text-neutral-400">No significant gatekeepers detected</p>
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 mb-2">
        <div className="p-3 rounded-xl bg-orange-50 border border-orange-200 text-center">
          <p className="text-xl font-bold text-orange-600">{data.decision_gatekeepers || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Decision Gatekeepers</p>
        </div>
        <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-center">
          <p className="text-xl font-bold text-blue-600">{data.information_gatekeepers || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Information Gatekeepers</p>
        </div>
      </div>
      {data.gatekeepers.map((gk, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-2">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-bold text-neutral-900">{gk.name}</p>
              <p className="text-xs text-neutral-500">{gk.title}</p>
            </div>
            <Badge label={gk.gatekeeper_type} type="high" />
          </div>
          <p className="text-sm text-neutral-700">{gk.summary}</p>
        </div>
      ))}
    </div>
  )
}

function ResilienceCard({ data }) {
  if (!data) return null
  const spofs = data.single_points_of_failure || []
  const silos = data.knowledge_silos || []
  return (
    <div className="space-y-4">
      <div className={`p-4 rounded-xl border ${scoreBg(data.resilience_score)}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-neutral-700">Resilience Score</span>
          <Badge label={data.risk_level?.toUpperCase()} type={data.risk_level} />
        </div>
        <ScoreBar value={data.resilience_score} />
      </div>
      {spofs.map((spof, i) => (
        <div key={i} className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-2">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-bold text-neutral-900">{spof.name}</p>
              <p className="text-xs text-neutral-500">{spof.title}</p>
            </div>
            <Badge label={spof.risk_level?.toUpperCase()} type={spof.risk_level} />
          </div>
          <p className="text-sm text-neutral-700">{spof.reason}</p>
        </div>
      ))}
      {silos.map((silo, i) => (
        <div key={i} className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
          <div>
            <p className="font-semibold text-sm">{silo.domain}</p>
            <p className="text-xs text-neutral-500">Owned by: {silo.owned_by || silo.owner}</p>
          </div>
          <Badge label={silo.backup === false ? 'No Backup' : 'Has Backup'} type={silo.backup === false ? 'critical' : 'low'} />
        </div>
      ))}
    </div>
  )
}

function VelocityCard({ data }) {
  if (!data) return null
  const bottlenecks = data.bottlenecks || []
  const benchmarkColor = data.benchmark === 'fast' ? 'text-emerald-600' : data.benchmark === 'normal' ? 'text-amber-600' : 'text-red-600'
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 rounded-xl bg-neutral-50 border text-center">
          <p className="text-xs text-neutral-500 mb-1">Avg Decision Time</p>
          <p className={`text-xl font-bold ${benchmarkColor}`}>{data.avg_days?.toFixed(1)}</p>
          <p className="text-xs text-neutral-400">days</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border text-center">
          <p className="text-xs text-neutral-500 mb-1">Benchmark</p>
          <Badge label={data.benchmark?.toUpperCase()} type={data.benchmark === 'fast' ? 'low' : data.benchmark === 'normal' ? 'medium' : 'critical'} />
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border text-center">
          <p className="text-xs text-neutral-500 mb-1">Trend</p>
          {data.trend === 'worsening' ? <TrendingUp size={18} className="text-red-500 mx-auto" /> :
           data.trend === 'improving' ? <TrendingDown size={18} className="text-emerald-500 mx-auto" /> :
           <Minus size={18} className="text-amber-500 mx-auto" />}
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.trend || 'stable'}</p>
        </div>
      </div>
      {bottlenecks.map((b, i) => (
        <div key={i} className="p-3 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between">
          <div>
            <p className="font-semibold text-sm">{b.name}</p>
            <p className="text-xs text-neutral-600 mt-0.5">{b.reason}</p>
          </div>
          <p className="text-sm font-bold text-red-600">+{b.avg_delay_days?.toFixed(1)} days</p>
        </div>
      ))}
    </div>
  )
}

function DiagnosisCard({ data }) {
  if (!data) return null
  const rootCauses = data.root_causes || []
  return (
    <div className="space-y-4">
      {data.predicted_if_unchanged && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200">
          <p className="text-xs font-bold text-red-600 uppercase mb-2">⚠️ If Nothing Changes</p>
          <p className="text-sm text-neutral-700 leading-relaxed">{data.predicted_if_unchanged}</p>
        </div>
      )}
      {rootCauses.map((rc, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-bold text-neutral-900 capitalize">{rc.system}</p>
              <p className="text-sm text-neutral-700 mt-0.5">{rc.issue}</p>
            </div>
            <Badge label={rc.severity?.toUpperCase()} type={rc.severity} />
          </div>
          {rc.cascade_effects && (
            <p className="text-xs text-neutral-500 bg-neutral-100 rounded-lg px-3 py-2">
              <span className="font-bold">Cascade:</span> {rc.cascade_effects}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}

function PredictionsCard({ data }) {
  if (!data) return null
  const attrition = data.attrition_risks || []
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-xl bg-neutral-50 border text-center">
          <p className="text-xs text-neutral-500 mb-1">Health Forecast 6mo</p>
          <p className={`text-xl font-bold ${scoreColor(data.health_forecast_6mo)}`}>{data.health_forecast_6mo?.toFixed(1)}</p>
          <p className="text-xs text-neutral-400">/10</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border text-center">
          <p className="text-xs text-neutral-500 mb-1">Velocity Trend</p>
          <div className="flex justify-center mt-1">
            {data.velocity_forecast === 'worsening' ? <TrendingUp size={18} className="text-red-500" /> :
             data.velocity_forecast === 'improving' ? <TrendingDown size={18} className="text-emerald-500" /> :
             <Minus size={18} className="text-amber-500" />}
          </div>
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.velocity_forecast}</p>
        </div>
      </div>
      {attrition.map((a, i) => (
        <div key={i} className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold">{a.name}</p>
              <p className="text-xs text-neutral-500">{a.title} · {a.timeline}</p>
            </div>
            <p className="text-lg font-bold text-red-600">{((a.probability || 0) * 100).toFixed(0)}%</p>
          </div>
          <div className="w-full h-2 bg-red-200 rounded-full">
            <div className="h-full bg-red-500 rounded-full" style={{ width: `${(a.probability || 0) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}

function RecommendationsCard({ data }) {
  const recs = Array.isArray(data) ? data : (data?.recommendations || [])
  if (!recs.length) return <p className="text-sm text-neutral-400">No recommendations available</p>
  return (
    <div className="space-y-4">
      {recs.sort((a, b) => (a.priority_rank || 99) - (b.priority_rank || 99)).map((rec, i) => (
        <div key={i} className={`p-4 rounded-xl border space-y-3 ${rec.impact === 'high' && rec.effort === 'low' ? 'bg-emerald-50 border-emerald-200' : 'bg-neutral-50 border-neutral-200'}`}>
          {rec.impact === 'high' && rec.effort === 'low' && (
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600">
              <Zap size={12} /> Quick Win
            </div>
          )}
          <div className="flex items-start justify-between gap-3">
            <p className="font-bold text-neutral-900">{rec.title}</p>
            <div className="flex gap-1.5 flex-shrink-0">
              <Badge label={`Impact: ${rec.impact}`} type={rec.impact === 'high' ? 'critical' : 'neutral'} />
            </div>
          </div>
          <p className="text-sm text-neutral-600">{rec.description}</p>
          {rec.cost_if_ignored && (
            <div className="p-2 rounded-lg bg-red-50 border border-red-200">
              <p className="text-xs text-red-700"><span className="font-bold">Cost if ignored:</span> {rec.cost_if_ignored}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}


function DemoChat({ dashboard }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', text: `Hi! I'm the OrgLens AI. Ask me anything about this demo organization's analysis.` }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function send() {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    try {
      const context = {
        org_name: dashboard?.org_name,
        org_health: dashboard?.org_health,
        trust_gap: dashboard?.trust_gap,
        top_influencers: dashboard?.top_influencers?.influencers?.slice(0, 5),
        resilience: { score: dashboard?.resilience?.resilience_score, risk_level: dashboard?.resilience?.risk_level },
        decision_velocity: dashboard?.decision_velocity,
        system_diagnosis: { root_causes: dashboard?.system_diagnosis?.root_causes?.slice(0, 3) },
        predictions: dashboard?.predictions,
      }

      const analysisId = dashboard?.analysis_id
      const apiMessages = [
        ...messages.slice(-6).map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.text })),
        { role: 'user', content: userMsg }
      ]

      try {
        const { data } = await axios.post(`/api/dashboard/chat/${analysisId}`, { messages: apiMessages, context })
        setMessages(prev => [...prev, { role: 'assistant', text: data.reply }])
      } catch {
        const fallbacks = [
          `The analysis shows an org health score of ${dashboard?.org_health?.org_health_score?.toFixed(1)}/10. The main issues are: ${(dashboard?.system_diagnosis?.root_causes || []).map(r => r.issue).slice(0, 2).join(', ')}.`,
          `The biggest trust gap is: "${(dashboard?.trust_gap?.top_gaps || [])[0]?.claim || 'not specified'}". Reality: ${(dashboard?.trust_gap?.top_gaps || [])[0]?.reality || 'see analysis'}.`,
          `Decision velocity averages ${dashboard?.decision_velocity?.avg_days?.toFixed(1)} days — rated "${dashboard?.decision_velocity?.benchmark}". Main bottleneck: ${(dashboard?.decision_velocity?.bottlenecks || [])[0]?.name || 'not identified'}.`,
        ]
        setMessages(prev => [...prev, { role: 'assistant', text: fallbacks[messages.length % fallbacks.length] }])
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button onClick={() => setOpen(true)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-maroon-600 text-white shadow-neo-lg flex items-center justify-center hover:bg-maroon-700 transition-all ${open ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
        <Bot size={24} />
      </button>

      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] h-[480px] rounded-2xl border border-neutral-200 bg-white shadow-neo-lg flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 bg-maroon-600 text-white">
            <div className="flex items-center gap-2">
              <Bot size={18} />
              <span className="font-bold text-sm">OrgLens AI (Demo)</span>
            </div>
            <button onClick={() => setOpen(false)}><X size={18} /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-2 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${m.role === 'assistant' ? 'bg-maroon-100 text-maroon-600' : 'bg-neutral-100 text-neutral-600'}`}>
                  {m.role === 'assistant' ? <Bot size={14} /> : <User size={14} />}
                </div>
                <div className={`max-w-[85%] text-sm rounded-2xl px-3.5 py-2.5 leading-relaxed ${m.role === 'assistant' ? 'bg-neutral-100 text-neutral-800' : 'bg-maroon-600 text-white'}`}>
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-maroon-100 flex items-center justify-center"><Bot size={14} className="text-maroon-600" /></div>
                <div className="bg-neutral-100 rounded-2xl px-3.5 py-2.5 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          {messages.length <= 1 && (
            <div className="px-3 pb-2 flex flex-wrap gap-1.5">
              {['What is the health score?', 'Who has hidden power?', 'What should be fixed first?'].map((s, i) => (
                <button key={i} onClick={() => { setInput(s); setTimeout(send, 50) }}
                  className="text-xs px-2.5 py-1.5 rounded-full bg-maroon-50 text-maroon-700 border border-maroon-200 hover:bg-maroon-100">
                  {s}
                </button>
              ))}
            </div>
          )}
          <div className="p-3 border-t border-neutral-200 flex gap-2">
            <input value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask about this analysis…"
              className="flex-1 text-sm px-3 py-2 rounded-xl border border-neutral-200 focus:outline-none focus:border-maroon-500" />
            <button onClick={send} disabled={loading || !input.trim()}
              className="w-9 h-9 rounded-xl bg-maroon-600 text-white flex items-center justify-center hover:bg-maroon-700 disabled:opacity-40">
              <Send size={14} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}


export default function DemoPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dashboard, setDashboard] = useState(null)
  const [expanded, setExpanded] = useState({})
  const navigate = useNavigate()

  useEffect(() => { load() }, [])

  async function load() {
    try {
      const data = await fetchDemoReport()
      setDashboard(data)
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to load demo'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  const toggle = id => setExpanded(prev => ({ ...prev, [id]: !prev[id] }))

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 size={48} className="text-maroon-600 animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading demo analysis…</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4">
          <span className="text-5xl">🚧</span>
          <h2 className="font-bold text-2xl text-neutral-900">Demo not ready yet</h2>
          <p className="text-neutral-600 text-sm leading-relaxed">{error}</p>
          <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 text-left text-xs font-mono text-neutral-600 space-y-1">
            <p className="font-bold text-neutral-900 mb-2">To set up the demo:</p>
            <p>1. python seed_demo.py --zip your_data.zip</p>
            <p>2. Add printed env vars to .env</p>
            <p>3. Restart frontend</p>
          </div>
          <Link to="/" className="inline-block px-6 py-3 bg-maroon-600 text-white font-bold rounded-xl hover:bg-maroon-700 transition-all">
            Back to Home
          </Link>
        </div>
      </div>
    )
  }

  const d = dashboard

  const cards = [
    { id: 'org-health', icon: '💚', title: 'Organizational Health', subtitle: `Grade: ${d.org_health?.grade} — Composite vitality score`, score: d.org_health?.org_health_score, content: <OrgHealthCard data={d.org_health} /> },
    { id: 'trust-gap', icon: '📊', title: 'Trust Gap Analysis', subtitle: `${d.trust_gap?.claims_analyzed || 0} claims analyzed`, score: d.trust_gap?.trust_gap_score, scoreInvert: true, content: <TrustGapCard data={d.trust_gap} /> },
    { id: 'power-structure', icon: '🕸️', title: 'Power Structure', subtitle: `${d.power_structure?.nodes?.length || 0} people mapped — ${d.power_structure?.hidden_powers || 0} hidden powers`, content: <PowerStructureCard data={d.power_structure} /> },
    { id: 'influencers', icon: '⭐', title: 'Top Influencers', subtitle: `${d.top_influencers?.total_analyzed || 0} analyzed`, content: <InfluencersCard data={d.top_influencers} /> },
    { id: 'gatekeepers', icon: '🚪', title: 'Gatekeepers', subtitle: `${d.gatekeepers?.gatekeepers?.length || 0} identified`, content: <GatekeepersCard data={d.gatekeepers} /> },
    { id: 'resilience', icon: '💪', title: 'Resilience Score', subtitle: `Risk: ${d.resilience?.risk_level?.toUpperCase()}`, score: d.resilience?.resilience_score, content: <ResilienceCard data={d.resilience} /> },
    { id: 'velocity', icon: '⚡', title: 'Decision Velocity', subtitle: `${d.decision_velocity?.avg_days?.toFixed(1)} days avg — ${d.decision_velocity?.benchmark}`, content: <VelocityCard data={d.decision_velocity} /> },
    { id: 'diagnosis', icon: '🔍', title: 'System Diagnosis', subtitle: `${d.system_diagnosis?.root_causes?.length || 0} root causes`, content: <DiagnosisCard data={d.system_diagnosis} /> },
    { id: 'predictions', icon: '🔮', title: 'Predictions', subtitle: `${d.predictions?.attrition_risks?.length || 0} attrition risks`, score: d.predictions?.health_forecast_6mo, content: <PredictionsCard data={d.predictions} /> },
    { id: 'recommendations', icon: '💡', title: 'Recommendations', subtitle: `${(Array.isArray(d.recommendations) ? d.recommendations : d.recommendations?.recommendations || []).length} action items`, content: <RecommendationsCard data={d.recommendations} /> },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Demo banner */}
      <div className="sticky top-0 z-40 bg-maroon-600 text-white px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-lg">🔍</span>
          <div>
            <p className="font-bold text-sm">Demo Mode — Sample Organization</p>
            <p className="text-xs text-maroon-200">This is real analysis run on anonymized sample data. No login required.</p>
          </div>
        </div>
        <Link to="/register"
          className="px-4 py-2 rounded-lg bg-white text-maroon-700 font-bold text-sm hover:bg-maroon-50 transition-all shadow-neo-sm">
          Try with your data →
        </Link>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Title */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-maroon-600 flex items-center justify-center text-white text-lg shadow-neo-sm">📊</div>
            <div>
              <h1 className="font-bold text-2xl text-neutral-900">{d.org_name} — Analysis Dashboard</h1>
              <p className="text-sm text-neutral-500 mt-0.5">{d.messages_analyzed} messages analyzed</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Org Health',         value: d.org_health?.org_health_score?.toFixed(1),    unit: '/10',   invert: false },
            { label: 'Trust Gap',          value: d.trust_gap?.trust_gap_score?.toFixed(1),      unit: '/10',   invert: true  },
            { label: 'Resilience',         value: d.resilience?.resilience_score?.toFixed(1),    unit: '/10',   invert: false },
            { label: 'Decision Velocity',  value: d.decision_velocity?.avg_days?.toFixed(1),     unit: ' days', invert: true  },
          ].map(({ label, value, unit, invert }) => (
            <div key={label} className="p-4 rounded-2xl border border-neutral-200 bg-white shadow-neo-sm text-center">
              <p className="text-xs text-neutral-500 mt-1">{label}</p>
              <p className={`text-xl font-bold mt-0.5 ${scoreColor(parseFloat(value || 0), invert)}`}>
                {value || 'N/A'}<span className="text-sm font-normal text-neutral-400">{unit}</span>
              </p>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          {cards.map(({ id, icon, title, subtitle, score, scoreInvert, content }) => (
            <AnalysisCard key={id} icon={icon} title={title} subtitle={subtitle}
              score={score} scoreInvert={scoreInvert}
              expanded={!!expanded[id]} onToggle={() => toggle(id)}>
              {content}
            </AnalysisCard>
          ))}
        </div>

        <div className="flex justify-center mt-8 mb-8">
          <button
            onClick={() => navigate(`/org/${d.org_id}/dashboard/${d.analysis_id}/deep-dive`)}
            className="px-6 py-3 rounded-xl bg-neutral-900 text-white font-bold text-sm hover:bg-neutral-800 shadow-neo-md hover:shadow-neo-lg transition-all">
            ⚡ Deep Dive Analysis
          </button>
        </div>

        <div className="mt-8 rounded-2xl border border-maroon-200 bg-maroon-50 p-8 text-center space-y-4">
          <h3 className="font-bold text-xl text-neutral-900">Ready to analyze your own organization?</h3>
          <p className="text-neutral-600 text-sm">Upload your Slack exports, Gmail data, or employee CSV — get insights in minutes.</p>
          <Link to="/register"
            className="inline-block px-8 py-3 bg-maroon-600 text-white font-bold rounded-xl hover:bg-maroon-700 transition-all shadow-neo-md">
            Start Free →
          </Link>
        </div>
      </div>

      <DemoChat dashboard={dashboard} />
    </div>
  )
}
