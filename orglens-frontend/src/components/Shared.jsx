import { useState } from 'react'
import { ChevronDown, Upload, Type, Sparkles, AlertCircle, TrendingUp } from 'lucide-react'

export function FileDropZone({ accept, label, sublabel, onChange, fileName }) {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <label className="block cursor-pointer group">
      <div
        onDragEnter={() => setIsDragging(true)}
        onDragLeave={() => setIsDragging(false)}
        onDrop={() => setIsDragging(false)}
        className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 overflow-hidden ${
          fileName
            ? 'border-maroon-400 bg-maroon-50 shadow-neo-md'
            : isDragging
            ? 'border-maroon-500 bg-neutral-100 scale-102 shadow-neo-md'
            : 'border-neutral-300 hover:border-maroon-500 hover:bg-neutral-50 group-hover:shadow-neo-md'
        }`}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-neutral-50 to-neutral-100 group-hover:from-neutral-100 group-hover:to-neutral-50 transition-all duration-700" />
        <input
          type="file"
          accept={accept}
          className="hidden"
          onChange={e => onChange(e.target.files[0] || null)}
        />
        {fileName ? (
          <div className="relative flex items-center justify-center gap-4 py-2">
            <div className="relative">
              <div className="absolute inset-0 bg-maroon-400 blur-xl rounded-2xl opacity-20" />
              <div className="relative w-12 h-12 rounded-2xl bg-maroon-600 flex items-center justify-center text-white shadow-neo-md">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="text-left">
              <p className="text-maroon-600 font-semibold text-sm">{fileName}</p>
              <p className="text-neutral-500 text-xs mt-0.5">✓ Ready to process</p>
            </div>
          </div>
        ) : (
          <>
            <div className="relative w-16 h-16 rounded-2xl bg-neutral-200 border border-neutral-300 flex items-center justify-center mx-auto mb-4 group-hover:border-maroon-500 group-hover:shadow-neo-md transition-all duration-300">
              <svg className="w-7 h-7 text-neutral-500 group-hover:text-maroon-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-neutral-900 font-semibold text-sm">{label}</p>
            <p className="text-neutral-600 text-xs mt-1">{sublabel}</p>
            <p className="text-neutral-500 text-xs mt-3">Or drag & drop your file here</p>
          </>
        )}
      </div>
    </label>
  )
}

export function InputMethodTabs({ options, value, onChange }) {
  return (
    <div className="overflow-x-auto pb-2">
      <div className="flex gap-2 p-1.5 bg-neutral-100 rounded-2xl border border-neutral-200 shadow-neo-sm min-w-min">
        {options.map(opt => {
          const isActive = value === opt
          return (
            <button
              key={opt}
              onClick={() => onChange(opt)}
              className={`relative px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${
                isActive
                  ? 'text-white bg-maroon-600 shadow-neo-sm'
                  : 'text-neutral-600 hover:text-neutral-900 hover:bg-white'
              }`}
            >
              {opt.includes('Upload') && <Upload size={16} />}
              {opt.includes('Type') && <Type size={16} />}
              <span className="relative flex items-center gap-2">
                {opt}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export function TextInput({ value, onChange, placeholder, rows = 6 }) {
  const [isFocused, setIsFocused] = useState(false)
  return (
    <div className="relative">
      <div className={`absolute -inset-0.5 bg-maroon-500 rounded-2xl blur opacity-0 transition-opacity duration-300 ${
        isFocused ? 'opacity-10' : 'opacity-0'
      }`} />
      <textarea
        rows={rows}
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        className="relative w-full bg-white border border-neutral-200 rounded-2xl px-4 py-3 text-neutral-900 placeholder-neutral-400 text-sm leading-relaxed font-mono resize-none focus:outline-none focus:border-maroon-500 focus:ring-2 focus:ring-maroon-200 transition-all duration-300 shadow-neo-inset"
      />
    </div>
  )
}

export function AnalyzeButton({ onClick, loading, label, icon }) {
  const [isHovering, setIsHovering] = useState(false)
  return (
    <button
      onClick={onClick}
      disabled={loading}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      className="w-full relative group py-4 rounded-2xl font-bold text-base text-white overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 bg-maroon-600 hover:bg-maroon-700 shadow-neo-md hover:shadow-neo-lg active:shadow-neo-sm"
    >
      {loading && (
        <div className="absolute inset-0 bg-gradient-to-r from-maroon-600 via-maroon-500 to-maroon-600 animate-shimmer" />
      )}
      <span className="relative flex items-center justify-center gap-3">
        {loading ? (
          <>
            <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>Processing...</span>
          </>
        ) : (
          <>
            <span className="text-lg">{icon}</span>
            <span>{label}</span>
            {isHovering && <Sparkles size={16} className="animate-pulse" />}
          </>
        )}
      </span>
    </button>
  )
}

export function PageHeader({ icon, title, highlight, subtitle }) {
  return (
    <div className="mb-12 relative">
      <div className="absolute -top-20 left-0 right-0 h-64 bg-gradient-to-b from-maroon-100/50 to-transparent blur-3xl pointer-events-none" />
      <div className="relative space-y-3">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="absolute inset-0 bg-maroon-200 rounded-2xl blur-lg opacity-40" />
            <div className="relative w-12 h-12 rounded-2xl bg-maroon-600 flex items-center justify-center text-2xl shadow-neo-md">
              {icon}
            </div>
          </div>
          <h1 className="font-display text-5xl md:text-6xl font-bold text-neutral-900 tracking-tight">
            {title} <span className="text-maroon-600">{highlight}</span>
          </h1>
        </div>
        <p className="text-neutral-600 text-base leading-relaxed max-w-2xl">{subtitle}</p>
      </div>
    </div>
  )
}

export function Card({ children, accent = 'default' }) {
  const accentStyles = {
    maroon: 'border-maroon-200 bg-maroon-50 shadow-neo-md',
    neutral: 'border-neutral-200 bg-white shadow-neo-sm',
    default: 'border-neutral-200 bg-white shadow-neo-sm',
  }
  return (
    <div className={`group rounded-2xl border p-6 mb-5 transition-all duration-300 hover:shadow-neo-lg ${accentStyles[accent] || accentStyles.default}`}>
      {children}
    </div>
  )
}

export function SectionCard({ icon, title, children, accent }) {
  const accentStyles = {
    maroon: 'border-maroon-200 bg-maroon-50 shadow-neo-md',
    neutral: 'border-neutral-200 bg-neutral-100 shadow-neo-md',
    default: 'border-neutral-200 bg-white shadow-neo-sm',
  }
  return (
    <div className={`group rounded-2xl border p-6 mb-5 transition-all duration-300 hover:shadow-neo-lg ${accentStyles[accent] || accentStyles.default}`}>
      <div className="flex items-start justify-between mb-4 pb-4 border-b border-neutral-200">
        <div className="flex items-center gap-2.5 text-base font-bold text-neutral-900">
          <span className="text-xl">{icon}</span>
          <span>{title}</span>
        </div>
        <Sparkles size={14} className="text-neutral-400 group-hover:text-maroon-600 transition-colors" />
      </div>
      <div className="text-neutral-700 text-sm leading-relaxed font-light">{children}</div>
    </div>
  )
}

export function MetricCard({ label, value, unit = '', icon, trend, color = 'maroon' }) {
  const colors = {
    maroon: 'bg-maroon-50 border-maroon-200 text-maroon-600',
    green: 'bg-green-50 border-green-200 text-green-600',
    red: 'bg-red-50 border-red-200 text-red-600',
    orange: 'bg-orange-50 border-orange-200 text-orange-600',
  }
  return (
    <div className={`rounded-2xl border p-6 transition-all duration-300 hover:shadow-neo-lg shadow-neo-sm ${colors[color]}`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-3xl">{icon}</span>
        {trend && (
          <div className={`flex items-center gap-1 text-xs font-bold ${
            trend > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            <TrendingUp size={14} />
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <p className="text-neutral-600 text-xs font-medium mb-1">{label}</p>
      <p className="text-2xl font-bold text-neutral-900">
        {value} {unit && <span className="text-sm">{unit}</span>}
      </p>
    </div>
  )
}

export function AlertBox({ type = 'info', title, message }) {
  const types = {
    info: 'bg-blue-50 border-blue-200 text-blue-700',
    success: 'bg-green-50 border-green-200 text-green-700',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    error: 'bg-red-50 border-red-200 text-red-700',
  }
  const icons = {
    info: 'ℹ️',
    success: '✓',
    warning: '⚠️',
    error: '✕',
  }
  return (
    <div className={`rounded-xl border p-4 text-sm flex items-start gap-3 shadow-neo-sm ${types[type]}`}>
      <span className="text-xl flex-shrink-0">{icons[type]}</span>
      <div>
        {title && <p className="font-bold mb-1">{title}</p>}
        <p>{message}</p>
      </div>
    </div>
  )
}
