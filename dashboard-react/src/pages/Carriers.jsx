import React, { useState, useMemo, useCallback } from 'react'
import { ChevronDown, ChevronUp, ArrowUpDown } from 'lucide-react'
import SectionHeader from '../components/SectionHeader.jsx'
import Badge from '../components/Badge.jsx'
import { fmtMoney, fmtPct, fmtShortDate, buildCarrierStats, sentimentColor, sentimentLabel, outcomeColor, outcomeLabel } from '../lib/utils.js'

function SortButton({ field, sortField, sortDir, onSort, children }) {
  const active = sortField === field
  return (
    <button
      onClick={() => onSort(field)}
      className={`flex items-center gap-1 text-xs font-medium uppercase tracking-wider transition-colors ${
        active ? 'text-[#6366F1]' : 'text-[#A1A1AA] hover:text-[#FAFAFA]'
      }`}
    >
      {children}
      {active ? (
        sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
      ) : (
        <ArrowUpDown size={11} className="opacity-40" />
      )}
    </button>
  )
}

function CallHistoryRow({ call }) {
  return (
    <div className="flex items-center gap-3 py-2 px-4 border-b border-[#1F1F23] last:border-0 text-xs">
      <div className="w-24 text-[#A1A1AA]">{fmtShortDate(call.created_at)}</div>
      <Badge color={outcomeColor(call.outcome)}>
        {outcomeLabel(call.outcome)}
      </Badge>
      <div className="flex-1 text-[#A1A1AA]">Load #{call.load_id || '—'}</div>
      <div className="w-20 text-right">
        {call.agreed_rate ? (
          <span className="text-green-400 font-medium">{fmtMoney(call.agreed_rate)}</span>
        ) : call.initial_offer ? (
          <span className="text-[#A1A1AA]">{fmtMoney(call.initial_offer)} offered</span>
        ) : (
          <span className="text-[#A1A1AA]">—</span>
        )}
      </div>
      <div className="w-16 text-right text-[#A1A1AA]">
        {call.num_negotiations ?? 0} rds
      </div>
      <div className="w-20 text-right">
        <Badge color={sentimentColor(call.sentiment)}>
          {sentimentLabel(call.sentiment)}
        </Badge>
      </div>
    </div>
  )
}

export default function Carriers({ data }) {
  const { calls = [] } = data
  const [sortField, setSortField] = useState('revenue')
  const [sortDir, setSortDir] = useState('desc')
  const [expanded, setExpanded] = useState(null)
  const [search, setSearch] = useState('')

  const carrierStats = useMemo(() => buildCarrierStats(calls), [calls])

  // KPI bar
  const kpis = useMemo(() => {
    const unique = carrierStats.length
    const avgBookings = unique > 0 ? carrierStats.reduce((s, c) => s + c.bookings, 0) / unique : 0
    const repeat = unique > 0 ? carrierStats.filter((c) => c.bookings > 1).length / unique * 100 : 0
    return { unique, avgBookings, repeat }
  }, [carrierStats])

  const handleSort = useCallback((field) => {
    setSortField((prev) => {
      if (prev === field) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
        return field
      }
      setSortDir('desc')
      return field
    })
  }, [])

  const sorted = useMemo(() => {
    const filtered = carrierStats.filter((c) =>
      !search ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.mc.toLowerCase().includes(search.toLowerCase())
    )
    return [...filtered].sort((a, b) => {
      let av = a[sortField]
      let bv = b[sortField]
      if (typeof av === 'string') av = av.toLowerCase()
      if (typeof bv === 'string') bv = bv.toLowerCase()
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1 : -1
      return 0
    })
  }, [carrierStats, sortField, sortDir, search])

  const toggleExpand = useCallback((mc) => {
    setExpanded((prev) => (prev === mc ? null : mc))
  }, [])

  return (
    <div className="flex flex-col gap-6">
      {/* KPI Bar */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-4">
          <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-1">Unique Carriers</div>
          <div className="text-2xl font-bold text-[#FAFAFA]">{kpis.unique}</div>
        </div>
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-4">
          <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-1">Avg Bookings / Carrier</div>
          <div className="text-2xl font-bold text-[#FAFAFA]">{kpis.avgBookings.toFixed(1)}</div>
        </div>
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-4">
          <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-1">Repeat Rate</div>
          <div className="text-2xl font-bold text-[#FAFAFA]">{fmtPct(kpis.repeat)}</div>
          <div className="text-xs text-[#A1A1AA]">carriers with 2+ bookings</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl overflow-hidden">
        {/* Search bar */}
        <div className="px-5 py-4 border-b border-[#1F1F23] flex items-center gap-3">
          <input
            type="text"
            placeholder="Search by carrier name or MC…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-[#1F1F23] border border-[#2a2a30] rounded-lg px-3 py-2 text-sm text-[#FAFAFA] placeholder-[#A1A1AA] outline-none focus:border-[#6366F1] transition-colors"
          />
          <div className="text-xs text-[#A1A1AA]">{sorted.length} carriers</div>
        </div>

        {sorted.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-[#A1A1AA] text-sm">
            {search ? 'No carriers match your search' : 'No carrier data'}
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1F1F23]">
                <th className="text-left py-3 px-4">
                  <SortButton field="name" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Carrier Name
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="mc" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    MC #
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="calls" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Total Calls
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="bookings" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Bookings
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="revenue" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Revenue
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="avgRounds" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Avg Rounds
                  </SortButton>
                </th>
                <th className="text-left py-3 px-4">
                  <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider">
                    Last Sentiment
                  </span>
                </th>
                <th className="text-left py-3 px-4">
                  <SortButton field="lastCallDate" sortField={sortField} sortDir={sortDir} onSort={handleSort}>
                    Last Call
                  </SortButton>
                </th>
                <th className="py-3 px-4 w-8" />
              </tr>
            </thead>
            <tbody>
              {sorted.map((carrier) => (
                <React.Fragment key={carrier.mc}>
                  <tr
                    onClick={() => toggleExpand(carrier.mc)}
                    className="border-b border-[#1F1F23] hover:bg-[#1F1F23]/50 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4 font-medium text-[#FAFAFA]">{carrier.name}</td>
                    <td className="py-3 px-4 text-[#A1A1AA] font-mono text-xs">{carrier.mc}</td>
                    <td className="py-3 px-4 text-[#FAFAFA]">{carrier.calls}</td>
                    <td className="py-3 px-4">
                      <span className="text-green-400 font-medium">{carrier.bookings}</span>
                      <span className="text-[#A1A1AA] text-xs ml-1">
                        ({fmtPct(carrier.bookingRate)})
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-[#FAFAFA]">
                      {fmtMoney(carrier.revenue)}
                    </td>
                    <td className="py-3 px-4 text-[#A1A1AA]">
                      {carrier.avgRounds.toFixed(1)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge color={sentimentColor(carrier.lastSentiment)}>
                        {sentimentLabel(carrier.lastSentiment)}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-[#A1A1AA] text-xs">
                      {fmtShortDate(carrier.lastCallDate)}
                    </td>
                    <td className="py-3 px-4 text-[#A1A1AA]">
                      {expanded === carrier.mc ? (
                        <ChevronUp size={14} />
                      ) : (
                        <ChevronDown size={14} />
                      )}
                    </td>
                  </tr>

                  {/* Expanded call history */}
                  {expanded === carrier.mc && (
                    <tr className="border-b border-[#1F1F23]">
                      <td colSpan={9} className="p-0">
                        <div className="bg-[#0D0D0F] border-t border-[#1F1F23]">
                          <div className="px-4 py-2 flex items-center gap-2 border-b border-[#1F1F23]">
                            <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider">
                              Call History — {carrier.history.length} call{carrier.history.length !== 1 ? 's' : ''}
                            </span>
                          </div>
                          {carrier.history
                            .slice()
                            .sort((a, b) => b.created_at?.localeCompare(a.created_at))
                            .map((call) => (
                              <CallHistoryRow key={call.id} call={call} />
                            ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
