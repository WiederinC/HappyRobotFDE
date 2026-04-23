import React from 'react'

export default function KPICard({ title, value, sub, icon: Icon, trend, loading }) {
  if (loading) {
    return (
      <div className="gradient-border p-5 flex flex-col gap-3">
        <div className="skeleton h-4 w-24" />
        <div className="skeleton h-8 w-32" />
        <div className="skeleton h-3 w-20" />
      </div>
    )
  }
  return (
    <div className="gradient-border p-5 flex flex-col gap-1 min-w-0">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider">{title}</span>
        {Icon && (
          <span className="p-1.5 rounded-lg bg-[#1F1F23]">
            <Icon size={14} className="text-[#6366F1]" />
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-[#FAFAFA] truncate">{value}</div>
      {(sub || trend != null) && (
        <div className="flex items-center gap-2 mt-1">
          {sub && <span className="text-xs text-[#A1A1AA]">{sub}</span>}
          {trend != null && (
            <span className={`text-xs font-medium ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
            </span>
          )}
        </div>
      )}
    </div>
  )
}
