import { AlertTriangle, CheckCircle } from 'lucide-react'

function ConfidenceBadge({ level, pct }) {
  const styles = {
    critical: {
      bg: 'bg-red-100',
      border: 'border-red-300',
      text: 'text-red-700',
      label: '🔴 Critical',
    },
    low: {
      bg: 'bg-orange-100',
      border: 'border-orange-300',
      text: 'text-orange-700',
      label: '🟠 Low',
    },
    medium: {
      bg: 'bg-amber-100',
      border: 'border-amber-300',
      text: 'text-amber-700',
      label: '🟡 Medium',
    },
    high: {
      bg: 'bg-lime-100',
      border: 'border-lime-300',
      text: 'text-lime-700',
      label: '🟢 High',
    },
    very_high: {
      bg: 'bg-emerald-100',
      border: 'border-emerald-300',
      text: 'text-emerald-700',
      label: '✅ Very High',
    },
  }

  const style = styles[level] || styles.medium

  return (
    <div className={`px-4 py-3 rounded-xl border ${style.bg} ${style.border}`}>
      <p className={`text-sm font-bold ${style.text}`}>
        {style.label} — {pct}% Confidence
      </p>
    </div>
  )
}

export function DataQualityCard({ data, expanded, onToggle }) {
  if (!data) {
    return (
      <div className="p-6 rounded-2xl border border-neutral-200 bg-white">
        <p className="text-sm text-neutral-400">
          No data quality metrics available
        </p>
      </div>
    )
  }

  const hasWarnings = data.warnings?.length > 0
  const isActionable = data.overall_confidence_pct >= 65

  const confidenceColorMap = {
    critical: 'text-red-600',
    low: 'text-orange-600',
    medium: 'text-amber-600',
    high: 'text-lime-600',
    very_high: 'text-emerald-600',
  }

  return (
    <div className="rounded-2xl border border-neutral-200 bg-white shadow-neo-sm hover:shadow-neo-md transition-all">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full text-left p-6 flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <span className="text-3xl">📊</span>

          <div>
            <h3 className="font-bold text-neutral-900">
              Data Quality & Confidence
            </h3>

            <p className="text-xs text-neutral-500 mt-0.5">
              How reliable are these findings?
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 rounded-lg bg-neutral-100 border border-neutral-200">
            <span
              className={`font-bold text-sm ${
                confidenceColorMap[data.overall_confidence] ||
                'text-amber-600'
              }`}
            >
              {data.overall_confidence_pct}%
            </span>
          </span>

          {expanded ? '🔽' : '▶️'}
        </div>
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-6 pb-6 border-t border-neutral-100 pt-5 space-y-5">

          {/* Confidence Level */}
          <div>
            <p className="text-xs font-bold text-neutral-500 uppercase mb-3">
              Confidence Level
            </p>

            <ConfidenceBadge
              level={data.overall_confidence}
              pct={data.overall_confidence_pct}
            />
          </div>

          {/* Data Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200">
              <p className="text-xs text-neutral-500 mb-1">
                Total Messages
              </p>

              <p className="text-lg font-bold text-neutral-800">
                {data.total_messages || 0}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200">
              <p className="text-xs text-neutral-500 mb-1">
                People Analyzed
              </p>

              <p className="text-lg font-bold text-neutral-800">
                {data.total_employees || 0}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200">
              <p className="text-xs text-neutral-500 mb-1">
                Msgs/Person
              </p>

              <p className="text-lg font-bold text-neutral-800">
                {data.messages_per_person?.toFixed?.(1) || '0.0'}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-neutral-50 border border-neutral-200">
              <p className="text-xs text-neutral-500 mb-1">
                Time Range
              </p>

              <p className="text-lg font-bold text-neutral-800">
                {data.date_range_days || 0}d
              </p>
            </div>
          </div>

          {/* Coverage by Function */}
          {Object.keys(data.coverage_by_function || {}).length > 0 && (
            <div>
              <p className="text-xs font-bold text-neutral-500 uppercase mb-3">
                Coverage by Department
              </p>

              <div className="space-y-2">
                {Object.entries(data.coverage_by_function).map(([func, pct]) => {
                  const status =
                    pct >= 70
                      ? 'good'
                      : pct >= 30
                      ? 'weak'
                      : 'critical'

                  const statusColor =
                    status === 'good'
                      ? 'bg-emerald-100 text-emerald-700'
                      : status === 'weak'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-red-100 text-red-700'

                  return (
                    <div key={func} className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-semibold text-neutral-800">
                            {func}
                          </p>

                          <span
                            className={`text-xs font-bold px-2 py-0.5 rounded-full ${statusColor}`}
                          >
                            {pct}%
                          </span>
                        </div>

                        <div className="w-full h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              status === 'good'
                                ? 'bg-emerald-500'
                                : status === 'weak'
                                ? 'bg-amber-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Coverage by Level */}
          {Object.keys(data.coverage_by_level || {}).length > 0 && (
            <div>
              <p className="text-xs font-bold text-neutral-500 uppercase mb-3">
                Coverage by Org Level
              </p>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(data.coverage_by_level).map(([level, pct]) => (
                  <div
                    key={level}
                    className="p-2 rounded-lg bg-neutral-50 border border-neutral-200 text-center"
                  >
                    <p className="text-xs text-neutral-500 mb-0.5">
                      {level}
                    </p>

                    <p
                      className={`text-sm font-bold ${
                        pct >= 70
                          ? 'text-emerald-600'
                          : pct >= 30
                          ? 'text-amber-600'
                          : 'text-red-600'
                      }`}
                    >
                      {pct}%
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Confidence Breakdown */}
          {data.confidence_breakdown &&
            Object.keys(data.confidence_breakdown).length > 0 && (
              <div>
                <p className="text-xs font-bold text-neutral-500 uppercase mb-3">
                  Why This Confidence Score?
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {Object.entries(data.confidence_breakdown).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="p-3 rounded-xl bg-neutral-50 border border-neutral-200"
                      >
                        <p className="text-xs text-neutral-500 mb-1 capitalize">
                          {key.replace(/_/g, ' ')}
                        </p>

                        <p className="text-lg font-bold text-neutral-800">
                          {value}%
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
          )}

          {/* Reliable Signals */}
          {data.strengths_detected?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-bold text-emerald-600 uppercase">
                ✅ Reliable Signals
              </p>

              {data.strengths_detected.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-emerald-50 border border-emerald-200"
                >
                  <p className="text-sm text-emerald-800">
                    {item}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Confidence Limitations */}
          {data.limitations_detected?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-bold text-amber-600 uppercase">
                ⚠️ Confidence Limitations
              </p>

              {data.limitations_detected.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-amber-50 border border-amber-200"
                >
                  <p className="text-sm text-amber-800">
                    {item}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Improvement Recommendations */}
          {data.recommended_data_improvements?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-bold text-blue-600 uppercase">
                📈 How To Improve Reliability
              </p>

              {data.recommended_data_improvements.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-blue-50 border border-blue-200"
                >
                  <p className="text-sm text-blue-900">
                    {item}
                  </p>
                </div>
              ))}
            </div>
          )}
          {/* Warnings */}
          {hasWarnings && (
            <div className="space-y-2">
              <p className="text-xs font-bold text-red-600 uppercase">
                ⚠️ Data Quality Warnings
              </p>

              {data.warnings.map((warning, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-red-50 border border-red-200"
                >
                  <p className="text-sm text-red-700">
                    {typeof warning === 'string'
                      ? warning
                      : warning.message}
                  </p>
                </div>
              ))}
            </div>
          )}

        </div>
      )}
    </div>
  )
}