import React from 'react'

const colorMap = {
  green: 'bg-green-500/15 text-green-400 border-green-500/20',
  amber: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
  red: 'bg-red-500/15 text-red-400 border-red-500/20',
  blue: 'bg-blue-500/15 text-blue-400 border-blue-500/20',
  indigo: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/20',
  subtext: 'bg-zinc-800 text-zinc-400 border-zinc-700',
}

export default function Badge({ color = 'blue', children, className = '' }) {
  const cls = colorMap[color] || colorMap.blue
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${cls} ${className}`}
    >
      {children}
    </span>
  )
}
