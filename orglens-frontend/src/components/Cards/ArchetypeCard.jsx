import { TrendingUp, AlertCircle, Lightbulb } from 'lucide-react'

function ArchetypeIcon({ archetype }) {
  const icons = {
    fast_and_political: '⚡',
    slow_but_healthy: '🌱',
    chaotic_startup: '🚀',
    waiting_for_exodus: '🔴',
    high_performance: '🏆',
    bureaucratic: '📋',
    fragmented: '💔',
    stable_mature: '🏛️',
  }

  return icons[archetype] || '🏢'
}

export function ArchetypeCard({ data, expanded, onToggle }) {
  if (!data) return null

  const arch = data

  return (
    <div
      className={`rounded-2xl border shadow-neo-sm hover:shadow-neo-md transition-all ${
        arch.archetype === 'high_performance'
          ? 'border-emerald-300 bg-emerald-50'
          : arch.archetype === 'waiting_for_exodus'
          ? 'border-red-300 bg-red-50'
          : arch.archetype === 'fast_and_political'
          ? 'border-orange-300 bg-orange-50'
          : arch.archetype === 'slow_but_healthy'
          ? 'border-blue-300 bg-blue-50'
          : 'border-neutral-200 bg-white'
      }`}
    >
      <button
        onClick={onToggle}
        className="w-full text-left p-6 flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <span className="text-3xl">
            <ArchetypeIcon archetype={arch.archetype} />
          </span>

          <div>
            <h3 className="font-bold text-neutral-900">
              {arch.name || 'Organizational Archetype'}
            </h3>

            <p className="text-xs text-neutral-500 mt-0.5">
              {arch.description || 'Operating model classification'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {arch.confidence_pct != null && (
            <span className="px-3 py-1.5 rounded-lg bg-neutral-100 border border-neutral-200">
              <span className="font-bold text-sm text-neutral-600">
                {arch.confidence_pct}%
              </span>
            </span>
          )}

          {expanded ? '🔽' : '▶️'}
        </div>
      </button>

      {expanded && (
        <div className="px-6 pb-6 border-t border-neutral-100 pt-5 space-y-5">

          {/* Executive Explanation */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-neutral-50 to-blue-50 border border-neutral-200">

            <p className="text-xs font-bold text-neutral-600 uppercase mb-2">
              🧠 How This Classification Was Derived
            </p>

            <p className="text-sm text-neutral-700 leading-relaxed">
              This archetype is not a label — it is a behavioral pattern derived from
              communication speed, trust signals, organizational health indicators,
              and contradiction density across the dataset. It represents how the
              organization actually behaves, not how it describes itself.
            </p>

            {Array.isArray(arch.classification_reasons) &&
              arch.classification_reasons.length > 0 && (
                <div className="mt-4 space-y-2">
                  {arch.classification_reasons.map((r, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-white border border-neutral-200"
                    >
                      <p className="text-sm text-neutral-700">
                        • {r}
                      </p>
                    </div>
                  ))}
                </div>
              )}
          </div>

          {/* Metrics Snapshot */}
          {arch.supporting_metrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">

              {Object.entries(arch.supporting_metrics).map(([key, value], i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-neutral-50 border border-neutral-200"
                >
                  <p className="text-xs text-neutral-500 mb-1 capitalize">
                    {key.replace(/_/g, ' ')}
                  </p>

                  <p className="text-sm font-bold text-neutral-800">
                    {typeof value === 'number' ? value.toFixed(1) : String(value)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Strengths */}
          {Array.isArray(arch.strengths) && arch.strengths.length > 0 && (
            <div>
              <p className="text-xs font-bold text-emerald-600 uppercase mb-2">
                💪 What Works Well
              </p>

              <div className="space-y-2">
                {arch.strengths.map((s, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-emerald-50 border border-emerald-100"
                  >
                    <p className="text-sm text-neutral-800">✓ {s}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Vulnerabilities */}
          {Array.isArray(arch.vulnerabilities) &&
            arch.vulnerabilities.length > 0 && (
              <div>
                <p className="text-xs font-bold text-red-600 uppercase mb-2">
                  ⚠️ Structural Risks
                </p>

                <div className="space-y-2">
                  {arch.vulnerabilities.map((v, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-red-50 border border-red-100"
                    >
                      <p className="text-sm text-neutral-800">• {v}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Risk + Trajectory */}
          <div className="grid grid-cols-2 gap-3">

            {arch.risk_level && (
              <div className="p-4 rounded-xl border border-neutral-200 bg-white">
                <p className="text-xs text-neutral-500 mb-1">Risk Level</p>

                <p className={`text-sm font-bold capitalize ${
                  arch.risk_level === 'high'
                    ? 'text-red-600'
                    : arch.risk_level === 'medium'
                    ? 'text-amber-600'
                    : 'text-emerald-600'
                }`}>
                  {arch.risk_level}
                </p>
              </div>
            )}

            {arch.trajectory && (
              <div className="p-4 rounded-xl border border-neutral-200 bg-white">
                <p className="text-xs text-neutral-500 mb-1">Trajectory</p>

                <p className={`text-sm font-bold capitalize ${
                  arch.trajectory === 'declining'
                    ? 'text-red-600'
                    : arch.trajectory === 'improving'
                    ? 'text-emerald-600'
                    : 'text-neutral-700'
                }`}>
                  {arch.trajectory}
                </p>
              </div>
            )}
          </div>

          {/* Recommended Focus */}
          {Array.isArray(arch.recommended_focus) &&
            arch.recommended_focus.length > 0 && (
              <div className="p-5 rounded-2xl bg-blue-50 border border-blue-200">

                <p className="text-xs font-bold text-blue-700 uppercase mb-3">
                  🎯 Executive Action Plan
                </p>

                <div className="space-y-2">
                  {arch.recommended_focus.map((rec, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-blue-600 font-bold">{i + 1}.</span>
                      <p className="text-sm text-blue-900">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Confidence */}
          {arch.confidence_pct != null && (
            <div className="p-3 rounded-lg bg-neutral-100 border border-neutral-200">
              <p className="text-xs text-neutral-600">
                Classification confidence: <strong>{arch.confidence_pct}%</strong>
              </p>
            </div>
          )}

        </div>
      )}
    </div>
  )
}