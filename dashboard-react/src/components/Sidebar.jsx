import React from 'react'
import { LayoutDashboard, BarChart3, Settings, Map, Users, Truck } from 'lucide-react'
import { fmtDateTime } from '../lib/utils.js'

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'operations', label: 'Operations', icon: Settings },
  { id: 'map', label: 'Network Map', icon: Map },
  { id: 'carriers', label: 'Carriers', icon: Users },
]

export default function Sidebar({ activePage, onNavigate, lastUpdated }) {
  return (
    <aside
      className="fixed top-0 left-0 h-screen flex flex-col"
      style={{
        width: 220,
        background: '#09090B',
        borderRight: '1px solid #1F1F23',
        zIndex: 40,
      }}
    >
      {/* Logo */}
      <div className="px-4 py-5 border-b border-[#1F1F23]">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
            style={{ background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)' }}
          >
            <Truck size={16} color="white" />
          </div>
          <div>
            <div className="text-sm font-bold text-[#FAFAFA] leading-tight">Acme Logistics</div>
            <div className="text-[10px] text-[#A1A1AA] leading-tight">AI Freight Dashboard</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5 overflow-y-auto">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const active = activePage === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left ${
                active
                  ? 'bg-[#6366F1]/15 text-[#6366F1]'
                  : 'text-[#A1A1AA] hover:text-[#FAFAFA] hover:bg-[#1F1F23]'
              }`}
            >
              <Icon size={16} className="shrink-0" />
              {label}
              {active && (
                <div className="ml-auto w-1 h-1 rounded-full bg-[#6366F1]" />
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-[#1F1F23]">
        <div className="flex items-center gap-2 mb-1">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
          </span>
          <span className="text-xs font-medium text-green-400">Live</span>
        </div>
        <div className="text-[10px] text-[#A1A1AA]">
          {lastUpdated ? `Updated ${fmtDateTime(lastUpdated)}` : 'Loading…'}
        </div>
      </div>
    </aside>
  )
}
