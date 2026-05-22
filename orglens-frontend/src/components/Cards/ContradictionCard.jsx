import { AlertTriangle, TrendingDown, TrendingUp } from 'lucide-react'

function SeverityBadge({ severity }) {
  const styles = {
    critical: { bg: 'bg-red-100', border: 'border-red-300', text: 'text-red-700', label: '🔴 Critical' },
    high: { bg: 'bg-orange-100', border: 'border-orange-300', text: 'text-orange-700', label: '🟠 High' },
    medium: { bg: 'bg-amber-100', border: 'border-amber-300', text: 'text-amber-700', label: '🟡 Medium' },
    low: { bg: 'bg-yellow-100', border: 'border-yellow-300', text: 'text-yellow-700', label: '🟨 Low' },
  }

  const style = styles[severity] || styles.medium

  return (
    <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${style.bg} ${style.border} ${style.text}`}>
      {style.label}
    </span>
  )
}

export function ContradictionCard({ data }) {
  const contradictions = data || []

  if (!contradictions || contradictions.length === 0) {
    return (
      <p className="text-sm text-neutral-400">
        No major contradictions detected
      </p>
    )
  }

  return (
    <div className="space-y-4">
      {contradictions.map((contra, i) => (
        <div
          key={i}
          className="p-4 rounded-xl bg-white border border-red-200 space-y-3"
        >
          {/* Claim vs Reality */}
          <div>
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1">
                <p className="text-xs font-bold text-neutral-500 uppercase mb-1">
                  They claim
                </p>

                <p className="text-sm font-semibold text-neutral-900">
                  "{contra.claim}"
                </p>
              </div>

              <SeverityBadge severity={contra.severity} />
            </div>
          </div>

          {/* Gap visualization */}
          <div className="p-3 rounded-lg bg-red-50 border border-red-200">
            <p className="text-xs text-neutral-500 mb-2">
              Reality
            </p>

            <p className="text-sm text-red-700 font-semibold">
              {contra.observed_reality}
            </p>

            <div className="mt-2 w-full h-2 bg-red-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-red-500"
                style={{ width: `${(contra.gap_score / 10) * 100}%` }}
              />
            </div>

            <p className="text-xs text-red-600 mt-1 font-bold">
              Gap: {contra.gap_score.toFixed(1)}/10
            </p>
          </div>

          {/* Evidence */}
          {contra.evidence_quotes && contra.evidence_quotes.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-bold text-neutral-500 uppercase">
                Evidence
              </p>

              {contra.evidence_quotes.slice(0, 3).map((quote, j) => (
                <div
                  key={j}
                  className="p-2.5 rounded-lg bg-red-50 border border-red-200"
                >
                  <p className="text-xs text-red-700 italic">
                    "{quote}"
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Root causes */}
          {contra.root_causes && contra.root_causes.length > 0 && (
            <div>
              <p className="text-xs font-bold text-neutral-500 uppercase mb-2">
                Why this gap exists
              </p>

              <ul className="space-y-1">
                {contra.root_causes.map((cause, j) => (
                  <li key={j} className="text-xs text-neutral-700">
                    • {cause}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Impact */}
          {contra.impact && (
            <div className="p-3 rounded-lg bg-red-100 border border-red-200">
              <p className="text-xs font-bold text-red-700 mb-1">
                ⚠️ Business Impact
              </p>

              <p className="text-xs text-red-700">
                {contra.impact}
              </p>
            </div>
          )}

          {/* Recommendation */}
          {contra.recommendation && (
            <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
              <p className="text-xs font-bold text-emerald-700 mb-1">
                ✅ How to close the gap
              </p>

              <p className="text-xs text-emerald-700">
                {contra.recommendation}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}