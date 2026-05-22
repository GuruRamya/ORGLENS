import { TrendingUp, Zap, Users, Heart } from 'lucide-react'
import { useState } from 'react'

function StrengthIcon({ category }) {
  const icons = {
    resilient_teams: '💪',
    healthy_managers: '👨‍💼',
    trust_clusters: '🤝',
    velocity_hotspots: '⚡',
    collaboration_zones: '🌐',
    psychological_safety: '🛡️',
    knowledge_sharing: '📚',
    innovation_culture: '💡',
  }

  return icons[category] || '⭐'
}

export function PositiveSignalsCard({ data, expanded, onToggle }) {
  const signals = Array.isArray(data) ? data : []

  if (signals.length === 0) {
    return (
      <div className="rounded-2xl border border-neutral-200 bg-white shadow-neo-sm">
        <button
          onClick={onToggle}
          className="w-full text-left p-6 flex items-center justify-between"
        >
          <div className="flex items-center gap-4">
            <span className="text-3xl">⭐</span>

            <div>
              <h3 className="font-bold text-neutral-900">
                Strengths & Positives
              </h3>

              <p className="text-xs text-neutral-500 mt-0.5">
                No clear strengths detected yet
              </p>
            </div>
          </div>
        </button>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-emerald-200 bg-emerald-50 shadow-neo-sm hover:shadow-neo-md transition-all">
      <button
        onClick={onToggle}
        className="w-full text-left p-6 flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <span className="text-3xl">⭐</span>

          <div>
            <h3 className="font-bold text-neutral-900">
              Strengths & Positives
            </h3>

            <p className="text-xs text-neutral-500 mt-0.5">
              What's working well — build on these
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 rounded-lg bg-emerald-100 border border-emerald-200">
            <span className="font-bold text-sm text-emerald-600">
              {signals.length}
            </span>
          </span>

          {expanded ? '🔽' : '▶️'}
        </div>
      </button>

      {expanded && (
        <div className="px-6 pb-6 border-t border-emerald-100 pt-5 space-y-5">

          {/* Executive Summary */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-100 to-green-50 border border-emerald-200">
            <p className="text-xs font-bold text-emerald-800 uppercase mb-2">
              🌱 Positive Culture Indicators
            </p>

            <p className="text-sm text-emerald-900 leading-relaxed">
              Even in organizations with visible dysfunction, healthy patterns usually exist.
              These signals represent teams, managers, or workflows that are already working better
              than the surrounding system. Protecting and scaling these behaviors is often faster
              than rebuilding culture from scratch.
            </p>
          </div>

          {/* Signal Cards (NEW VERSION) */}
          {signals.map((signal, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl bg-white border border-emerald-200 shadow-sm space-y-4"
            >

              <div className="flex items-start justify-between gap-4">

                <div className="flex-1">

                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">
                      <StrengthIcon category={signal.category} />
                    </span>

                    <div>
                      <p className="font-bold text-neutral-900 capitalize">
                        {(signal.category || 'positive signal').replace(/_/g, ' ')}
                      </p>

                      <p className="text-xs text-neutral-500">
                        Organizational strength detected
                      </p>
                    </div>
                  </div>

                  {signal.description && (
                    <p className="text-sm text-neutral-700 leading-relaxed">
                      {signal.description}
                    </p>
                  )}
                </div>

                {signal.strength_score != null && (
                  <div className="text-center flex-shrink-0">
                    <div
                      className={`w-16 h-16 rounded-2xl flex items-center justify-center border text-2xl font-bold ${
                        signal.strength_score >= 8
                          ? 'bg-emerald-100 border-emerald-300 text-emerald-700'
                          : signal.strength_score >= 6
                          ? 'bg-lime-100 border-lime-300 text-lime-700'
                          : 'bg-amber-100 border-amber-300 text-amber-700'
                      }`}
                    >
                      {Number(signal.strength_score).toFixed(1)}
                    </div>

                    <p className="text-xs text-neutral-400 mt-1">
                      strength
                    </p>
                  </div>
                )}
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">

                {signal.affected_people != null && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
                    <p className="text-xs text-neutral-500 mb-1">
                      People Impacted
                    </p>

                    <p className="text-lg font-bold text-emerald-700">
                      {signal.affected_people}
                    </p>
                  </div>
                )}

                {signal.growth_potential && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
                    <p className="text-xs text-neutral-500 mb-1">
                      Growth Potential
                    </p>

                    <p className="text-sm font-bold text-emerald-700 capitalize">
                      {signal.growth_potential}
                    </p>
                  </div>
                )}

                {signal.confidence_pct != null && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
                    <p className="text-xs text-neutral-500 mb-1">
                      Confidence
                    </p>

                    <p className="text-lg font-bold text-emerald-700">
                      {signal.confidence_pct}%
                    </p>
                  </div>
                )}

                {signal.momentum && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
                    <p className="text-xs text-neutral-500 mb-1">
                      Momentum
                    </p>

                    <p className="text-sm font-bold text-emerald-700 capitalize">
                      {signal.momentum}
                    </p>
                  </div>
                )}
              </div>

              {/* Evidence */}
              {Array.isArray(signal.evidence) &&
                signal.evidence.length > 0 && (
                  <div className="space-y-2">

                    <p className="text-xs font-bold text-neutral-500 uppercase">
                      Supporting Evidence
                    </p>

                    <div className="space-y-2">
                      {signal.evidence.map((e, j) => (
                        <div
                          key={j}
                          className="p-2.5 rounded-lg bg-neutral-50 border border-neutral-200"
                        >
                          <p className="text-sm text-neutral-700">
                            ✓ {e}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* Functional Areas */}
              {Array.isArray(signal.affected_functions) &&
                signal.affected_functions.length > 0 && (
                  <div>

                    <p className="text-xs font-bold text-neutral-500 uppercase mb-2">
                      Strongest In
                    </p>

                    <div className="flex flex-wrap gap-2">
                      {signal.affected_functions.map((func, j) => (
                        <span
                          key={j}
                          className="text-xs px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200 font-semibold"
                        >
                          {func}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              {/* Strategic Meaning */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-white to-emerald-50 border border-emerald-100">

                <p className="text-xs font-bold text-emerald-700 uppercase mb-2">
                  🎯 Why This Matters
                </p>

                <p className="text-sm text-neutral-700 leading-relaxed">
                  This signal indicates an area of the organization that can become a
                  cultural anchor during transformation efforts. Strong teams and
                  healthy collaboration patterns are easier to scale than rebuilding
                  trust from zero.
                </p>
              </div>
            </div>
          ))}

          {/* Bottom Summary */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-100 to-lime-50 border border-emerald-300">
            <p className="text-xs font-bold text-emerald-800 uppercase mb-2">
              💚 Strategic Recommendation
            </p>

            <p className="text-sm text-emerald-900 leading-relaxed">
              {signals.length} positive organizational signal
              {signals.length > 1 ? 's were' : ' was'} detected.
              Instead of focusing only on dysfunction, leadership should identify how
              these successful behaviors emerged naturally and intentionally replicate
              them across the organization.
            </p>
          </div>

        </div>
      )}
    </div>
  )
}