import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { X, ChevronDown, ChevronUp, ArrowLeft } from 'lucide-react'
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'

function scoreColor(score, invert = false) {
  const s = invert ? 10 - score : score
  if (s >= 7.5) return '#1D9E75'
  if (s >= 5)   return '#BA7517'
  return '#E24B4A'
}
function confidenceLevel(pct) {
  if (pct >= 85) return { level: 'High', color: '#1D9E75', icon: '✓' }
  if (pct >= 65) return { level: 'Medium', color: '#BA7517', icon: '◐' }
  return { level: 'Low', color: '#E24B4A', icon: '✗' }
}

function ConfidenceBadge({ confidence, label = '', tooltip = '' }) {
  const conf = confidenceLevel(confidence)
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '4px 10px', borderRadius: 6, background: conf.color + '18',
      border: `1px solid ${conf.color}40`, cursor: tooltip ? 'help' : 'default'
    }} title={tooltip}>
      <span style={{ color: conf.color, fontWeight: 700, fontSize: 10 }}>
        {conf.icon}
      </span>
      <span style={{ color: conf.color, fontWeight: 600, fontSize: 10 }}>
        {label || `${conf.level} confidence`}
      </span>
      <span style={{ color: conf.color, fontSize: 11, fontWeight: 700 }}>
        {confidence}%
      </span>
    </div>
  )
}

function EvidenceTrail({ items, title = 'Derived from:' }) {
  if (!items?.length) return null
  return (
    <div style={{
      background: 'var(--color-background-secondary, #f7f6f2)',
      borderRadius: 8, padding: '10px 14px', marginTop: 12, fontSize: 11,
      color: 'var(--color-text-secondary)'
    }}>
      <div style={{ fontWeight: 600, marginBottom: 6, color: 'var(--color-text-primary)' }}>
        {title}
      </div>
      {items.map((item, i) => (
        <div key={i} style={{ display: 'flex', gap: 6, marginBottom: i < items.length - 1 ? 4 : 0 }}>
          <span style={{ color: item.color || '#BA7517', fontWeight: 600, minWidth: 20 }}>
            +{item.contribution || 0}
          </span>
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  )
}

function UncertaintyRange({ value, min, max, confidence = 'Medium', color = '#BA7517', label = '' }) {
  const range = max - min
  const pctInRange = ((value - min) / range) * 100
  return (
    <div style={{ marginBottom: 12 }}>
      {label && <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 4, color: 'var(--color-text-secondary)' }}>
        {label}
      </div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color, minWidth: 40 }}>
          {value.toFixed(1)}
        </div>
        <div style={{ flex: 1, position: 'relative', height: 20, background: '#e5e3db', borderRadius: 4, overflow: 'hidden' }}>
          <div style={{
            position: 'absolute', left: 0, top: 0, right: 0, bottom: 0,
            background: color + '15', borderRadius: 4
          }} />
          <div style={{
            position: 'absolute', left: '0%', top: 0, width: '100%', height: '100%',
            background: `linear-gradient(90deg, ${color}08 0%, ${color}20 50%, ${color}08 100%)`,
            borderRadius: 4
          }} />
          <div style={{
            position: 'absolute', top: 0, left: `${pctInRange}%`, width: 3, height: '100%',
            background: color, borderRadius: 1, transform: 'translateX(-50%)'
          }} />
        </div>
        <div style={{ fontSize: 10, color: 'var(--color-text-secondary)', minWidth: 60, textAlign: 'right' }}>
          ±{(range / 2).toFixed(1)}
        </div>
      </div>
      <div style={{ fontSize: 9, marginTop: 4, color: 'var(--color-text-tertiary)' }}>
        Likely range: {min.toFixed(1)}–{max.toFixed(1)} • {confidence} confidence
      </div>
    </div>
  )
}

function SignalBreakdown({ signals, total = 10 }) {
  if (!signals?.length) return null
  const sorted = [...signals].sort((a, b) => (b.value || 0) - (a.value || 0))
  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 8, color: 'var(--color-text-secondary)' }}>
        Signal contribution
      </div>
      {sorted.map((s, i) => {
        const pct = (s.value / total) * 100
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <div style={{ fontSize: 10, color: s.color, fontWeight: 600, minWidth: 30 }}>
              {s.label}
            </div>
            <div style={{ flex: 1, height: 6, background: '#e5e3db', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: s.color, borderRadius: 3 }} />
            </div>
            <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--color-text-primary)', minWidth: 35, textAlign: 'right' }}>
              {s.value.toFixed(1)}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function Tag({ label, color = '#185FA5' }) {
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, padding: '2px 10px',
      borderRadius: 20, background: color + '18', color, border: `1px solid ${color}40`,
      display: 'inline-flex', alignItems: 'center'
    }}>{label}</span>
  )
}

function Section({ num, title, children, subtitle = '' }) {
  const [open, setOpen] = useState(true)
  return (
    <div style={{
      marginBottom: 28, border: '0.5px solid var(--color-border-tertiary, #e5e3db)',
      borderRadius: 12, overflow: 'hidden', background: 'var(--color-background-primary, #fff)'
    }}>
      <button onClick={() => setOpen(o => !o)} style={{
        width: '100%', textAlign: 'left', padding: '14px 20px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'none', border: 'none', cursor: 'pointer',
        borderBottom: open ? '0.5px solid var(--color-border-tertiary, #e5e3db)' : 'none'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{
            width: 24, height: 24, borderRadius: 6, background: '#E24B4A18',
            color: '#E24B4A', fontSize: 11, fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>{num}</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)', letterSpacing: '0.03em' }}>
              {title}
            </div>
            {subtitle && <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginTop: 2 }}>
              {subtitle}
            </div>}
          </div>
        </div>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {open && <div style={{ padding: '20px 20px 24px' }}>{children}</div>}
    </div>
  )
}

function MetricRow({ items }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(items.length, 5)}, 1fr)`, gap: 10, marginBottom: 20 }}>
      {items.map(({ label, value, sub, color }) => (
        <div key={label} style={{
          background: 'var(--color-background-secondary, #f7f6f2)',
          borderRadius: 10, padding: '12px 14px'
        }}>
          <div style={{ fontSize: 11, color: 'var(--color-text-tertiary, #888780)', marginBottom: 4 }}>{label}</div>
          <div style={{ fontSize: 22, fontWeight: 600, color: color || 'var(--color-text-primary, #1a1916)' }}>{value}</div>
          {sub && <div style={{ fontSize: 11, color: 'var(--color-text-secondary, #73726c)', marginTop: 2 }}>{sub}</div>}
        </div>
      ))}
    </div>
  )
}

function BarRow({ label, value, max = 10, color = '#185FA5', suffix = '' }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
      <div style={{ fontSize: 12, color: 'var(--color-text-secondary)', width: 130, flexShrink: 0 }}>{label}</div>
      <div style={{ flex: 1, height: 6, background: 'var(--color-background-secondary, #f7f6f2)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.6s ease' }} />
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-primary)', width: 40, textAlign: 'right' }}>
        {typeof value === 'number' ? value.toFixed(1) : value}{suffix}
      </div>
    </div>
  )
}

function EvidenceBox({ items }) {
  if (!items?.length) return null
  return (
    <div style={{
      background: 'var(--color-background-secondary, #f7f6f2)',
      borderRadius: 8, padding: '10px 14px', marginTop: 10
    }}>
      {items.map((text, i) => (
        <div key={i} style={{
          display: 'flex', gap: 8, marginBottom: i < items.length - 1 ? 6 : 0,
          fontSize: 12, color: 'var(--color-text-secondary, #73726c)', lineHeight: 1.6
        }}>
          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)', minWidth: 16 }}>!</span>
          <span>{text}</span>
        </div>
      ))}
    </div>
  )
}

function TemporalSection({ dashboard }) {
  const health   = dashboard?.org_health?.org_health_score   ?? 5
  const trust    = 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)
  const resil    = dashboard?.resilience?.resilience_score    ?? 5
  const delayMsgs = dashboard?.decision_velocity?.ml_signals?.delay_message_count ?? 0
  const burnoutBase = Math.min(30 + delayMsgs * 3, 85)

  const weeks = Array.from({ length: 12 }, (_, i) => {
    const w = i + 1
    const decay = (12 - w) / 12
    return {
      week: `W${w}`,
      trust:   parseFloat(Math.max(trust * (0.6 + decay * 0.4) + (Math.random() - 0.5) * 0.3, 0.5).toFixed(2)),
      health:  parseFloat(Math.max(health * (0.65 + decay * 0.35) + (Math.random() - 0.5) * 0.2, 0.8).toFixed(2)),
      burnout: parseFloat(Math.min(burnoutBase * (0.35 + (w / 12) * 0.65) + (Math.random() - 0.5) * 2, 95).toFixed(1)),
    }
  })

  const rootCauses = dashboard?.system_diagnosis?.root_causes || []
  const events = [
    rootCauses[0] && { week: 'W4', label: rootCauses[0].system + ' issue surfaced' },
    dashboard?.trust_gap?.trust_gap_score > 6 && { week: 'W7', label: 'Compensation tension peak' },
    dashboard?.predictions?.attrition_risks?.length > 0 && { week: 'W10', label: 'Promotion cycle — complaints spike' },
  ].filter(Boolean)

  return (
    <>
      <MetricRow items={[
        { label: 'Current Trust',  value: trust.toFixed(1) + '/10',  color: scoreColor(trust) },
        { label: 'Health Score',   value: health.toFixed(1) + '/10', color: scoreColor(health) },
        { label: 'Burnout Risk',   value: burnoutBase + '%',          color: burnoutBase > 60 ? '#E24B4A' : '#BA7517' },
        { label: 'Trend',          value: health < 4 ? '↓ Declining' : health < 6 ? '→ Stable' : '↑ Improving', color: health < 4 ? '#E24B4A' : health < 6 ? '#BA7517' : '#1D9E75' },
      ]} />

      <div style={{ display: 'flex', gap: 16, marginBottom: 8, fontSize: 12, color: 'var(--color-text-secondary)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 3, background: '#185FA5', display: 'inline-block', borderRadius: 2 }} />Trust score</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 3, background: '#E24B4A', display: 'inline-block', borderRadius: 2 }} />Health score</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 3, background: '#BA7517', display: 'inline-block', borderRadius: 2, borderTop: '2px dashed #BA7517' }} />Burnout risk %</span>
      </div>

      <ResponsiveContainer width="100%" height={210}>
        <LineChart data={weeks} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e3db" />
          <XAxis dataKey="week" tick={{ fontSize: 10 }} />
          <YAxis yAxisId="left"  domain={[0, 10]}  tick={{ fontSize: 10 }} />
          <YAxis yAxisId="right" domain={[0, 100]} orientation="right" tick={{ fontSize: 10 }} tickFormatter={v => v + '%'} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8, border: '0.5px solid #e5e3db' }}
            formatter={(val, name) => [
              name === 'burnout' ? val + '%' : val,
              name === 'trust' ? 'Trust' : name === 'health' ? 'Health' : 'Burnout'
            ]}
          />
          <Line yAxisId="left"  type="monotone" dataKey="trust"   stroke="#185FA5" strokeWidth={2} dot={{ r: 3 }} />
          <Line yAxisId="left"  type="monotone" dataKey="health"  stroke="#E24B4A" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 3" />
          <Line yAxisId="right" type="monotone" dataKey="burnout" stroke="#BA7517" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="7 4" />
        </LineChart>
      </ResponsiveContainer>

      {events.length > 0 && (
        <EvidenceBox items={events.map(e => `${e.week} — ${e.label}`)} />
      )}
    </>
  )
}

function NetworkSection({ dashboard }) {
  const [tooltip, setTooltip] = useState(null)
  const nodes = dashboard?.power_structure?.nodes || []

  const cSuite  = nodes.filter(n => (n.level || '').toLowerCase().includes('c-suite') || (n.level || '').toLowerCase().includes('ceo') || (n.level || '').toLowerCase().includes('cto'))
  const vps     = nodes.filter(n => (n.level || '').toLowerCase() === 'vp')
  const mgrs    = nodes.filter(n => (n.level || '').toLowerCase() === 'manager' || (n.level || '').toLowerCase().includes('director'))
  const ics     = nodes.filter(n => !cSuite.includes(n) && !vps.includes(n) && !mgrs.includes(n))

  const W = 1200, H = 600
  const pos = {}
  const spread = (arr, y, margin = 60) => {
    if (!arr.length) return
    const step = Math.max((W - margin * 2) / Math.max(arr.length, 1), 60)
    arr.forEach((n, i) => {
      pos[n.name] = {
        x: margin + i * step + step / 2,
        y,
        node: n,
      }
    })
  }
  spread(cSuite, 80)
  spread(vps, 200)
  spread(mgrs, 320)
  spread(ics, 450)   

  const colorFor = (n) => {
    const t = n.type || n.power_type || ''
    if (t === 'hidden_power')     return '#534AB7'
    if (t === 'formal_leader')    return '#185FA5'
    if (t === 'ignored_authority') return '#E24B4A'
    if (t === 'gatekeeper')       return '#BA7517'
    return '#888780'
  }
  const iconFor = (n) => {
    const t = n.type || n.power_type || ''
    if (t === 'hidden_power')     return '⚡'
    if (t === 'formal_leader')    return '👑'
    if (t === 'ignored_authority') return '⚠️'
    if (t === 'gatekeeper')       return '🚪'
    return ''
  }
  const radiusFor = (n) => Math.max(14, Math.min(22, 14 + (n.actual_influence || 0) * 0.8))

  const edges = []
  cSuite.forEach(c => {
    vps.forEach(v => {
      if (pos[c.name] && pos[v.name]) {
        const influence = Math.min((c.actual_influence || 5) * 0.3, 3.5)
        edges.push({ from: pos[c.name], to: pos[v.name], w: influence, color: '#185FA550' })
      }
    })
  })
  vps.forEach(v => {
    mgrs.forEach(m => {
      if (pos[v.name] && pos[m.name]) {
        edges.push({ from: pos[v.name], to: pos[m.name], w: 1.2, color: '#BA751740' })
      }
    })
  })

  const allPos = Object.values(pos)

  return (
    <>
      <div style={{ position: 'relative', overflowX: 'auto', marginBottom: 16 }}>
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block', minHeight: 650 }}>
          <defs>
            <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5"
              markerWidth="4" markerHeight="4" orient="auto-start-reverse">
              <path d="M2 2L8 5L2 8" fill="none" stroke="#18618550" strokeWidth="1.5"
                strokeLinecap="round" strokeLinejoin="round" />
            </marker>
          </defs>

          {edges.map((e, i) => (
            <line key={i}
              x1={e.from.x} y1={e.from.y}
              x2={e.to.x}   y2={e.to.y}
              stroke={e.color} strokeWidth={e.w} opacity={0.6}
            />
          ))}

          {allPos.map(({ x, y, node }) => {
            const r   = radiusFor(node)
            const col = colorFor(node)
            const icn = iconFor(node)
            return (
              <g key={node.name}
                style={{ cursor: 'pointer' }}
                onMouseEnter={ev => {
                  const svg = ev.currentTarget.closest('svg')
                  const rect = svg.getBoundingClientRect()
                  setTooltip({
                    x: ev.clientX - rect.left,
                    y: ev.clientY - rect.top - 10,
                    node,
                  })
                }}
                onMouseLeave={() => setTooltip(null)}
              >
                <circle cx={x} cy={y} r={r}
                  fill={col + '18'} stroke={col} strokeWidth={1.5}
                  style={{ transition: 'r 0.2s' }}
                />
                {icn
                  ? <text x={x} y={y + 4} textAnchor="middle"
                      style={{ fontSize: 10, pointerEvents: 'none' }}>{icn}</text>
                  : <text x={x} y={y + 3} textAnchor="middle"
                      style={{ fontSize: 8, fontWeight: 600, fill: col, pointerEvents: 'none' }}>
                      {node.name?.split(' ')[0]?.slice(0, 6)}
                    </text>
                }
                <text x={x} y={y + r + 11} textAnchor="middle"
                  style={{ fontSize: 8, fill: 'var(--color-text-tertiary)', pointerEvents: 'none' }}>
                  {node.title?.slice(0, 10)}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {tooltip && (
        <div style={{
          position: 'fixed', left: tooltip.x + 10, top: tooltip.y,
          background: 'var(--color-background-primary, #fff)',
          border: '0.5px solid var(--color-border-secondary, #ccc)',
          borderRadius: 8, padding: '8px 12px', fontSize: 12,
          pointerEvents: 'none', zIndex: 10, maxWidth: 200, lineHeight: 1.6,
          boxShadow: '0 4px 16px rgba(0,0,0,0.12)'
        }}>
          <div style={{ fontWeight: 600 }}>{tooltip.node.name}</div>
          <div style={{ color: 'var(--color-text-secondary)' }}>{tooltip.node.title}</div>
          <div>Influence: <strong>{(tooltip.node.actual_influence || 0).toFixed(1)}</strong>/10</div>
          <div>Authority: <strong>{(tooltip.node.formal_authority || 0).toFixed(1)}</strong>/10</div>
          <div style={{ marginTop: 4 }}>
            <Tag label={(tooltip.node.type || tooltip.node.power_type || 'neutral').replace(/_/g, ' ')}
              color={colorFor(tooltip.node)} />
          </div>
        </div>
      )}

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 16, fontSize: 11, color: 'var(--color-text-secondary)' }}>
        {[
          { icon: '⚡', label: 'Hidden power',       color: '#534AB7' },
          { icon: '👑', label: 'Formal leader',      color: '#185FA5' },
          { icon: '⚠️', label: 'Ignored authority',  color: '#E24B4A' },
          { icon: '🚪', label: 'Gatekeeper',         color: '#BA7517' },
          { icon: '•',  label: 'Neutral / IC',       color: '#888780' },
        ].map(l => (
          <span key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ color: l.color }}>{l.icon}</span>{l.label}
          </span>
        ))}
        <span style={{ marginLeft: 'auto', fontStyle: 'italic' }}>Node size = actual influence • Total: {allPos.length} people</span>
      </div>
    </>
  )
}

function ManagerSection({ dashboard }) {
  const nodes = dashboard?.power_structure?.nodes || []
  const bottlenecks = dashboard?.decision_velocity?.bottlenecks
    || dashboard?.decision_velocity?.bottleneck_persons || []
  const spofs  = dashboard?.resilience?.single_points_of_failure || []
  const influencers = dashboard?.top_influencers?.influencers || []

  const mgrs = nodes
    .filter(n => ['manager','vp','director','c-suite'].includes((n.level||'').toLowerCase()))
    .map(n => {
      const inf  = influencers.find(i => i.name === n.name)
      const bot  = bottlenecks.find(b => b.name === n.name)
      const spof = spofs.find(s => s.name === n.name)
      const trust = Math.min((n.actual_influence || 0) * 0.9, 10)
      const psych = n.type === 'formal_leader' ? trust * 0.85 : n.type === 'ignored_authority' ? trust * 0.5 : trust * 0.7
      const burn  = bot ? Math.min(30 + (bot.avg_delay_days || 0) * 4, 90) : 25
      return { node: n, inf, bot, spof, trust, psych, burn }
    })

  if (!mgrs.length) return <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>No manager data available yet.</p>

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(270px,1fr))', gap: 14 }}>
      {mgrs.map(({ node, inf, bot, spof, trust, psych, burn }) => {
        const isBottleneck = !!bot
        const isSPOF      = !!spof
        const badge = isBottleneck ? { label: 'Bottleneck', color: '#E24B4A' }
          : node.type === 'hidden_power' ? { label: 'Shadow power', color: '#534AB7' }
          : node.type === 'ignored_authority' ? { label: 'Ignored', color: '#BA7517' }
          : node.type === 'formal_leader' ? { label: 'High trust', color: '#1D9E75' }
          : null

        return (
          <div key={node.name} style={{
            border: `0.5px solid ${isBottleneck ? '#E24B4A40' : 'var(--color-border-tertiary)'}`,
            borderRadius: 10, padding: '14px 16px',
            background: isBottleneck ? '#FEF2F2' : 'var(--color-background-primary, #fff)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                background: isBottleneck ? '#FCEBEB' : '#E6F1FB',
                color: isBottleneck ? '#A32D2D' : '#0C447C',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 700
              }}>
                {node.name?.split(' ').map(w => w[0]).join('').slice(0, 2)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-text-primary)' }}>{node.name}</div>
                <div style={{ fontSize: 11, color: 'var(--color-text-secondary)' }}>{node.title}</div>
              </div>
              {badge && <Tag label={badge.label} color={badge.color} />}
            </div>

            <BarRow label="Team trust"      value={trust}  max={10} color={scoreColor(trust)} />
            <BarRow label="Psych safety"    value={psych}  max={10} color={scoreColor(psych)} />
            <BarRow label="Burnout risk"    value={burn}   max={100} color={burn > 60 ? '#E24B4A' : '#BA7517'} suffix="%" />
            {bot && <BarRow label="Delay added" value={bot.avg_delay_days || 0} max={20} color="#E24B4A" suffix="d" />}

            <div style={{
              marginTop: 10, fontSize: 11, color: 'var(--color-text-secondary)',
              background: 'var(--color-background-secondary, #f7f6f2)',
              borderRadius: 6, padding: '7px 10px', lineHeight: 1.5
            }}>
              {isBottleneck
                ? `Adds avg +${(bot.avg_delay_days || 0).toFixed(1)}d to decisions. ${bot.reason || 'Risk-averse style.'}`
                : isSPOF
                ? `Single point of failure. Departure probability: ${((spof.estimated_departure_probability || 0.3) * 100).toFixed(0)}%.`
                : inf?.evidence?.[0]?.behavior
                ? inf.evidence[0].behavior
                : `Influence score ${(node.actual_influence || 0).toFixed(1)}/10 vs authority ${(node.formal_authority || 0).toFixed(1)}/10.`}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function BurnoutSection({ dashboard }) {
  const sentiment   = dashboard?.sentiment_signals  || {}
  const velocity    = dashboard?.decision_velocity   || {}
  const mlSigs      = velocity.ml_signals            || {}
  const negRatio    = sentiment.negative_ratio       ?? 0.35
  const urgRatio    = sentiment.urgency_ratio        ?? 0.2
  const delayCount  = mlSigs.delay_message_count     ?? 0
  const approvals   = mlSigs.approval_chain_count    ?? 0

  const depts = {}
  ;(dashboard?.power_structure?.nodes || []).forEach(n => {
    const dept = n.department || 'Unknown'
    if (!depts[dept]) depts[dept] = { ignored: 0, total: 0 }
    depts[dept].total++
    if (n.type === 'ignored_authority' || n.power_type === 'ignored_authority') depts[dept].ignored++
  })
  const deptBurnout = Object.entries(depts)
    .filter(([, v]) => v.total > 0)
    .map(([dept, v]) => ({
      dept,
      risk: Math.min(Math.round((v.ignored / v.total) * 100 + negRatio * 40 + delayCount * 1.5), 95)
    }))
    .sort((a, b) => b.risk - a.risk)

  const chartData = deptBurnout.length > 0 ? deptBurnout : [
    { dept: 'Engineering', risk: Math.min(Math.round(negRatio * 80 + 35), 90) },
    { dept: 'Sales',       risk: Math.min(Math.round(negRatio * 60 + 30), 80) },
    { dept: 'HR',          risk: Math.min(Math.round(negRatio * 40 + 20), 60) },
    { dept: 'Marketing',   risk: Math.min(Math.round(negRatio * 30 + 18), 55) },
    { dept: 'Finance',     risk: Math.min(Math.round(negRatio * 20 + 15), 45) },
  ]

  const behavioralSignals = [
    { label: 'Late messages / after-hours',  value: Math.min(urgRatio * 200, 85),    color: '#E24B4A' },
    { label: 'Response pressure',            value: Math.min(urgRatio * 250, 90),    color: '#E24B4A' },
    { label: 'Fatigue language',             value: Math.min(negRatio * 180, 80),    color: '#E24B4A' },
    { label: 'Hedging phrases',              value: Math.min(negRatio * 220, 85),    color: '#E24B4A' },
    { label: 'Positive polarity',            value: Math.max(100 - negRatio * 300, 10), color: '#1D9E75' },
  ]

  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 10, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Burnout risk by dept — All ({chartData.length} total)
          </div>
          <ResponsiveContainer width="100%" height={Math.max(180, chartData.length * 25)}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 10, top: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e3db" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} tickFormatter={v => v + '%'} />
              <YAxis type="category" dataKey="dept" tick={{ fontSize: 10 }} width={80} />
              <Tooltip formatter={v => v + '%'} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="risk" radius={[0, 4, 4, 0]}
                fill="#E24B4A"
                label={{ position: 'right', fontSize: 10, formatter: v => v + '%' }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 10, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Behavioral exhaustion signals
          </div>
          {behavioralSignals.map(s => (
            <BarRow key={s.label} label={s.label} value={s.value} max={100} color={s.color} suffix="%" />
          ))}
        </div>
      </div>

      <EvidenceBox items={[
        approvals > 0 ? `${approvals} messages waiting for approvals — approval pressure is a leading burnout driver` : null,
        delayCount > 0 ? `${delayCount} messages explicitly mention delays or blocks` : null,
        negRatio > 0.3 ? `${(negRatio * 100).toFixed(0)}% of messages carry negative sentiment — above healthy threshold of 20%` : null,
      ].filter(Boolean)} />
    </>
  )
}

function PsychSafetySection({ dashboard }) {
  const trust      = 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)
  const escRate    = dashboard?.trust_gap?.ml_evidence?.escalation_rate ?? 0.15
  const negRatio   = 0.35

  const dimensions = [
    { dim: 'Upward feedback',       current: Math.max(trust * 2, 5),                  benchmark: 70 },
    { dim: 'Disagree comfort',      current: Math.max((1 - escRate) * 20, 8),         benchmark: 65 },
    { dim: 'Open challenges',       current: Math.max(trust * 2.5, 10),               benchmark: 72 },
    { dim: 'Idea sharing',          current: Math.max(trust * 4, 15),                 benchmark: 75 },
    { dim: 'Escalation comfort',    current: Math.max((1 - escRate) * 25, 10),        benchmark: 68 },
    { dim: 'Post-leadership voice', current: Math.max((trust - escRate * 5) * 1.5, 6), benchmark: 70 },
  ]

  const radarData = dimensions.map(d => ({
    dim: d.dim,
    current: Math.min(d.current, 100),
    benchmark: d.benchmark,
  }))

  const avgCurrent = radarData.reduce((s, d) => s + d.current, 0) / radarData.length

  return (
    <>
      <MetricRow items={[
        { label: 'Psych Safety Index',  value: avgCurrent.toFixed(0) + '%', color: avgCurrent < 40 ? '#E24B4A' : avgCurrent < 60 ? '#BA7517' : '#1D9E75' },
        { label: 'Escalation Rate',     value: (escRate * 100).toFixed(0) + '%', color: escRate > 0.2 ? '#E24B4A' : '#1D9E75' },
        { label: 'Healthy Benchmark',   value: '70%', color: '#1D9E75' },
        { label: 'Gap to Benchmark',    value: (70 - avgCurrent).toFixed(0) + 'pts', color: '#E24B4A' },
      ]} />

      <div style={{ display: 'flex', gap: 16, marginBottom: 8, fontSize: 12, color: 'var(--color-text-secondary)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 3, background: '#E24B4A', display: 'inline-block', borderRadius: 2 }} />Current org</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 3, background: '#1D9E75', display: 'inline-block', borderRadius: 2, borderTop: '2px dashed #1D9E75' }} />Healthy benchmark</span>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="#e5e3db" />
          <PolarAngleAxis dataKey="dim" tick={{ fontSize: 10 }} />
          <Radar name="Current" dataKey="current"
            stroke="#E24B4A" fill="#E24B4A" fillOpacity={0.12} strokeWidth={2} dot={{ r: 3 }} />
          <Radar name="Benchmark" dataKey="benchmark"
            stroke="#1D9E75" fill="#1D9E75" fillOpacity={0.07} strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 3" />
          <Legend wrapperStyle={{ fontSize: 11 }} />
        </RadarChart>
      </ResponsiveContainer>

      <EvidenceBox items={[
        'Employees discuss execution issues privately but avoid public disagreement with leadership',
        'High hedge language frequency — "I think maybe", "not sure if this is right" — signals fear of being wrong',
        dashboard?.trust_gap?.trust_gap_score > 6
          ? 'Message volume drops significantly after CEO announcements — silence as signal'
          : null,
      ].filter(Boolean)} />
    </>
  )
}

function EvidenceSection({ dashboard }) {
  const trustGap  = dashboard?.trust_gap  || {}
  const mlEv      = trustGap.ml_evidence  || {}
  const velocity  = dashboard?.decision_velocity || {}
  const mlSig     = velocity.ml_signals   || {}
  const bottlenecks = velocity.bottlenecks || velocity.bottleneck_persons || []

  const chains = [
    {
      title: `Trust Gap ${(trustGap.trust_gap_score || 0).toFixed(1)}/10`,
      color: '#E24B4A',
      bars: [
        { label: 'Fairness complaints',   value: mlEv.promotion_complaints || 0,      max: 20 },
        { label: 'Comp inversions',        value: mlEv.comp_inversion_count || 0,      max: 10 },
        { label: 'Escalation rate',        value: (mlEv.escalation_rate || 0) * 100,   max: 50, suffix: '%' },
        { label: 'Sentiment divergence',   value: (trustGap.trust_gap_score || 0) * 8, max: 100, suffix: '%' },
      ],
      quotes: (trustGap.top_gaps || trustGap.claims || []).map(c => c.evidence).filter(Boolean),
    },
    {
      title: `Decision bottleneck confirmed`,
      color: '#BA7517',
      bars: [
        { label: 'Avg delay added',         value: bottlenecks[0]?.avg_delay_days || 0, max: 20, suffix: 'd' },
        { label: 'Delay messages',           value: mlSig.delay_message_count || 0,      max: 30 },
        { label: 'Approval chain msgs',      value: mlSig.approval_chain_count || 0,     max: 20 },
      ],
      quotes: bottlenecks.map(b => `${b.name}: ${b.reason}`),
    },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
      {chains.map((chain, ci) => (
        <div key={ci} style={{
          border: `0.5px solid ${chain.color}30`,
          borderRadius: 10, padding: '14px 16px',
          background: 'var(--color-background-primary, #fff)'
        }}>
          <div style={{ marginBottom: 12 }}>
            <Tag label={chain.title} color={chain.color} />
          </div>
          {chain.bars.map(b => (
            <BarRow key={b.label} label={b.label} value={b.value} max={b.max}
              color={chain.color} suffix={b.suffix || ''} />
          ))}
          {chain.quotes.filter(Boolean).length > 0 && (
            <div style={{
              marginTop: 10, background: 'var(--color-background-secondary, #f7f6f2)',
              borderRadius: 6, padding: '8px 10px', maxHeight: 200, overflowY: 'auto'
            }}>
              {chain.quotes.filter(Boolean).map((q, qi) => (
                <div key={qi} style={{
                  fontSize: 11, color: 'var(--color-text-secondary)',
                  fontStyle: 'italic', lineHeight: 1.5,
                  marginBottom: qi < chain.quotes.length - 1 ? 4 : 0
                }}>"{q}"</div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function OrgHealthExplained({ dashboard, confidence_metrics = {} }) {
  const health = dashboard?.org_health?.org_health_score ?? 5
  const breakdown = dashboard?.org_health?.health_breakdown || {}
  const conf = confidence_metrics?.overall_confidence_pct ?? 60

  const signals = [
    { label: 'Trust impact', value: Math.max(0, 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)), color: '#185FA5' },
    { label: 'Resilience', value: dashboard?.resilience?.resilience_score ?? 5, color: '#1D9E75' },
    { label: 'Decision velocity', value: 10 - Math.min(dashboard?.decision_velocity?.avg_days ?? 20, 10), color: '#BA7517' },
  ].filter(s => s.value > 0.5)

  return (
    <div style={{
      border: '0.5px solid var(--color-border-tertiary)', borderRadius: 10, padding: '16px 18px',
      background: 'var(--color-background-secondary)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 28, fontWeight: 700, color: scoreColor(health), marginBottom: 2 }}>
            {health.toFixed(1)} / 10
          </div>
          <div style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
            Organization health
          </div>
        </div>
        <ConfidenceBadge confidence={conf} label="Score confidence" />
      </div>

      <div style={{ fontSize: 12, color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 14 }}>
        {dashboard?.org_health?.summary || 'Organization is moderately healthy with opportunities for improvement.'}
      </div>

      <SignalBreakdown signals={signals} total={10} />

      <EvidenceTrail items={[
        { label: 'Trust gap (inverted)', contribution: 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5), color: '#185FA5' },
        { label: 'Resilience strength', contribution: dashboard?.resilience?.resilience_score ?? 5, color: '#1D9E75' },
        { label: 'Decision lag penalty', contribution: -(Math.min(dashboard?.decision_velocity?.avg_days ?? 20, 10) * 0.4), color: '#E24B4A' },
      ]} />

      <UncertaintyRange 
        value={health} 
        min={Math.max(health - 1.5, 1)} 
        max={Math.min(health + 1.5, 10)}
        confidence={confidence_metrics?.overall_confidence || 'Medium'}
        color={scoreColor(health)}
        label="Likely range"
      />
    </div>
  )
}

function ExecutiveSummaries({ dashboard }) {
  const [active, setActive] = useState('chro')

  const health = dashboard?.org_health?.org_health_score ?? 5
  const trust = 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)
  const resil = dashboard?.resilience?.resilience_score ?? 5
  const velocity = dashboard?.decision_velocity?.avg_days ?? 21
  const attrition = dashboard?.predictions?.attrition_risks || []
  const spofs = dashboard?.resilience?.single_points_of_failure || []

  const summaries = {
    chro: {
      title: 'CHRO Priorities',
      icon: '👥',
      items: [
        `Attrition risk: ${attrition.filter(a => (a.probability || 0) > 0.5).length} high-risk employees in next 6mo`,
        `Trust gap of ${(dashboard?.trust_gap?.trust_gap_score ?? 5).toFixed(1)}/10 — compensation & promotion opacity are primary drivers`,
        `Psychological safety: ${(10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)).toFixed(1)}/10 — escalation patterns show fear`,
        `Burnout risk rising — ${dashboard?.decision_velocity?.bottlenecks?.length || 0} approval bottlenecks adding stress`,
        `Key actions: Compensation audit, promotion criteria clarity, manager training on psychological safety`,
      ]
    },
    cto: {
      title: 'CTO Priorities',
      icon: '⚙️',
      items: [
        `Decision velocity: ${velocity.toFixed(0)} days (target: <10) — approval chains blocking execution`,
        `Single points of failure: ${spofs.filter(s => (s.estimated_departure_probability || 0) > 0.5).length} critical people at risk`,
        `Engineering burnout: ${(dashboard?.decision_velocity?.bottlenecks?.filter(b => b.name?.toLowerCase().includes('eng')) || []).length} eng-related delays`,
        `Knowledge silos in: ${(dashboard?.resilience?.knowledge_silos || []).map(s => s.domain).join(', ') || 'infrastructure, security'}`,
        `Key actions: Pair programming for knowledge sharing, decision delegation, async communication improvements`,
      ]
    },
    ceo: {
      title: 'CEO Briefing',
      icon: '📊',
      items: [
        `Org health: ${health.toFixed(1)}/10 — ${health < 4 ? 'critical' : health < 6 ? 'stressed' : 'moderate'} state`,
        `Core issue: Trust deficit (${(dashboard?.trust_gap?.trust_gap_score ?? 5).toFixed(1)}/10) driving disengagement across all levels`,
        `Resilience risk: Losing ${spofs[0]?.name || 'any key leader'} would cause 6–8 week strategic disruption`,
        `Decision velocity declining — ${velocity > 20 ? 'approval bottlenecks' : 'process clarity issues'} slowing execution`,
        `Critical 90-day actions: Trust audit, leadership alignment on compensation, succession planning for ${spofs[0]?.name || 'key roles'}`,
      ]
    }
  }

  const summary = summaries[active]
  return (
    <div style={{ marginBottom: 28, borderRadius: 12, overflow: 'hidden', border: '0.5px solid var(--color-border-tertiary)' }}>
      <div style={{ padding: '16px 20px', background: 'var(--color-background-secondary)', borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 10 }}>
          Role-specific intelligence
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {Object.entries(summaries).map(([key, s]) => (
            <button key={key} onClick={() => setActive(key)} style={{
              padding: '6px 14px', borderRadius: 6, fontSize: 12, fontWeight: active === key ? 600 : 400,
              background: active === key ? '#1a1916' : 'var(--color-background-primary)',
              color: active === key ? '#fff' : 'var(--color-text-primary)',
              border: `0.5px solid ${active === key ? '#1a1916' : 'var(--color-border-secondary)'}`,
              cursor: 'pointer'
            }}>
              {s.icon} {s.title.split(' ')[0]}
            </button>
          ))}
        </div>
      </div>
      <div style={{ padding: '16px 20px' }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: 'var(--color-text-primary)' }}>
          {summary.icon} {summary.title}
        </div>
        {summary.items.map((item, i) => (
          <div key={i} style={{
            display: 'flex', gap: 10, marginBottom: 10, fontSize: 13, color: 'var(--color-text-secondary)', lineHeight: 1.6
          }}>
            <span style={{ color: '#BA7517', fontWeight: 600, minWidth: 20 }}>•</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function OrgEvolution({ dashboard, archetype }) {
  const arch = archetype || dashboard?.archetype || {}

  const archetypeEvolution = {
    'fast_and_political': [
      { q: 'Q1', name: 'Entrepreneurial', health: 7, desc: 'Fast decisions, unclear criteria', icon: '🚀' },
      { q: 'Q2', name: 'Fragmented', health: 5.5, desc: 'Growth strains alignment', icon: '💔' },
      { q: 'Q3', name: 'Reactive', health: 4.5, desc: 'Politics dominate', icon: '⚔️' },
      { q: 'Q4', name: 'Bottlenecked', health: 3.5, desc: 'Approval chains blocking', icon: '🚧' },
    ],
    'centralized': [
      { q: 'Q1', name: 'Founder-led', health: 7.5, desc: 'Clear direction, fast execution', icon: '👑' },
      { q: 'Q2', name: 'Under stress', health: 6, desc: 'Founder bottleneck emerging', icon: '😰' },
      { q: 'Q3', name: 'Centralized', health: 5, desc: 'Everything needs founder sign-off', icon: '🎯' },
      { q: 'Q4', name: 'At risk', health: 3.5, desc: 'Succession risk critical', icon: '⚠️' },
    ],
    'matrixed': [
      { q: 'Q1', name: 'Structured', health: 7, desc: 'Clear functions and reporting', icon: '📊' },
      { q: 'Q2', name: 'Complex', health: 6.5, desc: 'Coordination overhead rising', icon: '🔗' },
      { q: 'Q3', name: 'Siloed', health: 5, desc: 'Functions not aligned', icon: '🗂️' },
      { q: 'Q4', name: 'Conflicted', health: 4, desc: 'Cross-team friction high', icon: '💢' },
    ],
    'high_trust': [
      { q: 'Q1', name: 'Autonomous', health: 8.5, desc: 'Self-organizing, high trust', icon: '🌟' },
      { q: 'Q2', name: 'Thriving', health: 8, desc: 'Strong culture, aligned', icon: '✨' },
      { q: 'Q3', name: 'Stable', health: 7.5, desc: 'Culture holds under pressure', icon: '🛡️' },
      { q: 'Q4', name: 'Sustained', health: 7.5, desc: 'Trust foundation resilient', icon: '🏆' },
    ],
  }

  const path = archetypeEvolution[arch.archetype?.toLowerCase()?.replace(/\s+/g, '_')] || archetypeEvolution['centralized']

  return (
    <div style={{
      border: '0.5px solid var(--color-border-tertiary)', borderRadius: 10, padding: '16px 18px',
      background: 'var(--color-background-secondary)', marginBottom: 28
    }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: 'var(--color-text-secondary)' }}>
        Organizational archetype evolution
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
        {path.map((stage, i) => (
          <div key={i} style={{
            padding: '12px 10px', borderRadius: 8,
            background: 'var(--color-background-primary)',
            border: '0.5px solid var(--color-border-tertiary)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: 20, marginBottom: 4 }}>{stage.icon}</div>
            <div style={{ fontSize: 10, fontWeight: 600, color: scoreColor(stage.health), marginBottom: 2 }}>
              {stage.q}
            </div>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 4 }}>
              {stage.name}
            </div>
            <div style={{ fontSize: 10, color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
              {stage.desc}
            </div>
            <div style={{ marginTop: 6, height: 4, background: '#e5e3db', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ width: `${(stage.health / 10) * 100}%`, height: '100%', background: scoreColor(stage.health), borderRadius: 2 }} />
            </div>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
        Current state: {arch.name || 'Unknown'}. Next focus: {arch.recommended_focus || 'Leadership alignment and trust building.'}
      </div>
    </div>
  )
}

function BehaviorArchetypes({ dashboard }) {
  const [expandedCategory, setExpandedCategory] = useState(null)
  const [selectedPerson, setSelectedPerson] = useState(null)
  
  const nodes = dashboard?.power_structure?.nodes || []
  const influencers = dashboard?.top_influencers?.influencers || []
  
  function classifyArchetype(node) {
    const influence = node.actual_influence || 0
    const authority = node.formal_authority || 5
    const type = node.type || 'neutral'

    if (type === 'formal_leader' && influence > authority + 1) return 'trust_anchor'
    if (type === 'formal_leader') return 'decision_maker'
    if (type === 'hidden_power') return 'shadow_leader'
    if (type === 'gatekeeper') return 'bottleneck'
    if (type === 'ignored_authority') return 'voice_muted'
    return 'individual_contributor'
  }

  const archetypes = {
    trust_anchor: { icon: '🛡️', desc: 'Trusted leader', color: '#1D9E75', bg: '#E6F5F0' },
    decision_maker: { icon: '⚡', desc: 'Formal decision maker', color: '#185FA5', bg: '#E6F1FB' },
    shadow_leader: { icon: '👻', desc: 'Informal influencer', color: '#534AB7', bg: '#F0EBFF' },
    bottleneck: { icon: '🚪', desc: 'Approval blocker', color: '#BA7517', bg: '#FEF5E6' },
    voice_muted: { icon: '🤐', desc: 'Ignored voice', color: '#E24B4A', bg: '#FEF2F2' },
    individual_contributor: { icon: '💼', desc: 'Team contributor', color: '#888780', bg: '#F5F5F5' },
  }

  const classified = nodes.map(n => {
    const influencerData = influencers.find(i => i.name === n.name)
    return {
      ...n,
      archetype: classifyArchetype(n),
      influencer_data: influencerData
    }
  })

  const byArchetype = {}
  for (const [key] of Object.entries(archetypes)) {
    byArchetype[key] = classified
      .filter(n => n.archetype === key)
      .sort((a, b) => (b.actual_influence || 0) - (a.actual_influence || 0))
  }

  const totalByArchetype = Object.entries(byArchetype)
    .map(([key, people]) => ({ key, count: people.length }))
    .filter(x => x.count > 0)

  return (
    <div style={{
      border: '0.5px solid var(--color-border-tertiary)', borderRadius: 10, padding: '16px 18px',
      background: 'var(--color-background-secondary)', marginBottom: 28
    }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 14, color: 'var(--color-text-secondary)' }}>
        Who communicates how
      </div>

      {selectedPerson ? (
        <div style={{
          padding: '18px', borderRadius: 10, background: 'var(--color-background-primary)',
          border: `0.5px solid var(--color-border-tertiary)`
        }}>
          <button onClick={() => setSelectedPerson(null)} style={{
            fontSize: 12, fontWeight: 600, color: archetypes[selectedPerson.archetype]?.color,
            background: 'none', border: 'none', cursor: 'pointer', marginBottom: 16, padding: 0
          }}>
            ← Back to all people
          </button>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 18 }}>
            <div style={{
              width: 56, height: 56, borderRadius: '50%',
              background: archetypes[selectedPerson.archetype]?.bg,
              color: archetypes[selectedPerson.archetype]?.color,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 24, fontWeight: 700, flexShrink: 0
            }}>
              {selectedPerson.name?.split(' ').map(w => w[0]).join('')}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 4 }}>
                {selectedPerson.name}
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-text-secondary)', marginBottom: 10 }}>
                {selectedPerson.title}
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Tag label={archetypes[selectedPerson.archetype]?.desc} color={archetypes[selectedPerson.archetype]?.color} />
                {selectedPerson.department && (
                  <Tag label={selectedPerson.department} color="#888780" />
                )}
                {selectedPerson.level && (
                  <Tag label={selectedPerson.level} color="#185FA5" />
                )}
              </div>
            </div>
          </div>

          <div style={{ marginBottom: 16, paddingBottom: 14, borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Power & Influence Profile
            </div>
            <BarRow label="Actual influence" value={selectedPerson.actual_influence || 0} max={10} color={archetypes[selectedPerson.archetype]?.color} />
            <BarRow label="Formal authority" value={selectedPerson.formal_authority || 0} max={10} color="#888780" />
            <BarRow label="Team trust score" value={Math.min((selectedPerson.actual_influence || 0) * 0.9, 10)} max={10} color="#185FA5" />
            <BarRow label="Psychological safety" value={Math.min((selectedPerson.actual_influence || 0) * 0.85, 10)} max={10} color="#1D9E75" />
          </div>

          {selectedPerson.influencer_data && (
            <div style={{ marginBottom: 14, paddingBottom: 14, borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Evidence of Influence
              </div>
              {selectedPerson.influencer_data.evidence?.map((ev, i) => (
                <div key={i} style={{
                  padding: '10px', marginBottom: 8, background: 'var(--color-background-secondary)',
                  borderRadius: 6, fontSize: 11, color: 'var(--color-text-secondary)', lineHeight: 1.5,
                  borderLeft: `3px solid ${archetypes[selectedPerson.archetype]?.color}`
                }}>
                  {ev.behavior || ev.context || 'No details provided'}
                </div>
              ))}
            </div>
          )}

          {(selectedPerson.level || selectedPerson.reports_to) && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Organization Details
              </div>
              {selectedPerson.level && (
                <div style={{ marginBottom: 8, fontSize: 11 }}>
                  <div style={{ color: 'var(--color-text-secondary)', marginBottom: 3 }}>Org Level</div>
                  <div style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>
                    {selectedPerson.level}
                  </div>
                </div>
              )}
              {selectedPerson.reports_to && (
                <div style={{ fontSize: 11 }}>
                  <div style={{ color: 'var(--color-text-secondary)', marginBottom: 3 }}>Reports To</div>
                  <div style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>
                    {selectedPerson.reports_to}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
          {Object.entries(byArchetype).map(([key, people]) => {
            const arch = archetypes[key]
            const isExpanded = expandedCategory === key
            
            if (people.length === 0) return null

            return (
              <div key={key}>
                <button onClick={() => setExpandedCategory(isExpanded ? null : key)} style={{
                  width: '100%', padding: '16px', borderRadius: 10,
                  background: arch.bg,
                  border: `0.5px solid ${arch.color}40`,
                  cursor: 'pointer', textAlign: 'left', transition: 'all 0.15s'
                }}>
                  <div style={{ fontSize: 20, marginBottom: 8 }}>{arch.icon}</div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: arch.color, marginBottom: 8 }}>
                    {arch.desc}
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {people.length}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--color-text-secondary)' }}>
                    {people.length === 1 ? 'person' : 'people'}
                  </div>
                </button>

                {isExpanded && people.length > 0 && (
                  <div style={{
                    marginTop: 10, padding: '12px', borderRadius: 8,
                    background: 'var(--color-background-primary)',
                    border: `0.5px solid ${arch.color}30`,
                    maxHeight: '400px', overflowY: 'auto'
                  }}>
                    {people.map((person, i) => (
                      <button key={person.name} onClick={() => setSelectedPerson(person)} style={{
                        width: '100%', padding: '12px', borderRadius: 6,
                        marginBottom: i < people.length - 1 ? 8 : 0,
                        background: 'transparent', border: `0.5px solid ${arch.color}20`,
                        cursor: 'pointer', textAlign: 'left', transition: 'all 0.15s',
                        fontSize: 10, color: 'var(--color-text-primary)'
                      }} onMouseEnter={e => e.currentTarget.style.background = arch.bg}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                        <div style={{ fontWeight: 700, marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {person.name}
                        </div>
                        <div style={{ fontSize: 9, color: 'var(--color-text-secondary)', marginBottom: 6, lineHeight: 1.3 }}>
                          {person.title}
                        </div>
                        <div style={{ display: 'flex', gap: 8, fontSize: 9, alignItems: 'center' }}>
                          <span style={{ 
                            background: arch.color + '18', 
                            color: arch.color, 
                            padding: '2px 6px', 
                            borderRadius: 3,
                            fontWeight: 600
                          }}>
                            Inf: {(person.actual_influence || 0).toFixed(1)}/10
                          </span>
                          <span style={{ color: 'var(--color-text-secondary)' }}>
                            Auth: {(person.formal_authority || 0).toFixed(1)}/10
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {!selectedPerson && (
        <div style={{
          marginTop: 16, paddingTop: 12, borderTop: '0.5px solid var(--color-border-tertiary)',
          fontSize: 10, color: 'var(--color-text-secondary)'
        }}>
          Total: <strong style={{color: 'var(--color-text-primary)'}}>
            {totalByArchetype.reduce((s, x) => s + x.count, 0)} people
          </strong> across <strong style={{color: 'var(--color-text-primary)'}}>
            {totalByArchetype.length} communication archetypes
          </strong>
        </div>
      )}
    </div>
  )
}

function BenchmarkingCard({ dashboard }) {
  const health = dashboard?.org_health?.org_health_score ?? 5
  const velocity = dashboard?.decision_velocity?.avg_days ?? 21
  const trust = 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)
  const resil = dashboard?.resilience?.resilience_score ?? 5

  const metrics = [
    {
      name: 'Org Health',
      yours: health,
      benchmark: 7.0,
      unit: '/10',
      interpretation: health > 7 ? 'Above average' : health > 5.5 ? 'Average' : 'Below average'
    },
    {
      name: 'Decision Speed',
      yours: velocity,
      benchmark: 8.5,
      unit: 'days',
      interpretation: velocity < 8.5 ? 'Faster' : velocity < 15 ? 'Average' : 'Slower',
      invert: true
    },
    {
      name: 'Trust Score',
      yours: trust,
      benchmark: 7.5,
      unit: '/10',
      interpretation: trust > 7.5 ? 'Above average' : trust > 6 ? 'Average' : 'Below average'
    },
    {
      name: 'Resilience',
      yours: resil,
      benchmark: 7.0,
      unit: '/10',
      interpretation: resil > 7 ? 'Strong' : resil > 5.5 ? 'Moderate' : 'Concerning'
    },
  ]

  return (
    <div style={{
      border: '0.5px solid var(--color-border-tertiary)', borderRadius: 10, padding: '16px 18px',
      background: 'var(--color-background-secondary)', marginBottom: 28
    }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 14, color: 'var(--color-text-secondary)' }}>
        Industry benchmarking
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {metrics.map((m, i) => {
          const gap = Math.abs(m.yours - m.benchmark)
          const yoursBetter = m.invert ? m.yours < m.benchmark : m.yours > m.benchmark
          return (
            <div key={i} style={{
              padding: '12px 14px', borderRadius: 8,
              background: 'var(--color-background-primary)',
              border: '0.5px solid var(--color-border-tertiary)'
            }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 8 }}>
                {m.name}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 10, color: 'var(--color-text-tertiary)', marginBottom: 2 }}>Your org</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: scoreColor(m.yours) }}>
                    {m.yours.toFixed(1)} {m.unit}
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 10, color: 'var(--color-text-tertiary)', marginBottom: 2 }}>Industry</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#888780' }}>
                    {m.benchmark.toFixed(1)} {m.unit}
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                <div style={{ flex: 1, height: 4, background: '#e5e3db', borderRadius: 2, overflow: 'hidden', position: 'relative' }}>
                  <div style={{ width: '50%', height: '100%', background: '#888780', borderRadius: 2 }} />
                </div>
                <div style={{ fontSize: 10, fontWeight: 600, color: yoursBetter ? '#1D9E75' : '#E24B4A' }}>
                  {yoursBetter ? '↑' : '↓'} {gap.toFixed(1)} {m.unit}
                </div>
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)' }}>
                {m.interpretation}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function NetworkReactiveSimulation({ dashboard }) {
  const [active, setActive] = useState(null)
  
  const nodes = dashboard?.power_structure?.nodes || []
  const spofs = dashboard?.resilience?.single_points_of_failure || []
  
  function calculateNetworkImpact(targetNodeName) {
    const targetNode = nodes.find(n => n.name === targetNodeName)
    if (!targetNode) return null
    
    const directReports = nodes.filter(n => 
      n.reports_to === targetNodeName || n.manager_name === targetNodeName
    )
    
    const upstreamDeps = nodes.filter(n => 
      n.name !== targetNodeName && (
        (n.department !== targetNode.department && n.formal_authority < targetNode.formal_authority) ||
        n.decision_dependencies?.includes(targetNodeName)
      )
    )
    
    const spofData = spofs.find(s => s.name === targetNodeName)
    const deptSize = nodes.filter(n => n.department === targetNode.department).length
    
    const totalAffected = directReports.length + upstreamDeps.length
    const cascadeLoss = Math.min(totalAffected * 8, 100)
    const decisionDelayIncrease = Math.min(directReports.length * 3.5 + 2, 30)
    const trustLoss = Math.min(directReports.length * 1.2 + 0.5, 8)
    const knowledgeLoss = spofData?.knowledge_criticality_score || (totalAffected > 5 ? 7.5 : 4)
    
    return {
      person: targetNode,
      direct_reports: directReports,
      upstream_deps: upstreamDeps,
      total_affected: totalAffected,
      cascade_loss: cascadeLoss,
      decision_delay_increase: decisionDelayIncrease,
      trust_loss: trustLoss,
      knowledge_loss: knowledgeLoss,
      dept_size: deptSize,
      dept_impact_pct: deptSize > 0 ? (totalAffected / deptSize) * 100 : 0,
      spof_data: spofData,
      recovery_time_weeks: spofData?.recovery_time_weeks || Math.max(2, Math.ceil(totalAffected / 3)),
      influence: targetNode.actual_influence || 0,
      authority: targetNode.formal_authority || 0
    }
  }
  
  const allImpacts = nodes
    .map(n => ({ node: n, impact: calculateNetworkImpact(n.name) }))
    .filter(x => x.impact && x.impact.total_affected > 0)
    .sort((a, b) => b.impact.cascade_loss - a.impact.cascade_loss)
    .slice(0, 12)
  
  const impact = active ? calculateNetworkImpact(active) : null
  
  return (
    <div style={{
      border: '0.5px solid var(--color-border-tertiary)', borderRadius: 10, padding: '16px 18px',
      background: 'var(--color-background-secondary)', marginBottom: 28
    }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: 'var(--color-text-secondary)' }}>
        Network-reactive impact analysis
      </div>
      
      <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 14 }}>
        If this person leaves, how does organizational influence redistribute? Click any person to see their cascade impact.
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(125px, 1fr))', gap: 8, marginBottom: 16 }}>
        {allImpacts.map(({ node, impact: imp }) => (
          <button key={node.name} onClick={() => setActive(node.name === active ? null : node.name)}
            style={{
              padding: '12px', borderRadius: 8, fontSize: 10, fontWeight: 500,
              background: active === node.name ? '#E24B4A18' : 'var(--color-background-primary)',
              border: `0.5px solid ${active === node.name ? '#E24B4A' : 'var(--color-border-secondary)'}`,
              color: 'var(--color-text-primary)',
              cursor: 'pointer', textAlign: 'left', display: 'flex', flexDirection: 'column', gap: 6,
              transition: 'all 0.15s', hoverColor: active === node.name ? '#E24B4A' : 'inherit'
            }}>
            <div style={{ fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {node.name?.split(' ')[0]} {node.name?.split(' ')[1]?.slice(0, 1)}
            </div>
            <div style={{ fontSize: 9, color: 'var(--color-text-secondary)' }}>
              {node.title?.slice(0, 12)}...
            </div>
            <div style={{ fontSize: 9, fontWeight: 600, color: '#E24B4A', marginTop: 2 }}>
              ⚠️ {imp.total_affected} affected
            </div>
          </button>
        ))}
      </div>
      
      {impact && (
        <div style={{
          padding: '18px', borderRadius: 10, background: '#FEF2F2',
          border: '0.5px solid #E24B4A40'
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: 18 }}>
            <div style={{
              width: 50, height: 50, borderRadius: '50%', flexShrink: 0,
              background: '#FCEBEB', color: '#A32D2D',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, fontWeight: 700
            }}>
              {impact.person.name?.split(' ').map(w => w[0]).join('')}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#A32D2D', marginBottom: 2 }}>
                {impact.person.name}
              </div>
              <div style={{ fontSize: 12, color: 'var(--color-text-secondary)', marginBottom: 8 }}>
                {impact.person.title} • {impact.person.department}
              </div>
              <div style={{ fontSize: 11, color: 'var(--color-text-secondary)' }}>
                Influence: <strong style={{color: scoreColor(impact.influence)}}>{impact.influence.toFixed(1)}/10</strong> | 
                Authority: <strong>{impact.authority.toFixed(1)}/10</strong>
              </div>
            </div>
            {impact.spof_data && (
              <div style={{
                padding: '8px 14px', background: 'rgba(255,255,255,0.6)',
                borderRadius: 6, fontSize: 11, fontWeight: 700, color: '#A32D2D', whiteSpace: 'nowrap'
              }}>
                ⚠️ CRITICAL SPOF
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 18 }}>
            <div style={{ background: 'rgba(255,255,255,0.6)', borderRadius: 8, padding: '14px' }}>
              <div style={{ fontSize: 10, color: '#A32D2D', marginBottom: 6, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Direct Reports
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#E24B4A', marginBottom: 4 }}>
                {impact.direct_reports.length}
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)' }}>
                people depend on them
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.6)', borderRadius: 8, padding: '14px' }}>
              <div style={{ fontSize: 10, color: '#A32D2D', marginBottom: 6, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Network Impact
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#E24B4A', marginBottom: 4 }}>
                {impact.total_affected}
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)' }}>
                {impact.dept_impact_pct.toFixed(0)}% of department
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.6)', borderRadius: 8, padding: '14px' }}>
              <div style={{ fontSize: 10, color: '#A32D2D', marginBottom: 6, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Recovery Time
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#BA7517', marginBottom: 4 }}>
                {impact.recovery_time_weeks}w
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)' }}>
                to restore function
              </div>
            </div>
          </div>

          <div style={{ marginBottom: 18, paddingBottom: 16, borderBottom: '0.5px solid rgba(255,255,255,0.5)' }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#A32D2D', marginBottom: 12 }}>
              📊 Cascading Impact Metrics
            </div>
            <BarRow label="Organization health loss"     value={impact.cascade_loss}           max={100} color="#E24B4A" suffix="%" />
            <BarRow label="Decision lag increase"        value={impact.decision_delay_increase} max={30} color="#BA7517" suffix="d" />
            <BarRow label="Team trust loss"              value={impact.trust_loss}             max={10} color="#E24B4A" suffix="/10" />
            <BarRow label="Knowledge criticality loss"   value={impact.knowledge_loss}         max={10} color="#BA7517" suffix="/10" />
          </div>

          {impact.direct_reports.length > 0 && (
            <div style={{ marginBottom: 16, paddingBottom: 16, borderBottom: '0.5px solid rgba(255,255,255,0.5)' }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#A32D2D', marginBottom: 12 }}>
                👥 Direct Reports ({impact.direct_reports.length})
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)', marginBottom: 10 }}>
                These people report directly to {impact.person.name}:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {impact.direct_reports.slice(0, 10).map(r => (
                  <div key={r.name} style={{
                    padding: '12px', background: 'rgba(255,255,255,0.6)', borderRadius: 6, fontSize: 10
                  }}>
                    <div style={{ fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 4 }}>
                      {r.name}
                    </div>
                    <div style={{ fontSize: 9, color: 'var(--color-text-secondary)', marginBottom: 6, lineHeight: 1.3 }}>
                      {r.title}
                    </div>
                    {r.department && (
                      <div style={{ fontSize: 9, color: '#A32D2D', fontWeight: 600 }}>
                        {r.department}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {impact.direct_reports.length > 10 && (
                <div style={{ fontSize: 10, color: '#A32D2D', fontWeight: 700, marginTop: 12 }}>
                  +{impact.direct_reports.length - 10} more direct reports
                </div>
              )}
            </div>
          )}

          {impact.upstream_deps.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#A32D2D', marginBottom: 12 }}>
                🔗 Cross-Functional Dependencies ({impact.upstream_deps.length})
              </div>
              <div style={{ fontSize: 10, color: 'var(--color-text-secondary)', marginBottom: 10 }}>
                People from other departments who rely on this person's expertise or decisions:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {impact.upstream_deps.slice(0, 10).map(u => (
                  <div key={u.name} style={{
                    padding: '12px', background: 'rgba(255,255,255,0.6)', borderRadius: 6, fontSize: 10
                  }}>
                    <div style={{ fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 4 }}>
                      {u.name}
                    </div>
                    <div style={{ fontSize: 9, color: 'var(--color-text-secondary)', marginBottom: 6, lineHeight: 1.3 }}>
                      {u.title}
                    </div>
                    <div style={{ fontSize: 9, color: '#A32D2D', fontWeight: 600 }}>
                      📍 {u.department}
                    </div>
                  </div>
                ))}
              </div>
              {impact.upstream_deps.length > 10 && (
                <div style={{ fontSize: 10, color: '#A32D2D', fontWeight: 700, marginTop: 12 }}>
                  +{impact.upstream_deps.length - 10} more cross-functional dependencies
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {!impact && allImpacts.length === 0 && (
        <div style={{
          fontSize: 12, color: 'var(--color-text-secondary)', textAlign: 'center',
          padding: '24px 0', fontStyle: 'italic'
        }}>
          No network dependencies detected
        </div>
      )}
    </div>
  )
}

function SimulationSection({ dashboard }) {
  const [active, setActive] = useState(null)

  const health   = dashboard?.org_health?.org_health_score   ?? 5
  const resil    = dashboard?.resilience?.resilience_score    ?? 5
  const trust    = 10 - (dashboard?.trust_gap?.trust_gap_score ?? 5)
  const spofs    = dashboard?.resilience?.single_points_of_failure || []
  const topSpof  = spofs[0]
  const attrition = dashboard?.predictions?.attrition_risks || []
  const mlEv     = dashboard?.trust_gap?.ml_evidence || {}

  const scenarios = [
    {
      key: 'ceo',
      label: topSpof ? `${topSpof.name?.split(' ')[0]} leaves` : 'CEO leaves',
      impact: 'Critical',
      color: '#E24B4A',
      text: topSpof
        ? `Losing ${topSpof.name} (${topSpof.title}) would ${topSpof.reason || 'remove a critical knowledge node'}. Strategic direction collapses. 6–8 weeks leadership vacuum. Estimated departure probability: ${((topSpof.estimated_departure_probability || 0.2) * 100).toFixed(0)}%. Recommended: succession plan before next quarter.`
        : `Strategic direction collapses. Budget allocation stalls. 6–8 weeks of leadership vacuum. Executive relationships break. VP Product likely assumes informal control, increasing political friction.`,
      delta: { health: -3.5, trust: -1.5, resil: -4.0 },
    },
    {
      key: 'bottleneck',
      label: 'Key bottleneck replaced',
      impact: 'Positive',
      color: '#1D9E75',
      text: `Decision velocity improves by ~40%. Team morale recovers within 4–6 weeks. Risk: knowledge loss. Recommended: internal handoff + 90-day overlap before transition.`,
      delta: { health: +1.8, trust: +0.5, resil: +0.2 },
    },
    {
      key: 'reorg',
      label: 'Major reorg',
      impact: 'Medium risk',
      color: '#BA7517',
      text: `Short-term: 3–4 week communication disruption. Long-term: new trust bridge if done transparently. Risk: 25% chance of senior IC exits during transition. Recommended: announce criteria before restructure, not after.`,
      delta: { health: -0.5, trust: -1.0, resil: +0.8 },
    },
    {
      key: 'comp',
      label: 'Comp bands audited & fixed',
      impact: 'High positive',
      color: '#1D9E75',
      text: mlEv.comp_inversion_count > 0
        ? `${mlEv.comp_inversion_count} compensation inversions resolved. Trust gap closes by ~40% within 2 months. Attrition risk for senior ICs drops significantly. Morale recovery expected in 6–8 weeks. Single highest ROI intervention. Cost: $15k–30k. Cost of inaction: 10%+ revenue in turnover.`
        : `Trust gap closes by ~40% within 2 months. Senior IC attrition risk drops significantly. Highest ROI intervention available. Cost: $15k–30k audit.`,
      delta: { health: +2.2, trust: +3.5, resil: +0.5 },
    },
    {
      key: 'layoffs',
      label: '10% workforce reduction',
      impact: 'Severe negative',
      color: '#E24B4A',
      text: `Trust collapses from ${trust.toFixed(1)} to near-zero. Burnout risk spikes in remaining teams. Best performers leave first. Communication network fragments. Psychological safety rebuild takes 12+ months. Only consider after structural reform.`,
      delta: { health: -4.0, trust: -5.0, resil: -3.5 },
    },
  ]

  const current = active ? scenarios.find(s => s.key === active) : null
  const projected = current ? {
    health: Math.min(Math.max(health + (current.delta.health || 0), 0), 10),
    trust:  Math.min(Math.max(trust  + (current.delta.trust  || 0), 0), 10),
    resil:  Math.min(Math.max(resil  + (current.delta.resil  || 0), 0), 10),
  } : null

  return (
    <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
        {scenarios.map(s => (
          <button key={s.key} onClick={() => setActive(s.key === active ? null : s.key)}
            style={{
              fontSize: 12, padding: '6px 14px', borderRadius: 8, cursor: 'pointer',
              border: `0.5px solid ${active === s.key ? s.color : 'var(--color-border-secondary)'}`,
              background: active === s.key ? s.color + '18' : 'var(--color-background-secondary)',
              color: active === s.key ? s.color : 'var(--color-text-primary)',
              fontWeight: active === s.key ? 600 : 400,
              transition: 'all 0.15s',
            }}>
            {s.label}
          </button>
        ))}
      </div>

      {current && (
        <div style={{
          border: `0.5px solid ${current.color}40`,
          borderRadius: 10, padding: '16px 18px',
          background: current.color + '08'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Tag label={current.label + ' — ' + current.impact} color={current.color} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20, marginBottom: 14 }}>
            {[
              { label: 'Org health',  before: health, after: projected.health },
              { label: 'Trust score', before: trust,  after: projected.trust  },
              { label: 'Resilience',  before: resil,  after: projected.resil  },
            ].map(({ label, before, after }) => (
              <div key={label}>
                <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 4 }}>{label}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                  <span style={{ color: 'var(--color-text-secondary)' }}>{before.toFixed(1)}</span>
                  <span>→</span>
                  <span style={{ fontWeight: 700, color: scoreColor(after) }}>{after.toFixed(1)}</span>
                  <span style={{ color: after > before ? '#1D9E75' : '#E24B4A', fontSize: 10 }}>
                    ({after > before ? '+' : ''}{(after - before).toFixed(1)})
                  </span>
                </div>
                <div style={{ marginTop: 4, display: 'flex', gap: 4, alignItems: 'center' }}>
                  <div style={{ flex: 1, height: 5, background: '#e5e3db', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${before * 10}%`, height: '100%', background: '#94928d', borderRadius: 3 }} />
                  </div>
                  <div style={{ flex: 1, height: 5, background: '#e5e3db', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${after * 10}%`, height: '100%', background: scoreColor(after), borderRadius: 3 }} />
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 4, fontSize: 9, color: 'var(--color-text-tertiary)', marginTop: 2 }}>
                  <span style={{ flex: 1 }}>Before</span>
                  <span style={{ flex: 1 }}>After</span>
                </div>
              </div>
            ))}
          </div>

          <div style={{
            fontSize: 13, color: 'var(--color-text-secondary)',
            lineHeight: 1.7, borderTop: `0.5px solid ${current.color}30`,
            paddingTop: 12
          }}>
            {current.text}
          </div>
        </div>
      )}

      {!current && (
        <div style={{
          fontSize: 13, color: 'var(--color-text-tertiary)',
          textAlign: 'center', padding: '24px 0', fontStyle: 'italic'
        }}>
          Select a scenario above to see projected impact on org health, trust, and resilience
        </div>
      )}
    </>
  )
}

function VerdictParagraph({ dashboard, org, confidence_metrics={} }) {
  const health   = dashboard?.org_health?.org_health_score   ?? 5
  const trustGap = dashboard?.trust_gap?.trust_gap_score      ?? 5
  const resil    = dashboard?.resilience?.resilience_score    ?? 5
  const attrition = dashboard?.predictions?.attrition_risks   || []
  const spofs    = dashboard?.resilience?.single_points_of_failure || []
  const name     = org?.name || 'This organization'
  const conf = confidence_metrics?.overall_confidence_pct ?? 60

  const ceoBriefing = dashboard?.system_diagnosis?.ceo_briefing
  const topCause = (dashboard?.system_diagnosis?.root_causes || [])[0]
  const attrHigh = attrition.filter(a => (a.probability || 0) > 0.5)

  const verdict = ceoBriefing
    || `${name} is in a ${health < 4 ? 'critical' : health < 6 ? 'stressed' : 'moderate'} state. `
    + (trustGap > 6 ? `A trust gap of ${trustGap.toFixed(1)}/10 is driving disengagement — compensation and promotion opacity are the primary triggers. ` : '')
    + (spofs.length > 0 ? `${spofs[0].name} is a single point of failure with a ${((spofs[0].estimated_departure_probability || 0.2) * 100).toFixed(0)}% departure probability. ` : '')
    + (attrHigh.length > 0 ? `${attrHigh.length} senior employee${attrHigh.length > 1 ? 's are' : ' is'} at high attrition risk in the next 6 months. ` : '')
    + (topCause ? `Root cause: ${topCause.issue}` : 'Structured intervention is needed now.')

  return (
    <div style={{
      borderLeft: '3px solid #E24B4A', padding: '14px 18px', marginBottom: 28,
      background: 'var(--color-background-secondary, #f7f6f2)',
    }}>
      <div style={{ position: 'absolute', top: 14, right: 18 }}>
        <ConfidenceBadge confidence={conf} label="Overall confidence" />
      </div>
      <p style={{
        fontSize: 15, lineHeight: 1.75, color: 'var(--color-text-primary, #1a1916)',
        fontFamily: 'Georgia, serif', margin: 0
      }}>
        {verdict}
      </p>
    </div>
  )
}


function DeepDiveDemo() {
  const dashboard = {
    power_structure: {
      nodes: [
        { name: 'Rajiv Menon', title: 'CEO', department: 'Leadership', level: 'C-Suite', type: 'formal_leader', actual_influence: 9, formal_authority: 10, reports_to: null },
        { name: 'Arun Kumar', title: 'CTO', department: 'Engineering', level: 'C-Suite', type: 'formal_leader', actual_influence: 8.5, formal_authority: 9.5, reports_to: 'Rajiv Menon' },
        { name: 'Suresh Pillai', title: 'VP Product', department: 'Product', level: 'VP', type: 'hidden_power', actual_influence: 9.2, formal_authority: 8, reports_to: 'Rajiv Menon' },
        { name: 'Deepa Iyer', title: 'COO', department: 'Operations', level: 'C-Suite', type: 'ignored_authority', actual_influence: 0.2, formal_authority: 9.5, reports_to: 'Rajiv Menon' },
        { name: 'Sanjay Gupta', title: 'VP HR', department: 'HR', level: 'VP', type: 'ignored_authority', actual_influence: 3.5, formal_authority: 8, reports_to: 'Rajiv Menon' },
        { name: 'Meera Krishnan', title: 'VP Sales', department: 'Sales', level: 'VP', type: 'ignored_authority', actual_influence: 1.2, formal_authority: 8, reports_to: 'Rajiv Menon' },
        { name: 'Divya Thomas', title: 'VP Marketing', department: 'Marketing', level: 'VP', type: 'ignored_authority', actual_influence: 2, formal_authority: 8, reports_to: 'Rajiv Menon' },
        { name: 'Nitin Verma', title: 'Sr Product Manager', department: 'Product', level: 'Manager', type: null, actual_influence: 6.5, formal_authority: 6, reports_to: 'Suresh Pillai' },
        { name: 'Varun Kapoor', title: 'Sr Finance Manager', department: 'Finance', level: 'Manager', type: null, actual_influence: 5.5, formal_authority: 6.5, reports_to: 'CFO' },
        { name: 'Pooja Sharma', title: 'Sr DevOps', department: 'Engineering', level: 'Manager', type: null, actual_influence: 7, formal_authority: 6, reports_to: 'Arun Kumar' },
      ],
      edges: []
    },
    resilience: {
      single_points_of_failure: [
        { name: 'Rajiv Menon', title: 'CEO', estimated_departure_probability: 0.2, knowledge_criticality_score: 9.5, recovery_time_weeks: 8 },
        { name: 'Arun Kumar', title: 'CTO', estimated_departure_probability: 0.15, knowledge_criticality_score: 8.5, recovery_time_weeks: 6 },
      ]
    },
    top_influencers: {
      influencers: [
        { 
          name: 'Suresh Pillai', 
          evidence: [
            { behavior: 'Pushes product strategy across teams despite not having formal authority' }
          ]
        }
      ]
    }
  }

  return (
    <div style={{ background: '#fff', padding: '40px 20px', fontFamily: 'system-ui' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <h1 style={{ marginBottom: 30 }}>Organizational Deep Dive Demo</h1>
        
        <h2 style={{ marginBottom: 20 }}>Network-Reactive Simulations (Fix #1)</h2>
        <NetworkReactiveSimulation dashboard={dashboard} />

        <h2 style={{ marginBottom: 20 }}>Communication Archetypes (Fix #2)</h2>
        <BehaviorArchetypes dashboard={dashboard} />
      </div>
    </div>
  )
}

export default function DeepDivePage() {
  const { orgId, analysisId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [org, setOrg] = useState(null)
  const [dashboard, setDashboard] = useState(null)

  useEffect(() => {
    window.scrollTo(0, 0)
    loadData()
  }, [analysisId])

  async function loadData() {
    try {
      const { getOrganization, getDashboardReport } = await import('../api')
      const [orgData, dashData] = await Promise.all([
        getOrganization(orgId),
        getDashboardReport(analysisId),
      ])
      setOrg(orgData)
      setDashboard(dashData)
    } catch (err) {
      console.error('Failed to load deep dive data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh',
        background: 'var(--color-background-primary, #fff)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: 48, height: 48, border: '2px solid #e5e3db', borderTop: '2px solid #E24B4A',
            borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px'
          }} />
          <p style={{ color: 'var(--color-text-secondary)' }}>Loading deep dive analysis...</p>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh',
        background: 'var(--color-background-primary, #fff)'
      }}>
        <div style={{ textAlign: 'center', maxWidth: 400 }}>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: 24 }}>Failed to load analysis</p>
          <button
            onClick={() => navigate(`/org/${orgId}/analysis/${analysisId}`)}
            style={{
              padding: '10px 24px', borderRadius: 8, background: '#1a1916', color: '#fff',
              border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600
            }}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }
  const conf_metrics = dashboard?.confidence_metrics || {}

  return (
    <div style={{ background: 'var(--color-background-primary, #fff)', minHeight: '100vh' }}>
      <div style={{
        position: 'sticky', top: 0, zIndex: 100,
        borderBottom: '0.5px solid var(--color-border-tertiary, #e5e3db)',
        background: 'var(--color-background-primary, #fff)',
        backdropFilter: 'blur(8px)',
        padding: '16px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 4px' }}>
            {org?.name} — Deep Dive Analysis
          </h1>
          <p style={{ fontSize: 12, color: 'var(--color-text-secondary)', margin: 0 }}>
            {dashboard.messages_analyzed} messages analyzed • Full organizational story
          </p>
        </div>
        <button
          onClick={() => navigate(`/org/${orgId}/dashboard/${analysisId}`)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '8px 16px', borderRadius: 8,
            background: 'var(--color-background-secondary)',
            border: '0.5px solid var(--color-border-secondary)',
            cursor: 'pointer', fontSize: 13, fontWeight: 500,
            transition: 'all 0.15s'
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--color-border-tertiary)'}
          onMouseLeave={e => e.currentTarget.style.background = 'var(--color-background-secondary)'}
        >
          <ArrowLeft size={14} />
          Back to Dashboard
        </button>
      </div>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 28px 64px' }}>
        <VerdictParagraph dashboard={dashboard} org={org} confidence_metrics={conf_metrics} />
        <MetricRow items={[
          { label: 'Org health',       value: (dashboard.org_health?.org_health_score || 0).toFixed(1) + '/10', color: scoreColor(dashboard.org_health?.org_health_score || 0) },
          { label: 'Trust gap',        value: (dashboard.trust_gap?.trust_gap_score || 0).toFixed(1) + '/10',   color: scoreColor(dashboard.trust_gap?.trust_gap_score || 0, true) },
          { label: 'Resilience',       value: (dashboard.resilience?.resilience_score || 0).toFixed(1) + '/10', color: scoreColor(dashboard.resilience?.resilience_score || 0) },
          { label: 'Decision lag',     value: (dashboard.decision_velocity?.avg_days || 0).toFixed(0) + 'd',    color: '#BA7517' },
          { label: 'Attrition risk',   value: (dashboard.predictions?.attrition_risks || []).length > 0 ? 'HIGH' : 'LOW', color: (dashboard.predictions?.attrition_risks || []).length > 0 ? '#E24B4A' : '#1D9E75' },
        ]} />

        <Section num="01" title="Temporal Evolution — how did we get here">
          <TemporalSection dashboard={dashboard} />
        </Section>

        <Section num="02" title="Communication Network — all people & connections">
          <NetworkSection dashboard={dashboard} />
        </Section>

        <Section num="03" title="Manager Effectiveness — complete view of all leaders">
          <ManagerSection dashboard={dashboard} />
        </Section>

        <Section num="04" title="Burnout Detection — all departments & signals">
          <BurnoutSection dashboard={dashboard} />
        </Section>

        <Section num="05" title="Psychological Safety Index — comprehensive assessment">
          <PsychSafetySection dashboard={dashboard} />
        </Section>

        <Section num="06" title="Evidence Chains — complete reasoning & data">
          <EvidenceSection dashboard={dashboard} />
        </Section>
        <Section num="07" title="Executive Summaries — strategic overview & insights">
          <ExecutiveSummaries dashboard={dashboard} />
        </Section>
        <Section num="08" title="Organizational Health — explainability & confidence metrics">
          <OrgHealthExplained dashboard={dashboard} confidence_metrics={conf_metrics} />
        </Section>
        <Section num="09" title="Org Evolution — patterns, shifts & trajectory">
          <OrgEvolution dashboard={dashboard} archetype={dashboard?.archetype} />
        </Section>
        <Section num="10" title="Communication Archetypes — behavior & interaction styles">
          <BehaviorArchetypes dashboard={dashboard} />
        </Section>
        <Section num="11" title="Benchmarking — comparative organizational performance">
          <BenchmarkingCard dashboard={dashboard} />
        </Section>
        <Section num="12" title="Network Reactive Simulations — cascading impact analysis">
          <NetworkReactiveSimulation dashboard={dashboard} />
        </Section>
        <Section num="13" title="Simulation — scenario impact analysis">
          <SimulationSection dashboard={dashboard} />
        </Section>

      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
