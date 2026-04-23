import React, { useMemo } from 'react'
import {
  ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Scatter, BarChart, ScatterChart,
  ReferenceLine, Legend,
} from 'recharts'
import SectionHeader from '../components/SectionHeader.jsx'
import Badge from '../components/Badge.jsx'
import { fmtMoney, fmtPct, fmtNum, sentimentColor, sentimentLabel } from '../lib/utils.js'

const COLORS = {
  green: '#22C55E',
  amber: '#F59E0B',
  blue: '#3B82F6',
  indigo: '#6366F1',
  red: '#EF4444',
}

function DarkTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs shadow-xl">
      {label && <div className="text-[#A1A1AA] mb-1.5 font-medium">{label}</div>}
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || p.fill || '#FAFAFA' }} className="flex items-center gap-2">
          <span>{p.name}:</span>
          <span className="font-semibold">
            {formatter ? formatter(p.value, p.name) : p.value}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function Analytics({ data }) {
  const { calls = [], metrics = {} } = data

  // Call Funnel
  const funnel = useMemo(() => {
    const total = calls.length
    const eligible = calls.filter((c) => c.outcome !== 'carrier_ineligible').length
    const negotiated = calls.filter((c) => (c.num_negotiations || 0) > 0).length
    const booked = calls.filter((c) => c.outcome === 'booked').length
    return [
      { stage: 'Called', count: total, pct: 100 },
      { stage: 'Eligible', count: eligible, pct: total ? (eligible / total) * 100 : 0 },
      { stage: 'Negotiated', count: negotiated, pct: total ? (negotiated / total) * 100 : 0 },
      { stage: 'Booked', count: booked, pct: total ? (booked / total) * 100 : 0 },
    ]
  }, [calls])

  // Lane Performance
  const laneData = useMemo(() => {
    const lp = metrics.lane_performance || {}
    return Object.entries(lp).map(([lane, stats]) => ({
      lane,
      revenue: stats.total_revenue || 0,
      bookings: stats.bookings || 0,
      open: stats.open_loads || 0,
      avgRate: stats.avg_agreed_rate || 0,
      boardRate: stats.avg_loadboard_rate || 0,
    })).sort((a, b) => b.revenue - a.revenue).slice(0, 10)
  }, [metrics])

  // Negotiation rounds distribution
  const roundsDist = useMemo(() => {
    const dist = { 0: 0, 1: 0, 2: 0, 3: 0 }
    calls.forEach((c) => {
      const r = Math.min(c.num_negotiations || 0, 3)
      dist[r]++
    })
    return Object.entries(dist).map(([rounds, count]) => ({
      rounds: `${rounds}${rounds === '3' ? '+' : ''} rounds`,
      count,
    }))
  }, [calls])

  // Rate compression scatter
  const rateScatter = useMemo(() => {
    return calls
      .filter((c) => c.initial_offer && c.agreed_rate && c.outcome === 'booked')
      .map((c) => ({ x: c.initial_offer, y: c.agreed_rate, id: c.id }))
  }, [calls])

  // Carrier performance table
  const carrierPerf = useMemo(() => {
    const cv = metrics.carrier_volume || {}
    return Object.entries(cv)
      .map(([mc, stats]) => ({
        mc,
        name: stats.name || `MC ${mc}`,
        calls: stats.calls || 0,
        bookings: stats.bookings || 0,
        revenue: stats.revenue || 0,
        avgRounds: stats.avg_rounds ?? 0,
        avgSentiment: stats.avg_sentiment || '—',
      }))
      .sort((a, b) => b.revenue - a.revenue)
  }, [metrics])

  const maxRevenue = Math.max(...laneData.map((d) => d.revenue), 1)

  return (
    <div className="flex flex-col gap-6">
      {/* Call Funnel */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <SectionHeader title="Call Funnel" subtitle="Conversion through booking pipeline" />
        <div className="grid grid-cols-4 gap-4">
          {funnel.map((stage, i) => (
            <div key={stage.stage} className="relative">
              <div className="flex flex-col gap-1">
                <div className="text-xs text-[#A1A1AA] font-medium uppercase tracking-wider">{stage.stage}</div>
                <div className="text-2xl font-bold text-[#FAFAFA]">{fmtNum(stage.count)}</div>
                <div className="text-sm font-medium" style={{ color: i === 0 ? '#6366F1' : '#22C55E' }}>
                  {fmtPct(stage.pct)}
                </div>
                <div
                  className="h-1.5 rounded-full mt-1"
                  style={{
                    background: `linear-gradient(90deg, #6366F1 ${stage.pct}%, #1F1F23 ${stage.pct}%)`,
                    width: '100%',
                  }}
                />
              </div>
              {i < funnel.length - 1 && (
                <div className="absolute top-4 -right-2 text-[#A1A1AA] text-lg z-10">→</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Lane Performance */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <SectionHeader
          title="Lane Performance"
          subtitle="Revenue per lane with individual booking rates vs board rates"
        />
        {laneData.length === 0 ? (
          <div className="flex items-center justify-center h-40 text-[#A1A1AA] text-sm">No lane data</div>
        ) : (
          <ResponsiveContainer width="100%" height={Math.max(280, laneData.length * 42)}>
            <ComposedChart
              layout="vertical"
              data={laneData}
              margin={{ top: 4, right: 80, bottom: 4, left: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fill: '#A1A1AA', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              />
              <YAxis
                type="category"
                dataKey="lane"
                width={180}
                tick={{ fill: '#A1A1AA', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(lane, i) => {
                  const d = laneData.find((l) => l.lane === lane)
                  if (!d) return lane
                  return `${lane} (${d.bookings} booked · ${d.open} open)`
                }}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null
                  const d = laneData.find((l) => l.lane === label)
                  return (
                    <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs shadow-xl">
                      <div className="text-[#FAFAFA] font-semibold mb-2">{label}</div>
                      <div className="text-green-400">Revenue: {fmtMoney(d?.revenue)}</div>
                      <div className="text-[#A1A1AA]">Bookings: {d?.bookings} · Open: {d?.open}</div>
                      {d?.avgRate > 0 && <div className="text-amber-400">Avg booked: {fmtMoney(d?.avgRate)}</div>}
                      {d?.boardRate > 0 && <div className="text-blue-400">Avg board: {fmtMoney(d?.boardRate)}</div>}
                    </div>
                  )
                }}
              />
              <Bar dataKey="revenue" name="Revenue" fill={COLORS.green} radius={[0, 4, 4, 0]} barSize={14} />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Bottom row charts */}
      <div className="grid grid-cols-2 gap-4">
        {/* Negotiation Rounds */}
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
          <SectionHeader title="Negotiation Rounds" subtitle="Distribution of rounds per call" />
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={roundsDist} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" />
              <XAxis dataKey="rounds" tick={{ fill: '#A1A1AA', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#A1A1AA', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                content={<DarkTooltip formatter={(v) => v} />}
                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
              />
              <Bar dataKey="count" name="Calls" fill={COLORS.indigo} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Rate Compression Scatter */}
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
          <SectionHeader title="Rate Compression" subtitle="Initial offer vs agreed rate (diagonal = no compression)" />
          {rateScatter.length === 0 ? (
            <div className="flex items-center justify-center h-40 text-[#A1A1AA] text-sm">No booked call data</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <ScatterChart margin={{ top: 4, right: 16, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" />
                <XAxis
                  dataKey="x"
                  name="Initial Offer"
                  tick={{ fill: '#A1A1AA', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`}
                  label={{ value: 'Initial Offer', fill: '#A1A1AA', fontSize: 10, position: 'insideBottom', offset: -8 }}
                />
                <YAxis
                  dataKey="y"
                  name="Agreed Rate"
                  tick={{ fill: '#A1A1AA', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3', stroke: '#1F1F23' }}
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null
                    const d = payload[0].payload
                    return (
                      <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs">
                        <div className="text-[#A1A1AA]">Initial: <span className="text-[#FAFAFA] font-medium">{fmtMoney(d.x)}</span></div>
                        <div className="text-[#A1A1AA]">Agreed: <span className="text-green-400 font-medium">{fmtMoney(d.y)}</span></div>
                        {d.x > 0 && (
                          <div className="text-[#A1A1AA]">
                            Compression: <span className="text-amber-400">{fmtPct(((d.x - d.y) / d.x) * 100)}</span>
                          </div>
                        )}
                      </div>
                    )
                  }}
                />
                <ReferenceLine
                  segment={[
                    { x: Math.min(...rateScatter.map((d) => d.x)), y: Math.min(...rateScatter.map((d) => d.x)) },
                    { x: Math.max(...rateScatter.map((d) => d.x)), y: Math.max(...rateScatter.map((d) => d.x)) },
                  ]}
                  stroke="#1F1F23"
                  strokeDasharray="4 4"
                />
                <Scatter data={rateScatter} fill={COLORS.indigo} opacity={0.8} />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Carrier Performance Table */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <SectionHeader title="Carrier Performance" subtitle="All carriers ranked by revenue" />
        {carrierPerf.length === 0 ? (
          <div className="flex items-center justify-center h-20 text-[#A1A1AA] text-sm">No carrier data</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1F1F23]">
                  {['MC #', 'Carrier', 'Calls', 'Bookings', 'Revenue', 'Avg Rounds', 'Avg Sentiment'].map((h) => (
                    <th key={h} className="text-left py-2.5 px-3 text-xs font-medium text-[#A1A1AA] uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {carrierPerf.map((c, i) => (
                  <tr
                    key={c.mc}
                    className="border-b border-[#1F1F23] hover:bg-[#1F1F23]/50 transition-colors"
                  >
                    <td className="py-3 px-3 text-[#A1A1AA] font-mono text-xs">{c.mc}</td>
                    <td className="py-3 px-3 text-[#FAFAFA] font-medium">{c.name}</td>
                    <td className="py-3 px-3 text-[#FAFAFA]">{c.calls}</td>
                    <td className="py-3 px-3">
                      <span className="text-green-400 font-medium">{c.bookings}</span>
                      <span className="text-[#A1A1AA] text-xs ml-1">
                        ({c.calls > 0 ? fmtPct((c.bookings / c.calls) * 100) : '0%'})
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#FAFAFA] font-semibold">{fmtMoney(c.revenue)}</td>
                    <td className="py-3 px-3 text-[#A1A1AA]">{Number(c.avgRounds).toFixed(1)}</td>
                    <td className="py-3 px-3">
                      <Badge color={sentimentColor(c.avgSentiment)}>
                        {sentimentLabel(c.avgSentiment)}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
