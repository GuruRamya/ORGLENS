import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, Share2, Loader2, ChevronDown, ChevronUp,
  Bot, X, Send, MessageCircle, User, Sparkles, AlertTriangle,
  TrendingUp, TrendingDown, Minus, Shield, Zap, Users, Network,
  Eye, Clock, Target, Activity, Brain, BarChart3
} from 'lucide-react'
import { getDashboardReport, getOrganization } from '../api'
import { classifyPowerNodes } from '../api'
import { chatWithAnalysis } from '../api'
import { ContradictionCard } from '../components/Cards/ContradictionCard'
import { PositiveSignalsCard } from '../components/Cards/PositiveSignalCard'
import { ArchetypeCard } from '../components/Cards/ArchetypeCard'
import { DataQualityCard } from '../components/Cards/DataQualityCard'


function scoreColor(score, invert = false) {
  const s = invert ? 10 - score : score
  if (s >= 7.5) return 'text-emerald-600'
  if (s >= 5) return 'text-amber-600'
  return 'text-red-600'
}

function scoreBg(score, invert = false) {
  const s = invert ? 10 - score : score
  if (s >= 7.5) return 'bg-emerald-50 border-emerald-200'
  if (s >= 5) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}

function ScoreBar({ value, max = 10, invert = false }) {
  const pct = (value / max) * 100
  const color = (() => {
    const s = invert ? 10 - value : value
    if (s >= 7.5) return 'bg-emerald-500'
    if (s >= 5) return 'bg-amber-500'
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
    high: 'bg-orange-100 text-orange-700 border-orange-200',
    medium: 'bg-amber-100 text-amber-700 border-amber-200',
    low: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    neutral: 'bg-neutral-100 text-neutral-600 border-neutral-200',
    info: 'bg-blue-100 text-blue-700 border-blue-200',
  }
  return (
    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${styles[type] || styles.neutral}`}>
      {label}
    </span>
  )
}

function EvidenceQuote({ text }) {
  if (!text) return null
  return (
    <blockquote className="mt-2 pl-3 border-l-2 border-maroon-300 text-xs text-neutral-500 italic leading-relaxed break-words whitespace-pre-wrap">
      "{text}"
    </blockquote>
  )
}

function SectionHeader({ icon, title, subtitle, score, scoreInvert }) {
  return (
    <div className="flex items-start justify-between mb-5 pb-4 border-b border-neutral-100">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-bold text-base text-neutral-900">{title}</h3>
          {subtitle && <p className="text-xs text-neutral-500 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {score !== undefined && (
        <div className="text-right">
          <p className={`text-2xl font-bold ${scoreColor(score, scoreInvert)}`}>
            {score.toFixed(1)}
          </p>
          <p className="text-xs text-neutral-400">/ 10</p>
        </div>
      )}
    </div>
  )
}


function AnalysisCard({ id, icon, title, subtitle, score, scoreInvert, expanded, onToggle, children, accent }) {
  const accentBorder = accent === 'red' ? 'border-red-200' : 'border-neutral-200'
  const accentBg = accent === 'red' ? 'bg-red-50' : 'bg-white'
  return (
    <div className={`rounded-2xl border ${accentBorder} ${accentBg} shadow-neo-sm hover:shadow-neo-md transition-all duration-300`}>
      <button
        onClick={onToggle}
        className="w-full text-left p-6 flex items-center justify-between"
      >
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
          {expanded ? <ChevronUp size={18} className="text-neutral-400" /> : <ChevronDown size={18} className="text-neutral-400" />}
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
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const breakdown = data.health_breakdown || {}
  return (
    <div className="space-y-5">
      <p className="text-sm text-neutral-700 leading-relaxed">{data.summary}</p>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(breakdown).map(([key, val]) => (
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
        <p className="text-xs text-neutral-500 mt-1">
          {data.org_health_score >= 7.5 ? 'Healthy — continue current practices'
            : data.org_health_score >= 5 ? 'At risk — address key issues soon'
            : 'Critical — immediate intervention needed'}
        </p>
      </div>
    </div>
  )
}

function TrustGapCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const claims = data.top_gaps || data.claims || []
  const mlEvidence = data.ml_evidence || {}

  return (
    <div className="space-y-5">
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
          <div className="flex justify-center">
            {data.trend === 'widening' ? <TrendingUp size={18} className="text-red-500" /> :
             data.trend === 'narrowing' ? <TrendingDown size={18} className="text-emerald-500" /> :
             <Minus size={18} className="text-amber-500" />}
          </div>
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.trend || 'stable'}</p>
        </div>
      </div>

      {claims.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider">What They Claim vs. Reality</p>
          {claims.map((claim, i) => (
            <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-2">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-xs font-bold text-neutral-500 uppercase">Claim</p>
                  <p className="text-sm text-neutral-800 mt-0.5">{claim.claim}</p>
                </div>
                <Badge label={`Gap: ${Number(claim.gap || 0).toFixed(1)}`} type={claim.gap >= 7 ? 'critical' : claim.gap >= 5 ? 'high' : 'medium'} />
              </div>
              <div>
                <p className="text-xs font-bold text-red-600 uppercase">Reality</p>
                <p className="text-sm text-neutral-700 mt-0.5">{claim.reality}</p>
              </div>
              {claim.evidence && <EvidenceQuote text={claim.evidence} />}
              <ScoreBar value={claim.gap || 0} invert />
            </div>
          ))}
        </div>
      )}

      {(mlEvidence.comp_inversion_count > 0 || mlEvidence.promotion_complaints > 0) && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200">
          <p className="text-xs font-bold text-red-700 uppercase mb-2">ML Signal Evidence</p>
          {mlEvidence.comp_inversion_count > 0 && (
            <p className="text-sm text-red-700">⚠️ {mlEvidence.comp_inversion_count} compensation inversion complaints detected</p>
          )}
          {mlEvidence.promotion_complaints > 0 && (
            <p className="text-sm text-red-700 mt-1">⚠️ {mlEvidence.promotion_complaints} promotion fairness complaints detected</p>
          )}
          {mlEvidence.escalation_rate > 0.1 && (
            <p className="text-sm text-red-700 mt-1">⚠️ High escalation rate ({(mlEvidence.escalation_rate * 100).toFixed(1)}%)</p>
          )}
        </div>
      )}
    </div>
  )
}


async function classifyNodesWithML(nodes) {
  if (!nodes || nodes.length === 0) return []
  
  const seen = new Set()
  const unique = nodes.filter(n => {
    if (!n?.name) return false
    const k = n.name.toLowerCase().trim()
    if (seen.has(k)) return false
    seen.add(k)
    return true
  })

  try {
    return await classifyPowerNodes(unique)
  } catch {
    return unique.map(node => ({
      ...node,
      level: node.level || deriveLevel(node),
      power_type: node.type || deriveType(node),
    }))
  }
}

function deriveLevel(node) {
  const t = (node.title || '').toLowerCase()
  if (/\b(ceo|cfo|cto|coo|cpo|chro|cmo|cro|president|co-founder)\b/.test(t)) return 'C-Suite'
  if (/\b(vp|vice president|svp|evp)\b/.test(t)) return 'VP'
  if (/\bdirector\b/.test(t)) return 'Director'
  if (/\b(manager|mgr|team lead|eng lead|tech lead)\b/.test(t)) return 'Manager'
  if (/\b(senior|sr\.?|staff|principal|architect)\b/.test(t)) return 'Senior IC'
  if (t) return 'IC'
  return 'Unknown'
}

function deriveType(node) {
  const fa = node.formal_authority ?? 0
  const ai = node.actual_influence ?? 0
  if (ai - fa > 1.5) return 'hidden_power'
  if (fa >= 7.5 && Math.abs(ai - fa) <= 1.5) return 'formal_leader'
  if (fa - ai > 1.5) return 'ignored_authority'
  return 'neutral'
}

const TYPE_ICONS = {
  hidden_power: '⚡',
  formal_leader: '👑',
  ignored_authority: '⚠️',
  gatekeeper: '🚪',
}

const LEVEL_ORDER = ['C-Suite', 'VP', 'Director', 'Manager', 'Senior IC', 'IC', 'Unknown']

const LEVEL_STYLES = {
  'C-Suite':   { bg: 'bg-red-50',     border: 'border-red-200',     dot: 'bg-red-600',     text: 'text-red-700' },
  'VP':        { bg: 'bg-blue-50',    border: 'border-blue-200',    dot: 'bg-blue-500',    text: 'text-blue-700' },
  'Director':  { bg: 'bg-purple-50',  border: 'border-purple-200',  dot: 'bg-purple-500',  text: 'text-purple-700' },
  'Manager':   { bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-500', text: 'text-emerald-700' },
  'Senior IC': { bg: 'bg-amber-50',   border: 'border-amber-200',   dot: 'bg-amber-500',   text: 'text-amber-700' },
  'IC':        { bg: 'bg-neutral-50', border: 'border-neutral-200', dot: 'bg-neutral-400', text: 'text-neutral-600' },
  'Unknown':   { bg: 'bg-neutral-50', border: 'border-neutral-200', dot: 'bg-neutral-300', text: 'text-neutral-500' },
}

function StatBox({ label, count, colorClass, onClick, active }) {
  const variants = {
    'hidden-power':    { box: 'bg-red-50 border-red-200',     num: 'text-red-600',     activeBorder: 'ring-2 ring-red-400' },
    'formal-leader':   { box: 'bg-emerald-50 border-emerald-200', num: 'text-emerald-600', activeBorder: 'ring-2 ring-emerald-400' },
    'gatekeeper':      { box: 'bg-blue-50 border-blue-200',   num: 'text-blue-600',    activeBorder: 'ring-2 ring-blue-400' },
    'ignored-auth':    { box: 'bg-amber-50 border-amber-200', num: 'text-amber-600',   activeBorder: 'ring-2 ring-amber-400' },
  }
  const v = variants[colorClass]
  return (
    <button
      onClick={onClick}
      className={`p-3 rounded-xl border text-center cursor-pointer transition-all duration-150 hover:-translate-y-0.5 ${v.box} ${active ? v.activeBorder : ''}`}
    >
      <p className={`text-2xl font-bold ${v.num}`}>{count}</p>
      <p className="text-xs text-neutral-600 mt-1">{label}</p>
    </button>
  )
}

function NamePopup({ type, names, colorClass }) {
  if (!names || names.length === 0) return null
  const variants = {
    'hidden-power':  { bg: 'bg-red-50 border-red-200',     title: 'text-red-700',     pill: 'bg-red-100 text-red-800 border-red-200' },
    'formal-leader': { bg: 'bg-emerald-50 border-emerald-200', title: 'text-emerald-700', pill: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    'gatekeeper':    { bg: 'bg-blue-50 border-blue-200',   title: 'text-blue-700',    pill: 'bg-blue-100 text-blue-800 border-blue-200' },
    'ignored-auth':  { bg: 'bg-amber-50 border-amber-200', title: 'text-amber-700',   pill: 'bg-amber-100 text-amber-800 border-amber-200' },
  }
  const labels = {
    'hidden-power': 'Hidden powers',
    'formal-leader': 'Formal leaders',
    'gatekeeper': 'Gatekeepers',
    'ignored-auth': 'Ignored authorities',
  }
  const v = variants[colorClass]
  return (
    <div className={`rounded-xl border p-3 mb-2 ${v.bg}`}>
      <p className={`text-xs font-bold uppercase tracking-wider mb-2 ${v.title}`}>{labels[colorClass]}</p>
      <div className="flex flex-wrap gap-1.5">
        {names.map((n, i) => (
          <span key={i} className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${v.pill}`}>
            {n.name}{n.title ? ` · ${n.title}` : ''}
          </span>
        ))}
      </div>
    </div>
  )
}


export function PowerStructureCard({ data }) {
  const [mlNodes, setMlNodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [openPopup, setOpenPopup] = useState(null) 

  useEffect(() => {
    if (!data?.nodes?.length) {
      setLoading(false)
      return
    }

    const seen = new Set()
    const unique = (data.nodes || []).filter(n => {
      if (!n?.name) return false
      const k = n.name.toLowerCase().trim()
      if (seen.has(k)) return false
      seen.add(k)
      return true
    })

    const classified = unique.map(node => ({
      ...node,
      level: node.level || deriveLevel(node),
      power_type: node.type || deriveType(node),
    }))

    setMlNodes(classified)
    setLoading(false)
  }, [data])

  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>

  const byType = {
    'hidden-power':  mlNodes.filter(n => n.power_type === 'hidden_power'),
    'formal-leader': mlNodes.filter(n => n.power_type === 'formal_leader'),
    'gatekeeper':    mlNodes.filter(n => n.power_type === 'gatekeeper'),
    'ignored-auth':  mlNodes.filter(n => n.power_type === 'ignored_authority'),
  }

  const byLevel = {}
  for (const node of mlNodes) {
    const lvl = LEVEL_ORDER.includes(node.level) ? node.level : 'Unknown'
    if (!byLevel[lvl]) byLevel[lvl] = []
    byLevel[lvl].push(node)
  }
  const presentLevels = LEVEL_ORDER.filter(l => byLevel[l]?.length > 0)

  const handleBoxClick = (type) => {
    setOpenPopup(prev => prev === type ? null : type)
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-neutral-500 py-4">
        <div className="w-4 h-4 border-2 border-neutral-200 border-t-neutral-500 rounded-full animate-spin" />
        Classifying org levels and power types…
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-2">
          Power types — click to see names
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatBox label="Hidden powers"       count={byType['hidden-power'].length}  colorClass="hidden-power"  onClick={() => handleBoxClick('hidden-power')}  active={openPopup === 'hidden-power'} />
          <StatBox label="Formal leaders"      count={byType['formal-leader'].length} colorClass="formal-leader" onClick={() => handleBoxClick('formal-leader')} active={openPopup === 'formal-leader'} />
          <StatBox label="Gatekeepers"         count={byType['gatekeeper'].length}    colorClass="gatekeeper"    onClick={() => handleBoxClick('gatekeeper')}    active={openPopup === 'gatekeeper'} />
          <StatBox label="Ignored authorities" count={byType['ignored-auth'].length}  colorClass="ignored-auth"  onClick={() => handleBoxClick('ignored-auth')}  active={openPopup === 'ignored-auth'} />
        </div>
      </div>

      {openPopup && (
        <NamePopup
          type={openPopup}
          names={byType[openPopup]}
          colorClass={openPopup}
        />
      )}

      <div className="border-t border-neutral-100" />

      <div>
        <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-3">
          Org structure — by level
        </p>
        {presentLevels.length === 0 ? (
          <p className="text-xs text-neutral-400 text-center py-4">
            No people to display — upload employee CSV to resolve names
          </p>
        ) : (
          <div className="space-y-3">
            {presentLevels.map(level => {
              const styles = LEVEL_STYLES[level] || LEVEL_STYLES['Unknown']
              const members = byLevel[level]
              return (
                <div key={level} className={`rounded-xl border p-3 ${styles.bg} ${styles.border}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${styles.dot}`} />
                    <p className={`text-xs font-bold uppercase tracking-wider ${styles.text}`}>{level}</p>
                    <span className="text-xs text-neutral-400">({members.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {members.map((n, i) => {
                      const icon = TYPE_ICONS[n.power_type] || ''
                      const isNotable = n.power_type && n.power_type !== 'neutral'
                      return (
                        <div
                          key={i}
                          title={[n.title, n.department, n.power_type?.replace(/_/g, ' ')].filter(Boolean).join(' · ')}
                          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border bg-white ${isNotable ? 'border-maroon-200 text-maroon-800' : 'border-neutral-200 text-neutral-700'}`}
                        >
                          {icon && <span>{icon}</span>}
                          <span className="font-semibold">{n.name}</span>
                          {n.title && <span className="text-neutral-400 font-normal">· {n.title}</span>}
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
            <p className="text-xs text-neutral-400 text-center">
              ⚡ hidden power · 👑 formal leader · ⚠️ ignored authority · 🚪 gatekeeper
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

function InfluencersCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const influencers = data.influencers || []
  return (
    <div className="space-y-4">
      {influencers.map((inf, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-3">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-bold text-neutral-900">{inf.name}</p>
              <p className="text-xs text-neutral-500">{inf.title}</p>
            </div>
            <div className="flex gap-2 items-center">
              <Badge label={inf.type?.replace(/_/g, ' ')} type={inf.type === 'hidden_power' ? 'critical' : inf.type === 'ignored_authority' ? 'high' : 'neutral'} />
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

          {inf.evidence?.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-xs font-bold text-neutral-500 uppercase">Evidence</p>
              {inf.evidence.slice(0, 3).map((ev, j) => (
                <div key={j} className="p-2.5 rounded-lg bg-white border border-neutral-200">
                  {ev.behavior && <p className="text-xs text-neutral-700"><span className="font-semibold">Behavior:</span> {ev.behavior}</p>}
                  {ev.impact && <p className="text-xs text-neutral-600 mt-0.5"><span className="font-semibold">Impact:</span> {ev.impact}</p>}
                  {ev.source && <p className="text-xs text-neutral-400 mt-0.5">Source: {ev.source}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function GatekeepersCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const gatekeepers = data.gatekeepers || []
  
  if (gatekeepers.length === 0) {
    return (
      <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
        <p className="text-sm text-neutral-600">No significant gatekeepers detected</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 rounded-xl bg-orange-50 border border-orange-200 text-center">
          <p className="text-xl font-bold text-orange-600">{data.decision_gatekeepers || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Decision Gatekeepers</p>
        </div>
        <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-center">
          <p className="text-xl font-bold text-blue-600">{data.information_gatekeepers || 0}</p>
          <p className="text-xs text-neutral-600 mt-1">Information Gatekeepers</p>
        </div>
      </div>

      {gatekeepers.map((gk, i) => (
        <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-bold text-neutral-900">{gk.name}</p>
              <p className="text-xs text-neutral-500">{gk.title}</p>
            </div>
            <Badge label={gk.gatekeeper_type} type="high" />
          </div>

          <p className="text-sm text-neutral-700">{gk.summary}</p>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-2.5 rounded-lg bg-white border border-neutral-200">
              <p className="text-xs text-neutral-400 mb-1">Credibility</p>
              <p className="text-xs text-emerald-600 font-semibold">{((gk.credibility_score || 0) * 100).toFixed(0)}%</p>
            </div>
            <div className="p-2.5 rounded-lg bg-white border border-neutral-200">
              <p className="text-xs text-neutral-400 mb-1">Power Play</p>
              <p className="text-xs text-red-600 font-semibold">{((gk.power_play_score || 0) * 100).toFixed(0)}%</p>
            </div>
          </div>

          {gk.domains?.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {gk.domains.slice(0, 3).map((d, j) => <Badge key={j} label={d} type="info" />)}
            </div>
          )}

          {gk.specific_examples?.length > 0 && (
            <EvidenceQuote text={gk.specific_examples[0]} />
          )}
        </div>
      ))}
      {gatekeepers.length > 3 && (
        <p className="text-xs text-neutral-500 text-center">+{gatekeepers.length - 3} more gatekeepers</p>
      )}
    </div>
  )
}

function ResilienceCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const spofs = data.single_points_of_failure || []
  const silos = data.knowledge_silos || []
  const mlSigs = data.ml_signals || {}

  return (
    <div className="space-y-5">
      <div className={`p-4 rounded-xl border ${scoreBg(data.resilience_score)}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-neutral-700">Resilience Score</span>
          <Badge label={data.risk_level?.toUpperCase()} type={data.risk_level === 'critical' ? 'critical' : data.risk_level === 'high' ? 'high' : data.risk_level === 'medium' ? 'medium' : 'low'} />
        </div>
        <ScoreBar value={data.resilience_score} />
        <p className="text-xs text-neutral-500 mt-1">
          {data.resilience_score <= 3 ? 'Extremely fragile — losing one person could collapse key operations'
            : data.resilience_score <= 5 ? 'Fragile — significant dependencies on individuals'
            : data.resilience_score <= 7 ? 'Moderate — some redundancy but key gaps remain'
            : 'Resilient — well distributed knowledge and authority'}
        </p>
      </div>

      {spofs.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-bold text-red-600 uppercase tracking-wider">⚠️ Single Points of Failure — If these people leave…</p>
          {spofs.map((spof, i) => (
            <div key={i} className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-bold text-neutral-900">{spof.name}</p>
                  <p className="text-xs text-neutral-500">{spof.title}</p>
                </div>
                <div className="text-right">
                  <Badge label={spof.risk_level?.toUpperCase()} type={spof.risk_level} />
                  <p className="text-xs text-neutral-500 mt-1">Departure prob: <strong>{((spof.estimated_departure_probability || 0) * 100).toFixed(0)}%</strong></p>
                </div>
              </div>
              <p className="text-sm text-neutral-700">{spof.reason}</p>
              <div>
                <p className="text-xs text-neutral-500 mb-1">Impact if leaves</p>
                <ScoreBar value={spof.impact_if_leaves || 0} invert />
              </div>
              <p className="text-sm text-neutral-700">{spof.reason}</p>
              {spof.knowledge_domains?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {spof.knowledge_domains.map((d, j) => <Badge key={j} label={d} type="info" />)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {silos.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-amber-600 uppercase tracking-wider">Knowledge Silos — Single-person owned domains</p>
          {silos.map((silo, i) => (
            <div key={i} className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
              <div>
                <p className="font-semibold text-sm text-neutral-900">{silo.domain}</p>
                <p className="text-xs text-neutral-500">Owned by: {silo.owned_by || silo.owner}</p>
              </div>
              <Badge label={silo.backup === false ? 'No Backup' : 'Has Backup'} type={silo.backup === false ? 'critical' : 'low'} />
            </div>
          ))}
        </div>
      )}

      {(mlSigs.ownership_gaps > 0 || mlSigs.departure_mentions > 0) && (
        <div className="p-3 rounded-xl bg-neutral-100 border border-neutral-200">
          <p className="text-xs font-bold text-neutral-500 uppercase mb-2">ML Signals Detected</p>
          {mlSigs.ownership_gaps > 0 && <p className="text-xs text-neutral-600">• {mlSigs.ownership_gaps} ownership gap mentions in communications</p>}
          {mlSigs.departure_mentions > 0 && <p className="text-xs text-red-600 mt-0.5">• {mlSigs.departure_mentions} departure / resignation mentions detected</p>}
        </div>
      )}
    </div>
  )
}

function VelocityCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const bottlenecks = data.bottlenecks || data.bottleneck_persons || []
  const mlSigs = data.ml_signals || {}

  const benchmarkColor = data.benchmark === 'fast' ? 'text-emerald-600' : data.benchmark === 'normal' ? 'text-amber-600' : 'text-red-600'

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Avg Decision Time</p>
          <p className={`text-xl font-bold ${benchmarkColor}`}>{data.avg_days?.toFixed(1)}</p>
          <p className="text-xs text-neutral-400">days</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Benchmark</p>
          <Badge label={data.benchmark?.toUpperCase()} type={data.benchmark === 'fast' ? 'low' : data.benchmark === 'normal' ? 'medium' : 'critical'} />
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Trend</p>
          <div className="flex justify-center">
            {data.trend === 'worsening' ? <TrendingUp size={18} className="text-red-500" /> :
             data.trend === 'improving' ? <TrendingDown size={18} className="text-emerald-500" /> :
             <Minus size={18} className="text-amber-500" />}
          </div>
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.trend || 'stable'}</p>
        </div>
      </div>

      {bottlenecks.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-red-600 uppercase tracking-wider">Decision Bottlenecks</p>
          {bottlenecks.map((b, i) => (
            <div key={i} className="p-3 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between">
              <div>
                <p className="font-semibold text-sm text-neutral-900">{b.name}</p>
                <p className="text-xs text-neutral-600 mt-0.5">{b.reason}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-red-600">+{b.avg_delay_days?.toFixed(1)} days</p>
                <p className="text-xs text-neutral-400">avg delay</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {(mlSigs.delay_message_count > 0 || mlSigs.approval_chain_count > 0) && (
        <div className="p-3 rounded-xl bg-neutral-100 border border-neutral-200">
          <p className="text-xs font-bold text-neutral-500 uppercase mb-2">ML Signal Evidence</p>
          {mlSigs.delay_message_count > 0 && <p className="text-xs text-neutral-600">• {mlSigs.delay_message_count} messages explicitly mention delays or blocks</p>}
          {mlSigs.approval_chain_count > 0 && <p className="text-xs text-neutral-600 mt-0.5">• {mlSigs.approval_chain_count} messages waiting for approvals detected</p>}
          {mlSigs.domain_delays && Object.keys(mlSigs.domain_delays).length > 0 && (
            <div className="mt-2">
              <p className="text-xs font-semibold text-neutral-500 mb-1">Delays by domain:</p>
              {Object.entries(mlSigs.domain_delays).map(([domain, count]) => (
                <p key={domain} className="text-xs text-neutral-600">• {domain}: {count} delay mentions</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function DiagnosisCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const rootCauses = data.root_causes || []
  const whoProfit = data.who_profits || data.who_profits_from_gaps || []

  return (
    <div className="space-y-5">
      {data.predicted_if_unchanged && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200">
          <p className="text-xs font-bold text-red-600 uppercase mb-2">⚠️ If Nothing Changes — 6-12 Month Forecast</p>
          <p className="text-sm text-neutral-700 leading-relaxed break-words">{data.predicted_if_unchanged}</p>
        </div>
      )}

      {rootCauses.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider">Root Causes Identified</p>
          {rootCauses.map((rc, i) => (
            <div key={i} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-bold text-neutral-900 capitalize">{rc.system}</p>
                  <p className="text-sm text-neutral-700 mt-0.5 break-words">{rc.issue}</p>
                </div>
                <div className="flex gap-1.5 flex-shrink-0">
                  <Badge label={rc.severity?.toUpperCase()} type={rc.severity} />
                  <Badge label={rc.fixable ? 'Fixable' : 'Structural'} type={rc.fixable ? 'low' : 'high'} />
                </div>
              </div>
              {rc.evidence && <EvidenceQuote text={rc.evidence} />}
              {rc.cascade_effects && (
                <p className="text-xs text-neutral-500 bg-neutral-100 rounded-lg px-3 py-2 break-words">
                  <span className="font-bold">Cascade Effect:</span> {rc.cascade_effects}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {whoProfit.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-amber-600 uppercase tracking-wider">Who Benefits from Current Dysfunction</p>
          {whoProfit.map((p, i) => (
            <div key={i} className="p-3 rounded-xl bg-amber-50 border border-amber-200">
              <p className="font-semibold text-sm text-neutral-900">{p.name}</p>
              <p className="text-xs text-neutral-600 mt-1">{p.how}</p>
              {p.motivation_to_maintain && (
                <Badge label={`Motivation: ${p.motivation_to_maintain}`} type={p.motivation_to_maintain === 'high' ? 'critical' : 'medium'} />
              )}
            </div>
          ))}
        </div>
      )}

      {data.dysfunction_cost_annual && (
        <div className="p-4 rounded-xl bg-neutral-900 text-white">
          <p className="text-xs text-neutral-400 uppercase mb-1">Estimated Annual Cost of Dysfunction</p>
          <p className="text-2xl font-bold text-red-400">{data.dysfunction_cost_annual}</p>
        </div>
      )}
    </div>
  )
}

function PredictionsCard({ data }) {
  if (!data) return <p className="text-neutral-400 text-sm">No data available</p>
  const attrition = data.attrition_risks || []
  const reversals = data.decision_reversal_risks || data.decision_reversals || []
  const keyRisks = data.key_risks || []

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Health Forecast 6mo</p>
          <p className={`text-xl font-bold ${scoreColor(data.health_forecast_6mo)}`}>{data.health_forecast_6mo?.toFixed(1)}</p>
          <p className="text-xs text-neutral-400">/10</p>
        </div>
        <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 text-center">
          <p className="text-xs text-neutral-500 mb-1">Velocity Trend</p>
          <div className="flex justify-center mt-1">
            {data.velocity_forecast === 'worsening' ? <TrendingUp size={18} className="text-red-500" /> :
             data.velocity_forecast === 'improving' ? <TrendingDown size={18} className="text-emerald-500" /> :
             <Minus size={18} className="text-amber-500" />}
          </div>
          <p className="text-xs font-semibold mt-0.5 capitalize">{data.velocity_forecast}</p>
        </div>
      </div>

      {attrition.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-bold text-red-600 uppercase tracking-wider">Attrition Risks</p>
          {attrition.map((a, i) => (
            <div key={i} className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-bold text-neutral-900">{a.name}</p>
                  <p className="text-xs text-neutral-500">{a.title} • {a.timeline}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-red-600">{((a.probability || 0) * 100).toFixed(0)}%</p>
                  <p className="text-xs text-neutral-400">probability</p>
                </div>
              </div>
              <div className="w-full h-2 bg-red-200 rounded-full">
                <div className="h-full bg-red-500 rounded-full" style={{ width: `${(a.probability || 0) * 100}%` }} />
              </div>
              {a.risk_factors?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {a.risk_factors.map((rf, j) => <Badge key={j} label={rf} type="high" />)}
                </div>
              )}
              {a.impact_if_leaves && (
                <p className="text-xs text-neutral-600"><span className="font-bold">Impact:</span> {a.impact_if_leaves}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {reversals.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-amber-600 uppercase tracking-wider">Decisions At Risk of Reversal</p>
          {reversals.map((r, i) => (
            <div key={i} className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-semibold text-neutral-900">{r.decision}</p>
                <p className="text-xs text-neutral-600 mt-0.5">{r.reason}</p>
              </div>
              <p className="text-sm font-bold text-amber-600 ml-3">{((r.reversal_probability || 0) * 100).toFixed(0)}%</p>
            </div>
          ))}
        </div>
      )}

      {keyRisks.length > 0 && (
        <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
          <p className="text-xs font-bold text-neutral-500 uppercase mb-2">Key Risks Ahead</p>
          {keyRisks.map((r, i) => (
            <p key={i} className="text-sm text-neutral-700 mt-1">• {r}</p>
          ))}
        </div>
      )}
    </div>
  )
}

function generateFallbackRecommendations(dashboardData) {
  const recs = []
  let id = 1

  const health      = dashboardData?.org_health
  const trustGap    = dashboardData?.trust_gap
  const resilience  = dashboardData?.resilience
  const velocity    = dashboardData?.decision_velocity
  const diagnosis   = dashboardData?.system_diagnosis
  const predictions = dashboardData?.predictions
  const influencers = dashboardData?.top_influencers?.influencers || []
  const gatekeepers = dashboardData?.gatekeepers?.gatekeepers || []
  const spofs       = dashboardData?.resilience?.single_points_of_failure || []

  if (trustGap && trustGap.trust_gap_score > 4) {
    recs.push({
      id: id++,
      title: 'Close the Trust Gap — Align actions with stated values',
      description: `The trust gap score is ${trustGap.trust_gap_score?.toFixed(1)}/10 (${trustGap.severity}). ` +
        `The organisation is making claims that its communication patterns contradict. ` +
        `Run a leadership workshop to audit the top ${trustGap.claims_analyzed || 3} gap areas and produce a concrete action plan within 30 days. ` +
        `Publish decisions openly, reduce approval chain length, and set measurable alignment targets quarterly.`,
      impact: trustGap.trust_gap_score > 7 ? 'critical' : 'high',
      effort: 'medium',
      timeline_weeks: 8,
      cost_estimate: '$2K–5K (facilitation)',
      expected_roi: '30–50% improvement in employee trust scores within 2 quarters',
      confidence: 0.80,
      cost_if_ignored: 'Continued talent flight risk and decision paralysis',
      priority_rank: 1,
      addresses: ['trust gap', 'alignment'],
    })
  }

  if (spofs && spofs.length > 0) {
    const top = spofs[0]
    recs.push({
      id: id++,
      title: `Succession plan for ${top.name || 'key person'}`,
      description: `${top.name || 'This person'} is a single point of failure with a ${((top.estimated_departure_probability || 0.65) * 100).toFixed(0)}% departure probability. ` +
        `Identify at least one successor, begin knowledge transfer sessions weekly, and document all domain expertise within 60 days. ` +
        `${top.knowledge_domains?.length ? `Critical domains: ${top.knowledge_domains.join(', ')}.` : ''} ` +
        `Without this, the organisation risks losing irreplaceable institutional knowledge.`,
      impact: top.risk_level === 'critical' ? 'critical' : 'high',
      effort: 'medium',
      timeline_weeks: 12,
      cost_estimate: '$0 (internal time)',
      expected_roi: `Eliminate ${((top.estimated_departure_probability || 0.65) * 100).toFixed(0)}% departure risk impact`,
      confidence: 0.85,
      cost_if_ignored: `Complete loss of ${top.name || "this person"}'s domain knowledge if they leave`,
      priority_rank: 2,
      addresses: ['resilience', 'knowledge silo'],
    })
  }

  if (velocity && velocity.avg_days > 14) {
    const bottleneck = (velocity.bottlenecks || velocity.bottleneck_persons || [])[0]
    recs.push({
      id: id++,
      title: `Streamline decision-making — cut ${velocity.avg_days?.toFixed(0)}-day average to under 10`,
      description: `Decisions currently take ${velocity.avg_days?.toFixed(1)} days on average (benchmark: ${velocity.benchmark}). ` +
        `Create a decision authority matrix: define which decisions can be made at each level without escalation. ` +
        (bottleneck ? `${bottleneck.name} is adding ~${bottleneck.avg_delay_days?.toFixed(1)} days of delay — consider delegating their approval role. ` : '') +
        `Implement async approval via documented criteria so teams are unblocked without synchronous sign-off.`,
      impact: velocity.avg_days > 25 ? 'critical' : 'high',
      effort: 'low',
      timeline_weeks: 4,
      cost_estimate: '$1K–2K',
      expected_roi: '40–60% reduction in decision cycle time',
      confidence: 0.82,
      cost_if_ignored: `$${Math.round(velocity.avg_days * 500)}+ weekly in blocked productivity`,
      priority_rank: 3,
      addresses: ['decision velocity', 'governance'],
    })
  }

  if (diagnosis && diagnosis.root_causes) {
    const rootCauses = diagnosis.root_causes || []
    rootCauses.slice(0, 2).forEach(rc => {
      if (rc) {
        recs.push({
          id: id++,
          title: `Fix ${rc.system} issue: ${rc.issue?.slice(0, 60)}${rc.issue?.length > 60 ? '…' : ''}`,
          description: `Root cause identified in ${rc.system}: ${rc.issue} ` +
            `${rc.cascade_effects ? `This cascades into: ${rc.cascade_effects}.` : ''} ` +
            `${rc.fixable ? 'This is fixable with targeted process changes.' : 'This is a structural issue requiring organisational redesign.'} ` +
            `Assign a task force to address this within the next sprint cycle.`,
          impact: rc.severity === 'critical' ? 'critical' : rc.severity === 'high' ? 'high' : 'medium',
          effort: rc.fixable ? 'low' : 'high',
          timeline_weeks: rc.fixable ? 6 : 16,
          cost_estimate: rc.fixable ? '$0–3K' : '$10K–30K',
          expected_roi: 'Reduction in cross-team friction and decision reversals',
          confidence: 0.75,
          cost_if_ignored: 'Compounding dysfunction and team burnout',
          priority_rank: id,
          addresses: [rc.system],
        })
      }
    })
  }

  if (influencers && influencers.length > 0) {
    const hiddenPowers = influencers.filter(i => i.type === 'hidden_power')
    if (hiddenPowers.length > 0) {
      const hp = hiddenPowers[0]
      recs.push({
        id: id++,
        title: `Formalise ${hp.name}'s authority — close the influence gap`,
        description: `${hp.name} (${hp.title}) has an actual influence score of ${hp.influence_score?.toFixed(1)}/10 ` +
          `but a formal authority of only ${hp.formal_authority?.toFixed(1)}/10. ` +
          `This misalignment creates confusion about who really decides things, causes resentment among formal leaders, ` +
          `and puts ${hp.name} at flight risk if their contribution goes unrecognised. ` +
          `Update their title/scope or formally redistribute decision rights within 4 weeks.`,
        impact: 'high',
        effort: 'low',
        timeline_weeks: 4,
        cost_estimate: '$0',
        expected_roi: 'Clarity on authority, reduced shadow decision-making',
        confidence: 0.88,
        cost_if_ignored: `${hp.name} may leave or become a political liability`,
        priority_rank: id,
        addresses: ['power structure', 'hidden power'],
      })
    }
  }

  if (predictions && predictions.attrition_risks) {
    const attritionRisks = predictions.attrition_risks || []
    if (attritionRisks.length > 0) {
      const highRisk = attritionRisks.filter(a => (a.probability || 0) > 0.5)
      if (highRisk.length > 0) {
        recs.push({
          id: id++,
          title: `Retention plan for ${highRisk.length} high-risk employee${highRisk.length > 1 ? 's' : ''}`,
          description: `${highRisk.map(a => a.name).join(', ')} ${highRisk.length > 1 ? 'are' : 'is'} at high attrition risk within the next 6–12 months. ` +
            `Schedule 1:1 career development conversations immediately. ` +
            `Identify unmet growth, compensation, or recognition gaps and address them within 30 days. ` +
            `Consider retention bonuses or role expansions for the highest-risk individuals.`,
          impact: 'critical',
          effort: 'low',
          timeline_weeks: 4,
          cost_estimate: '$5K–20K (retention bonus) or $0 (role change)',
          expected_roi: `Avoid ${highRisk.length}x replacement costs (typically 50–200% of annual salary each)`,
          confidence: 0.80,
          cost_if_ignored: `Loss of ${highRisk.length} key people and 3–6 months of productivity gap per departure`,
          priority_rank: id,
          addresses: ['attrition', 'resilience'],
        })
      }
    }
  }

  if (health && health.org_health_score < 6) {
    const lowest = Object.entries(health?.health_breakdown || {})
      .sort((a, b) => a[1] - b[1])
      .slice(0, 2)
      .map(([k]) => k.replace(/_/g, ' '))
    recs.push({
      id: id++,
      title: 'Organisational health recovery programme',
      description: `Overall health is ${health.org_health_score?.toFixed(1)}/10 (${health.grade}). ` +
        (lowest.length > 0 ? `The two lowest-scoring dimensions are ${lowest.join(' and ')}, which are dragging down the composite score. ` : '') +
        `Commission a 90-day improvement sprint targeting these dimensions. ` +
        `Set a monthly health check cadence and report progress to leadership to create accountability.`,
      impact: health.org_health_score < 4 ? 'critical' : 'high',
      effort: 'high',
      timeline_weeks: 12,
      cost_estimate: '$10K–25K',
      expected_roi: '+2 to +3 point improvement in org health score within 2 quarters',
      confidence: 0.70,
      cost_if_ignored: 'Continued performance degradation and talent attrition spiral',
      priority_rank: id,
      addresses: ['org health', ...lowest],
    })
  }

  if (recs.length === 0) {
    recs.push({
      id: id++,
      title: 'Conduct comprehensive organizational assessment',
      description: 'No critical issues were detected in the automated analysis, but this does not mean the organization is healthy. Schedule a 360-degree stakeholder review to identify blind spots in communication, decision-making, and team dynamics. This assessment should cover cross-functional collaboration, manager effectiveness, and career growth perception.',
      impact: 'medium',
      effort: 'medium',
      timeline_weeks: 4,
      cost_estimate: '$3K–8K',
      expected_roi: 'Proactive identification of emerging risks',
      confidence: 0.65,
      cost_if_ignored: 'Undetected cultural issues may emerge as crisis later',
      priority_rank: id,
      addresses: ['general health'],
    })
  }

  return recs.sort((a, b) => (a.priority_rank || 999) - (b.priority_rank || 999))
}

function RecommendationsCard({ data, dashboardData }) {
  const fromApi = Array.isArray(data) ? data : (data?.recommendations || [])
  const recs = fromApi.length > 0 ? fromApi : generateFallbackRecommendations(dashboardData)
  const isFallback = fromApi.length === 0 && recs.length > 0

  if (!recs.length) return <p className="text-neutral-400 text-sm">No recommendations available</p>

  const sorted = [...recs].sort((a, b) => (a.priority_rank || 999) - (b.priority_rank || 999))

  return (
    <div className="space-y-4">
      {sorted.map((rec, i) => (
        <div key={i} className={`p-4 rounded-xl border space-y-3 ${
          rec.impact === 'high' && rec.effort === 'low' ? 'bg-emerald-50 border-emerald-200' : 'bg-neutral-50 border-neutral-200'
        }`}>
          {rec.impact === 'high' && rec.effort === 'low' && (
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600">
              <Zap size={12} /> Quick Win — High impact, low effort
            </div>
          )}
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <p className="font-bold text-neutral-900">{rec.title}</p>
              <p className="text-sm text-neutral-600 mt-1 leading-relaxed">{rec.description}</p>
            </div>
            <div className="flex gap-1.5 flex-shrink-0">
              <Badge label={`Impact: ${rec.impact}`} type={rec.impact === 'high' ? 'critical' : rec.impact === 'medium' ? 'high' : 'neutral'} />
              <Badge label={`Effort: ${rec.effort}`} type={rec.effort === 'low' ? 'low' : rec.effort === 'medium' ? 'medium' : 'high'} />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
            {rec.timeline_weeks && (
              <div className="p-2 bg-white rounded-lg border border-neutral-200">
                <p className="text-neutral-400">Timeline</p>
                <p className="font-semibold text-neutral-700">{rec.timeline_weeks} weeks</p>
              </div>
            )}
            {rec.cost_estimate && (
              <div className="p-2 bg-white rounded-lg border border-neutral-200">
                <p className="text-neutral-400">Cost</p>
                <p className="font-semibold text-neutral-700">{rec.cost_estimate}</p>
              </div>
            )}
            {rec.confidence && (
              <div className="p-2 bg-white rounded-lg border border-neutral-200">
                <p className="text-neutral-400">Confidence</p>
                <p className="font-semibold text-neutral-700">{(rec.confidence * 100).toFixed(0)}%</p>
              </div>
            )}
          </div>

          {rec.expected_roi && (
            <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-200">
              <p className="text-xs text-neutral-400">Expected ROI</p>
              <p className="text-xs font-semibold text-emerald-700">{rec.expected_roi}</p>
            </div>
          )}
          {rec.cost_if_ignored && (
            <div className="p-2 rounded-lg bg-red-50 border border-red-200">
              <p className="text-xs text-neutral-400">Cost if ignored</p>
              <p className="text-xs font-semibold text-red-700">{rec.cost_if_ignored}</p>
            </div>
          )}
          {rec.owner && (
            <p className="text-xs text-neutral-500">Owner: <span className="font-semibold">{rec.owner}</span></p>
          )}
        </div>
      ))}
    </div>
  )
}

function DeepIntelCard({ data }) {
  if (!data?.ceo_briefing && !data?.political_map) return null
  return (
    <div className="space-y-5">
      {data.ceo_briefing && (
        <div className="p-5 rounded-xl bg-white border border-red-200 space-y-2">
          <p className="text-xs font-bold text-red-600 uppercase tracking-wider">🔐 CEO Briefing — Confidential</p>
          <p className="text-sm text-neutral-700 leading-relaxed whitespace-pre-line">{data.ceo_briefing}</p>
        </div>
      )}

      {data.political_map && (
        <div className="p-4 rounded-xl bg-white border border-red-200 space-y-3">
          <p className="text-xs font-bold text-red-700 uppercase tracking-wider">Political Map</p>
          {data.political_map.real_power_center && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-100">
              <p className="text-xs text-neutral-500">Real Power Center</p>
              <p className="text-sm font-semibold text-neutral-900 mt-0.5">{data.political_map.real_power_center}</p>
            </div>
          )}
          {data.political_map.official_vs_reality && (
            <p className="text-sm text-neutral-700">{data.political_map.official_vs_reality}</p>
          )}
          {data.political_map.power_factions?.map((f, i) => (
            <div key={i} className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-sm">{f.name}</p>
                <Badge label={`Threat: ${f.threat_level}`} type={f.threat_level === 'high' ? 'critical' : f.threat_level === 'medium' ? 'high' : 'low'} />
              </div>
              <p className="text-xs text-neutral-500 mt-1">Leader: {f.leader}</p>
              <p className="text-xs text-neutral-600 mt-1">Agenda: {f.agenda}</p>
              {f.members?.length > 0 && <div className="flex flex-wrap gap-1 mt-1">{f.members.map((m, j) => <Badge key={j} label={m} type="neutral" />)}</div>}
            </div>
          ))}
        </div>
      )}

      {data.culture_toxins?.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-red-600 uppercase tracking-wider">Culture Toxins</p>
          {data.culture_toxins.map((t, i) => (
            <div key={i} className="p-3 rounded-xl bg-white border border-red-200 space-y-1.5">
              <p className="font-semibold text-sm text-neutral-900">{t.toxin}</p>
              <p className="text-xs text-neutral-600">{t.evidence}</p>
              {t.carriers?.length > 0 && <p className="text-xs text-neutral-500">Carriers: {t.carriers.join(', ')}</p>}
              {t.antidote && <p className="text-xs text-emerald-700 font-semibold">Antidote: {t.antidote}</p>}
            </div>
          ))}
        </div>
      )}

      {data.between_the_lines?.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-neutral-500 uppercase tracking-wider">Between the Lines</p>
          {data.between_the_lines.slice(0, 4).map((b, i) => (
            <div key={i} className="p-3 rounded-xl bg-neutral-50 border border-neutral-200 space-y-1">
              <p className="text-xs text-neutral-400">{b.source} — {b.who_said_it}</p>
              <p className="text-xs text-neutral-600"><span className="font-bold">Said:</span> "{b.surface_message}"</p>
              <p className="text-xs text-red-700"><span className="font-bold">Meant:</span> {b.real_meaning}</p>
              {b.political_implication && <p className="text-xs text-neutral-400 italic">{b.political_implication}</p>}
            </div>
          ))}
        </div>
      )}

      {data.alert_signals?.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-bold text-amber-600 uppercase tracking-wider">⚠️ Alert Signals</p>
          {data.alert_signals.map((a, i) => (
            <div key={i} className={`p-3 rounded-xl border ${a.severity === 'critical' ? 'bg-red-50 border-red-300' : a.severity === 'high' ? 'bg-orange-50 border-orange-200' : 'bg-amber-50 border-amber-200'}`}>
              <p className="font-semibold text-sm">{a.signal}</p>
              <p className="text-xs text-neutral-600 mt-0.5">{a.evidence}</p>
              {a.action_needed && <p className="text-xs font-bold text-red-700 mt-1">Action: {a.action_needed}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


function AIChatbot({ dashboard, org, analysisId }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: `Hi! I'm your OrgLens AI analyst. I have full access to ${org?.name || 'your organization'}'s analysis — ask me anything about the findings, why something happened, or what to do about it.`
    }
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    if (!input.trim() || loading) return

    const userMsg = input.trim()

    setInput('')

    setMessages(prev => [
      ...prev,
      { role: 'user', text: userMsg }
    ])

    setLoading(true)

    try {
      const context = {
        org_name: org?.name,
        org_health: dashboard?.org_health,
        trust_gap: dashboard?.trust_gap,
        top_influencers: dashboard?.top_influencers?.influencers?.slice(0, 5),
        gatekeepers: dashboard?.gatekeepers?.gatekeepers?.slice(0, 3),
        resilience: {
          score: dashboard?.resilience?.resilience_score,
          risk_level: dashboard?.resilience?.risk_level,
          single_points_of_failure: dashboard?.resilience?.single_points_of_failure?.slice(0, 3),
        },
        decision_velocity: dashboard?.decision_velocity,
        system_diagnosis: {
          root_causes: dashboard?.system_diagnosis?.root_causes?.slice(0, 3),
          predicted_if_unchanged: dashboard?.system_diagnosis?.predicted_if_unchanged,
          ceo_briefing: dashboard?.system_diagnosis?.ceo_briefing,
        },
        predictions: dashboard?.predictions,
        recommendations: (
          Array.isArray(dashboard?.recommendations)
            ? dashboard.recommendations
            : dashboard?.recommendations?.recommendations
        )?.slice(0, 5),
      }

      const apiMessages = [
        ...messages.slice(-6).map(m => ({
          role: m.role === 'assistant' ? 'assistant' : 'user',
          content: m.text
        })),
        { role: 'user', content: userMsg }
      ]

      const reply = await chatWithAnalysis(analysisId, apiMessages, context)

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: reply
        }
      ])

    } catch (e) {
      console.error(e)

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: 'Sorry, I encountered an error while analyzing the organization. Please try again.'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-maroon-600 text-white shadow-neo-lg flex items-center justify-center hover:bg-maroon-700 transition-all duration-300 ${open ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
        title="Ask AI about this analysis"
      >
        <Bot size={24} />
      </button>

      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] h-[520px] rounded-2xl border border-neutral-200 bg-white shadow-neo-lg flex flex-col overflow-hidden">

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-maroon-600 text-white">
            <div className="flex items-center gap-2">
              <Bot size={18} />
              <span className="font-bold text-sm">
                OrgLens AI Analyst
              </span>
            </div>

            <button
              onClick={() => setOpen(false)}
              className="hover:opacity-70 transition-opacity"
            >
              <X size={18} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex gap-2 ${
                  m.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                    m.role === 'assistant'
                      ? 'bg-maroon-100 text-maroon-600'
                      : 'bg-neutral-100 text-neutral-600'
                  }`}
                >
                  {m.role === 'assistant' ? <Bot size={14} /> : <User size={14} />}
                </div>

                <div
                  className={`max-w-[85%] text-sm rounded-2xl px-3.5 py-2.5 leading-relaxed ${
                    m.role === 'assistant'
                      ? 'bg-neutral-100 text-neutral-800'
                      : 'bg-maroon-600 text-white'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-maroon-100 flex items-center justify-center">
                  <Bot size={14} className="text-maroon-600" />
                </div>
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
              {[
                'Why is the trust gap so high?',
                'Who are the real decision makers?',
                'What should we fix first?',
                'Who might leave soon?'
              ].map((s, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setInput(s)
                    setTimeout(() => sendMessage(), 50)
                  }}
                  className="text-xs px-2.5 py-1.5 rounded-full bg-maroon-50 text-maroon-700 border border-maroon-200 hover:bg-maroon-100 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <div className="p-3 border-t border-neutral-200 flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask about this analysis…"
              className="flex-1 text-sm px-3 py-2 rounded-xl border border-neutral-200 focus:outline-none focus:border-maroon-500 focus:ring-1 focus:ring-maroon-200 transition-all"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="w-9 h-9 rounded-xl bg-maroon-600 text-white flex items-center justify-center hover:bg-maroon-700 disabled:opacity-40 transition-all"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default function Dashboard() {
  const { orgId, analysisId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [org, setOrg] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [expanded, setExpanded] = useState({})

  useEffect(() => { loadDashboard() }, [analysisId])

  async function loadDashboard() {
    try {
      const [orgData, dashData] = await Promise.all([
        getOrganization(orgId),
        getDashboardReport(analysisId),
      ])
      setOrg(orgData)
      setDashboard(dashData)
    } catch (err) {
      setError('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const toggle = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }))

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 size={48} className="text-maroon-600 animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !dashboard) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <p className="text-neutral-600 mb-6">{error || 'Failed to load analysis'}</p>
          <button onClick={() => navigate(`/org/${orgId}/analysis`)} className="px-6 py-3 bg-maroon-600 text-white font-bold rounded-xl">
            Back to Analysis
          </button>
        </div>
      </div>
    )
  }

  const d = dashboard
  const cards = [
    {
      id: 'org-health', icon: '💚', title: 'Organizational Health',
      subtitle: `Grade: ${d.org_health?.grade || 'N/A'} — Composite vitality score`,
      score: d.org_health?.org_health_score,
      content: <OrgHealthCard data={d.org_health} />
    },
    {
      id: 'trust-gap', icon: '📊', title: 'Trust Gap Analysis',
      subtitle: `${d.trust_gap?.claims_analyzed || 0} claims analyzed — Values vs. reality`,
      score: d.trust_gap?.trust_gap_score, scoreInvert: true,
      content: <TrustGapCard data={d.trust_gap} />
    },
    {
      id: 'power-structure', icon: '🕸️', title: 'Power Structure',
      subtitle: `${d.power_structure?.nodes?.length || 0} people mapped — ${d.power_structure?.hidden_powers || 0} hidden powers`,
      content: <PowerStructureCard data={d.power_structure} />
    },
    {
      id: 'influencers', icon: '⭐', title: 'Top Influencers',
      subtitle: `${d.top_influencers?.total_analyzed || 0} analyzed — Formal vs. actual authority`,
      content: <InfluencersCard data={d.top_influencers} />
    },
    {
      id: 'gatekeepers', icon: '🚪', title: 'Gatekeepers',
      subtitle: `${d.gatekeepers?.gatekeepers?.length || 0} identified — Information & decision control`,
      content: <GatekeepersCard data={d.gatekeepers} />
    },
    {
      id: 'resilience', icon: '💪', title: 'Resilience Score',
      subtitle: `Risk: ${d.resilience?.risk_level?.toUpperCase() || 'N/A'} — Single points of failure`,
      score: d.resilience?.resilience_score,
      content: <ResilienceCard data={d.resilience} />
    },
    {
      id: 'velocity', icon: '⚡', title: 'Decision Velocity',
      subtitle: `${d.decision_velocity?.avg_days?.toFixed(1) || 'N/A'} days avg — ${d.decision_velocity?.benchmark || 'N/A'}`,
      content: <VelocityCard data={d.decision_velocity} />
    },
    {
      id: 'diagnosis', icon: '🔍', title: 'System Diagnosis',
      subtitle: `${d.system_diagnosis?.root_causes?.length || 0} root causes — What is really broken`,
      content: <DiagnosisCard data={d.system_diagnosis} />
    },
    {
      id: 'predictions', icon: '🔮', title: 'Predictions',
      subtitle: `${d.predictions?.attrition_risks?.length || 0} attrition risks — 6-month forecast`,
      score: d.predictions?.health_forecast_6mo,
      content: <PredictionsCard data={d.predictions} />
    },
    {
      id: 'data-quality', icon: '📊', title: 'Data Quality & Confidence',
      subtitle: `Based on ${d.confidence_metrics?.total_messages ?? d.messages_analyzed ?? 0} messages — Reliability assessment`,
      isSpecial: true,
      render: (expanded, toggle) => (
        <DataQualityCard 
          data={
            d.confidence_metrics && Object.keys(d.confidence_metrics).length > 0
              ? d.confidence_metrics
              : {
                  overall_confidence: d.messages_analyzed > 200 ? 'high' : d.messages_analyzed > 100 ? 'medium' : d.messages_analyzed > 50 ? 'low' : 'critical',
                  overall_confidence_pct: Math.min(Math.round((d.messages_analyzed || 0) / 3), 100),
                  total_messages: d.messages_analyzed || 0,
                  total_employees: d.power_structure?.nodes?.length || 0,
                  messages_per_person: d.power_structure?.nodes?.length
                    ? Number(((d.messages_analyzed || 0) / d.power_structure.nodes.length).toFixed(1))
                    : 0,
                  date_range_days: 30,
                  coverage_by_function: {},
                  coverage_by_level: {},
                  warnings: d.messages_analyzed < 50
                    ? [`⚠️ Limited message volume (${d.messages_analyzed} messages). Findings may be skewed.`]
                    : [],
                  signals_pending_data: [],
                  confidence_breakdown: {
                    message_volume: Math.min((d.messages_analyzed || 0) / 10 * 100, 100),
                    department_coverage: 50,
                    time_range_quality: Math.min((d.decision_velocity?.avg_days || 14) / 30 * 100, 100),
                  },
                  strengths_detected: [
                    d.messages_analyzed > 100 ? 'Message volume is reasonably strong' : null,
                    d.org_health?.org_health_score >= 7 ? 'Good organizational health signals detected' : null,
                  ].filter(Boolean),
                  limitations_detected: [
                    d.messages_analyzed < 100 ? 'Limited message volume reduces statistical reliability' : null,
                    d.messages_analyzed < 50 ? 'Short observation window limits trend detection' : null,
                    !d.power_structure?.nodes?.length ? 'No people data available' : null,
                  ].filter(Boolean),
                  recommended_data_improvements: [
                    d.messages_analyzed < 100 ? 'Collect more communication samples across teams' : null,
                    d.decision_velocity?.avg_days < 30 ? 'Analyze at least 30 days of organizational activity' : null,
                  ].filter(Boolean),
                  data_sufficiency_summary: `Analysis based on ${d.messages_analyzed || 0} messages across ${d.power_structure?.nodes?.length || 0} people.`,
                  recommendation: d.messages_analyzed > 100
                    ? '✅ GOOD DATA: Confidence is high enough for strategic decisions.'
                    : '⚠️ LIMITED DATA: Collect more communication data for higher confidence.',
                }
          }
          expanded={expanded}
          onToggle={toggle}
        />
      ),
    },
   {
      id: 'contradictions', icon: '🚨', title: 'Contradictions',
      subtitle: `${(d.contradictions || []).length} gaps between claims & reality`,
      content: <ContradictionCard data={d.contradictions || []} />,
    },
    {
      id: 'positive-signals', icon: '⭐', title: 'Strengths & Positives',
      subtitle: `${(d.positive_signals || []).length} areas working well — Build on these`,
      isSpecial: true,
      render: (expanded, toggle) => (
        <PositiveSignalsCard 
          data={d.positive_signals || []}
          expanded={expanded}
          onToggle={toggle}
        />
      ),
    },
    {
      id: 'archetype', icon: '🏢', title: 'Organizational Archetype',
      subtitle: `${d.archetype?.name || 'Operating mode classification'}`,
      isSpecial: true,
      render: (expanded, toggle) => (
        <ArchetypeCard
          data={
            d.archetype && d.archetype.archetype
              ? d.archetype
              : null
          }
          expanded={expanded}
          onToggle={toggle}
        />
      ),
    },
    {
      id: 'recommendations', icon: '💡', title: 'Recommendations',
      subtitle: `${(Array.isArray(d.recommendations) ? d.recommendations : d.recommendations?.recommendations || []).length} action items — Prioritized by impact`,
      content: <RecommendationsCard data={d.recommendations} dashboardData={d} />
    },
  ]

  const hasDeepIntel = d.system_diagnosis?.ceo_briefing || d.system_diagnosis?.political_map

  return (
    <div className="min-h-screen bg-white">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-maroon-100/15 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-neutral-100/20 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate(`/org/${orgId}/analysis`)}
            className="group flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold text-neutral-600 hover:text-maroon-600 hover:bg-maroon-50 transition-all shadow-neo-sm"
          >
            <ArrowLeft size={15} className="group-hover:-translate-x-0.5 transition-transform" />
            Back
          </button>
          <div className="flex gap-2">
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify({ org: org?.name, dashboard }, null, 2)], { type: 'application/json' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${org?.name || 'analysis'}-${new Date().toISOString().split('T')[0]}.json`
                a.click()
                URL.revokeObjectURL(url)
              }}
              className="p-2 rounded-lg hover:bg-neutral-100 transition-colors" title="Download">
              <Download size={18} className="text-neutral-600" />
            </button>
            <button onClick={() => { navigator.clipboard.writeText(window.location.href).then(() => alert('Link copied!')).catch(() => {}) }}
              className="p-2 rounded-lg hover:bg-neutral-100 transition-colors" title="Share">
              <Share2 size={18} className="text-neutral-600" />
            </button>
          </div>
        </div>

        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-maroon-600 flex items-center justify-center text-white text-lg shadow-neo-sm">
              📊
            </div>
            <div>
              <h1 className="font-bold text-2xl text-neutral-900">{org?.name} — Analysis Dashboard</h1>
              <p className="text-sm text-neutral-500 mt-0.5">{d.messages_analyzed} messages analyzed</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Org Health', value: d.org_health?.org_health_score?.toFixed(1), unit: '/10', icon: '💚', invert: false },
            { label: 'Trust Gap', value: d.trust_gap?.trust_gap_score?.toFixed(1), unit: '/10', icon: '📊', invert: true },
            { label: 'Resilience', value: d.resilience?.resilience_score?.toFixed(1), unit: '/10', icon: '💪', invert: false },
            { label: 'Decision Velocity', value: d.decision_velocity?.avg_days?.toFixed(1), unit: ' days', icon: '⚡', invert: true },
          ].map(({ label, value, unit, icon, invert }) => (
            <div key={label} className="p-4 rounded-2xl border border-neutral-200 bg-white shadow-neo-sm text-center">
              <span className="text-2xl">{icon}</span>
              <p className="text-xs text-neutral-500 mt-1">{label}</p>
              <p className={`text-xl font-bold mt-0.5 ${scoreColor(parseFloat(value || 0), invert)}`}>
                {value || 'N/A'}<span className="text-sm font-normal text-neutral-400">{unit}</span>
              </p>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          {cards.map(({ id, icon, title, subtitle, score, scoreInvert, content, isSpecial, render }) => {
            if (isSpecial) {
              return (
                <div key={id} className="rounded-2xl border border-neutral-200 bg-white shadow-neo-sm hover:shadow-neo-md transition-all">
                  <button
                    onClick={() => toggle(id)}
                    className="w-full text-left p-6 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-3xl">{icon}</span>
                      <div>
                        <h3 className="font-bold text-neutral-900">{title}</h3>
                        <p className="text-xs text-neutral-500 mt-0.5">{subtitle}</p>
                      </div>
                    </div>
                    {expanded[id] ? <ChevronUp size={18} className="text-neutral-400" /> : <ChevronDown size={18} className="text-neutral-400" />}
                  </button>
                  {expanded[id] && (
                    <div className="px-6 pb-6 border-t border-neutral-100 pt-5">
                      {render(!!expanded[id], () => toggle(id))}
                    </div>
                  )}
                </div>
              )
            }
            
            return (
              <AnalysisCard
                key={id}
                id={id}
                icon={icon}
                title={title}
                subtitle={subtitle}
                score={score}
                scoreInvert={scoreInvert}
                expanded={!!expanded[id]}
                onToggle={() => toggle(id)}
              >
                {content}
              </AnalysisCard>
            )
          })}
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 32, marginBottom: 32 }}>
          <button
            onClick={() => navigate(`/org/${orgId}/dashboard/${analysisId}/deep-dive`)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '12px 24px',
              borderRadius: 10,
              cursor: 'pointer',
              background: '#1a1916',
              color: '#fff',
              fontSize: 13,
              fontWeight: 600,
              border: 'none',
              boxShadow: '0 2px 12px rgba(0,0,0,0.18)',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.25)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.18)'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            <span>⚡</span>
            Deep Dive Analysis
          </button>
        </div>
      </div>

      <AIChatbot dashboard={dashboard} org={org} analysisId={analysisId} />
    </div>
  )
}
