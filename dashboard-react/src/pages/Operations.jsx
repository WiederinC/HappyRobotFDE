import React, { useMemo } from 'react'
import { Clock, AlertTriangle } from 'lucide-react'
import SectionHeader from '../components/SectionHeader.jsx'
import LoadCard from '../components/LoadCard.jsx'
import Badge from '../components/Badge.jsx'
import { fmtMoney, fmtDate, fmtShortDate } from '../lib/utils.js'

export default function Operations({ data }) {
  const { loads = [], calls = [], waitlist = {}, matches = {} } = data

  const waitlistEntries = waitlist.entries || []
  const matchList = matches.matches || []

  // Lane intelligence from historical calls
  const laneIntel = useMemo(() => {
    const intel = {}
    calls.filter((c) => c.outcome === 'booked' && c.agreed_rate).forEach((c) => {
      const load = loads.find((l) => l.load_id === c.load_id)
      if (!load) return
      const lane = `${load.origin}→${load.destination}`
      if (!intel[lane]) intel[lane] = { rates: [], carriers: [] }
      intel[lane].rates.push(c.agreed_rate)
      if (c.carrier_mc && !intel[lane].carriers.includes(c.carrier_mc)) {
        intel[lane].carriers.push(c.carrier_mc)
      }
    })
    return intel
  }, [calls, loads])

  function getLaneIntel(load) {
    const lane = `${load.origin}→${load.destination}`
    const info = laneIntel[lane]
    if (!info || info.rates.length === 0) return { avgLanePrice: null, pastCarriers: [] }
    const avg = info.rates.reduce((a, b) => a + b, 0) / info.rates.length
    return { avgLanePrice: avg, pastCarriers: info.carriers }
  }

  // Available loads (non-booked)
  const availableLoads = useMemo(
    () => loads.filter((l) => l.status === 'available' || l.status === 'pending' || !l.status),
    [loads]
  )

  // Callback opportunities from matches
  const callbackLoads = useMemo(() => {
    return matchList
      .filter((m) => m.waiting_count > 0)
      .map((m) => {
        const load = loads.find((l) => l.load_id === m.load_id)
        return { load, match: m }
      })
      .filter((x) => x.load)
  }, [matchList, loads])

  // Rate holds: waitlist entries with carrier ask rate
  const rateHolds = useMemo(() => {
    return waitlistEntries.filter((e) => e.carrier_ask_rate && e.entry_type === 'rate_hold')
  }, [waitlistEntries])

  // Lane waitlist
  const laneWaitlist = useMemo(() => {
    return waitlistEntries.filter((e) => e.entry_type !== 'rate_hold')
  }, [waitlistEntries])

  return (
    <div className="flex flex-col gap-8">
      {/* Available Loads */}
      <section>
        <SectionHeader
          title="Available Loads"
          subtitle={`${availableLoads.length} load${availableLoads.length !== 1 ? 's' : ''} open for booking`}
        />
        {availableLoads.length === 0 ? (
          <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-8 text-center text-[#A1A1AA] text-sm">
            No available loads
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {availableLoads.map((load) => {
              const { avgLanePrice, pastCarriers } = getLaneIntel(load)
              return (
                <LoadCard
                  key={load.load_id}
                  load={load}
                  avgLanePrice={avgLanePrice}
                  pastCarriers={pastCarriers}
                />
              )
            })}
          </div>
        )}
      </section>

      {/* Callback Opportunities */}
      <section>
        <SectionHeader
          title="Callback Opportunities"
          subtitle={`${callbackLoads.length} load${callbackLoads.length !== 1 ? 's' : ''} with waiting carriers`}
          action={
            callbackLoads.length > 0 && (
              <Badge color="amber">
                {callbackLoads.reduce((sum, x) => sum + (x.match.waiting_count || 0), 0)} total waiting
              </Badge>
            )
          }
        />
        {callbackLoads.length === 0 ? (
          <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-8 text-center text-[#A1A1AA] text-sm">
            No callback opportunities
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {callbackLoads.map(({ load, match }) => {
              const { avgLanePrice, pastCarriers } = getLaneIntel(load)
              return (
                <LoadCard
                  key={load.load_id}
                  load={load}
                  waitingCount={match.waiting_count}
                  waitingCarriers={match.waiting_carriers || []}
                  avgLanePrice={avgLanePrice}
                  pastCarriers={pastCarriers}
                />
              )
            })}
          </div>
        )}
      </section>

      {/* Rate Holds */}
      <section>
        <SectionHeader
          title="Rate Holds"
          subtitle="Carriers holding out for a specific rate"
        />
        {rateHolds.length === 0 ? (
          <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-8 text-center text-[#A1A1AA] text-sm">
            No active rate holds
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {rateHolds.map((entry) => {
              const matchedLoad = loads.find((l) =>
                l.origin === entry.origin && l.destination === entry.destination
              )
              const boardRate = matchedLoad?.loadboard_rate
              const gap = boardRate && entry.carrier_ask_rate ? entry.carrier_ask_rate - boardRate : null

              return (
                <div
                  key={entry.id}
                  className="bg-[#111113] border border-[#1F1F23] rounded-xl p-4 flex flex-col gap-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-sm font-semibold text-[#FAFAFA]">
                        {entry.origin} → {entry.destination}
                      </div>
                      <div className="text-xs text-[#A1A1AA] mt-0.5">
                        MC {entry.carrier_mc} · {entry.carrier_name}
                      </div>
                    </div>
                    <Badge color={gap != null && gap > 0 ? 'red' : 'green'}>
                      {gap != null ? (gap > 0 ? `+${fmtMoney(gap)} ask` : 'Under board') : 'Hold'}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-[#1F1F23] rounded-lg p-2.5">
                      <div className="text-[#A1A1AA] mb-0.5">Carrier Asks</div>
                      <div className="text-amber-400 font-semibold text-sm">{fmtMoney(entry.carrier_ask_rate)}</div>
                    </div>
                    <div className="bg-[#1F1F23] rounded-lg p-2.5">
                      <div className="text-[#A1A1AA] mb-0.5">Board Rate</div>
                      <div className="text-[#FAFAFA] font-semibold text-sm">
                        {boardRate ? fmtMoney(boardRate) : '—'}
                      </div>
                    </div>
                  </div>

                  {entry.availability_window && (
                    <div className="flex items-center gap-1.5 text-xs text-[#A1A1AA]">
                      <Clock size={12} />
                      Available: {entry.availability_window}
                    </div>
                  )}

                  {entry.notes && (
                    <div className="text-xs text-[#A1A1AA] bg-[#1F1F23] rounded-lg p-2">
                      {entry.notes}
                    </div>
                  )}

                  <button className="w-full py-2 rounded-lg text-xs font-medium bg-[#6366F1]/15 text-[#6366F1] border border-[#6366F1]/20 hover:bg-[#6366F1]/25 transition-colors">
                    Resolve Hold
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* Lane Waitlist */}
      <section>
        <SectionHeader
          title="Lane Waitlist"
          subtitle={`${laneWaitlist.length} carrier${laneWaitlist.length !== 1 ? 's' : ''} waiting for lanes`}
        />
        {laneWaitlist.length === 0 ? (
          <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-8 text-center text-[#A1A1AA] text-sm">
            No carriers on waitlist
          </div>
        ) : (
          <div className="bg-[#111113] border border-[#1F1F23] rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1F1F23]">
                  {['Route', 'Equipment', 'Carrier MC', 'Carrier Name', 'Availability', 'Ask Rate', 'Added'].map((h) => (
                    <th key={h} className="text-left py-3 px-4 text-xs font-medium text-[#A1A1AA] uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {laneWaitlist.map((entry) => (
                  <tr key={entry.id} className="border-b border-[#1F1F23] hover:bg-[#1F1F23]/50 transition-colors">
                    <td className="py-3 px-4 font-medium text-[#FAFAFA]">
                      {entry.origin || '—'} → {entry.destination || '—'}
                    </td>
                    <td className="py-3 px-4 text-[#A1A1AA]">{entry.equipment_type || '—'}</td>
                    <td className="py-3 px-4 text-[#A1A1AA] font-mono text-xs">{entry.carrier_mc || '—'}</td>
                    <td className="py-3 px-4 text-[#FAFAFA]">{entry.carrier_name || '—'}</td>
                    <td className="py-3 px-4 text-[#A1A1AA]">
                      {entry.availability_window || '—'}
                    </td>
                    <td className="py-3 px-4">
                      {entry.carrier_ask_rate ? (
                        <span className="text-amber-400 font-medium">{fmtMoney(entry.carrier_ask_rate)}</span>
                      ) : (
                        <span className="text-[#A1A1AA]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-[#A1A1AA] text-xs">{fmtShortDate(entry.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
