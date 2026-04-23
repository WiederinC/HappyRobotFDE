import React from 'react'
import { MapPin, Truck, Calendar, DollarSign, Package } from 'lucide-react'
import Badge from './Badge.jsx'
import { fmtMoney, fmtDate, fmtRPM } from '../lib/utils.js'

function statusColor(status) {
  switch (status) {
    case 'available': return 'green'
    case 'booked': return 'blue'
    case 'pending': return 'amber'
    case 'cancelled': return 'red'
    default: return 'subtext'
  }
}

export default function LoadCard({ load, waitingCount, waitingCarriers, avgLanePrice, pastCarriers, extra }) {
  return (
    <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-4 flex flex-col gap-3 hover:border-[#2a2a30] transition-colors">
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <MapPin size={14} className="text-[#6366F1] shrink-0 mt-0.5" />
          <span className="text-sm font-semibold text-[#FAFAFA] truncate">
            {load.origin} → {load.destination}
          </span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {waitingCount > 0 && (
            <Badge color="amber">🔥 {waitingCount} waiting</Badge>
          )}
          <Badge color={statusColor(load.status)}>
            {load.status || 'unknown'}
          </Badge>
        </div>
      </div>

      {/* Details grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-[#A1A1AA]">
          <Truck size={12} className="shrink-0" />
          <span>{load.equipment_type || '—'}</span>
        </div>
        <div className="flex items-center gap-1.5 text-[#A1A1AA]">
          <Calendar size={12} className="shrink-0" />
          <span>{fmtDate(load.pickup_datetime)}</span>
        </div>
        <div className="flex items-center gap-1.5 text-[#A1A1AA]">
          <DollarSign size={12} className="shrink-0" />
          <span className="font-medium text-[#FAFAFA]">{fmtMoney(load.loadboard_rate)}</span>
          {load.miles && (
            <span className="text-[#A1A1AA]">· {fmtRPM(load.loadboard_rate, load.miles)}</span>
          )}
        </div>
        {load.miles && (
          <div className="flex items-center gap-1.5 text-[#A1A1AA]">
            <span>{Number(load.miles).toLocaleString()} mi</span>
          </div>
        )}
        {load.commodity_type && (
          <div className="flex items-center gap-1.5 text-[#A1A1AA] col-span-2">
            <Package size={12} className="shrink-0" />
            <span>{load.commodity_type}{load.weight ? ` · ${Number(load.weight).toLocaleString()} lbs` : ''}</span>
          </div>
        )}
      </div>

      {/* Lane intelligence */}
      {(avgLanePrice != null || (pastCarriers && pastCarriers.length > 0)) && (
        <div className="border-t border-[#1F1F23] pt-2 flex flex-col gap-1">
          {avgLanePrice != null && (
            <div className="text-xs text-[#A1A1AA]">
              Avg lane price: <span className="text-[#FAFAFA] font-medium">{fmtMoney(avgLanePrice)}</span>
            </div>
          )}
          {pastCarriers && pastCarriers.length > 0 && (
            <div className="text-xs text-[#A1A1AA]">
              Past carriers:{' '}
              <span className="text-[#FAFAFA]">
                {pastCarriers.slice(0, 5).join(', ')}
                {pastCarriers.length > 5 ? ` +${pastCarriers.length - 5} more` : ''}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Waiting carriers */}
      {waitingCarriers && waitingCarriers.length > 0 && (
        <div className="border-t border-[#1F1F23] pt-2 flex flex-col gap-1.5">
          {waitingCarriers.slice(0, 3).map((wc) => (
            <div key={wc.entry_id} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5">
                <span className="text-[#A1A1AA]">MC {wc.carrier_mc}</span>
                <span className="text-[#FAFAFA] font-medium">{wc.carrier_name}</span>
              </div>
              <div className="flex items-center gap-1.5">
                {wc.carrier_ask_rate && (
                  <span className={`font-medium ${wc.rate_match ? 'text-green-400' : 'text-amber-400'}`}>
                    {fmtMoney(wc.carrier_ask_rate)}
                  </span>
                )}
              </div>
            </div>
          ))}
          {waitingCarriers.length > 3 && (
            <div className="text-xs text-[#A1A1AA]">+{waitingCarriers.length - 3} more carriers waiting</div>
          )}
        </div>
      )}

      {extra}
    </div>
  )
}
