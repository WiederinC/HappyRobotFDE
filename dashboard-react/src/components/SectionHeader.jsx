import React from 'react'

export default function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <h2 className="text-base font-semibold text-[#FAFAFA]">{title}</h2>
        {subtitle && <p className="text-sm text-[#A1A1AA] mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
