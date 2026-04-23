import React, { useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, BarChart, Bar,
} from 'recharts'
import { Phone, TrendingUp, DollarSign, Activity } from 'lucide-react'
import KPICard from '../components/KPICard.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import Badge from '../components/Badge.jsx'
import {
  fmtMoney, fmtPct, fmtDate, fmtShortDate, groupCallsByDay,
  outcomeColor, outcomeLabel, sentimentColor, sentimentLabel,
} from '../lib/utils.js'

const CHART_COLORS = {
  booked: '#22C55E',
  no_deal: '#F59E0B',
  carrier_ineligible: '#EF4444',
  positive: '#22C55E',
  neutral: '#3B82F6',
  negative: '#EF4444',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs">
      <div className="text-[#A1A1AA] mb-1">{label}</div>
      {payload.map((p) => (
        <div key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {typeof p.value === 'number' && p.name.includes('%') ? fmtPct(p.value) : p.value}
        </div>
      ))}
    </div>
  )
}

const PieTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs">
      <div className="font-medium text-[#FAFAFA]">{outcomeLabel(name)}</div>
      <div className="text-[#A1A1AA]">{value} calls</div>
    </div>
  )
}

export default function Overview({ data }) {
  const { calls = [], metrics = {} } = data

  const kpis = useMemo(() => ({
    totalCalls: metrics.total_calls ?? calls.length,
    bookingRate: metrics.booking_rate ?? 0,
    totalRevenue: metrics.total_revenue ?? 0,
    avgCompression: metrics.avg_compression_pct ?? 0,
  }), [metrics, calls])

  const dailyData = useMemo(() => groupCallsByDay(calls), [calls])

  const outcomeData = useMemo(() => {
    const outcomes = metrics.outcomes || {}
    return Object.entries(outcomes).map(([key, val]) => ({
      name: key,
      value: val,
      fill: CHART_COLORS[key] || '#6366F1',
    }))
  }, [metrics])

  const sentimentData = useMemo(() => {
    const sc = metrics.sentiment_counts || {}
    return ['positive', 'neutral', 'negative'].map((k) => ({
      name: k,
      value: sc[k] || 0,
      fill: CHART_COLORS[k],
    }))
  }, [metrics])

  const recentCalls = useMemo(
    () => [...calls].sort((a, b) => b.created_at?.localeCompare(a.created_at)).slice(0, 8),
    [calls]
  )

  return (
    <div className="flex flex-col gap-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard
          title="Total Calls"
          value={kpis.totalCalls.toLocaleString()}
          icon={Phone}
          sub="All time"
        />
        <KPICard
          title="Booking Rate"
          value={fmtPct(kpis.bookingRate)}
          icon={TrendingUp}
          sub={`${metrics.bookings ?? 0} booked`}
        />
        <KPICard
          title="Total Revenue"
          value={fmtMoney(kpis.totalRevenue)}
          icon={DollarSign}
          sub="From booked loads"
        />
        <KPICard
          title="Avg Rate Compression"
          value={fmtPct(kpis.avgCompression)}
          icon={Activity}
          sub="Below board rate"
        />
      </div>

      {/* Booking Rate Over Time */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <SectionHeader title="Booking Rate Over Time" subtitle="Daily % of calls that resulted in a booking" />
        {dailyData.length === 0 ? (
          <div className="flex items-center justify-center h-40 text-[#A1A1AA] text-sm">No data available</div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={dailyData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" />
              <XAxis dataKey="label" tick={{ fill: '#A1A1AA', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis
                tick={{ fill: '#A1A1AA', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v.toFixed(0)}%`}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="bookingRate"
                name="Booking Rate %"
                stroke="#6366F1"
                strokeWidth={2}
                dot={{ fill: '#6366F1', r: 3 }}
                activeDot={{ r: 5, fill: '#6366F1' }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Outcome Donut */}
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
          <SectionHeader title="Outcome Distribution" subtitle="Call outcomes breakdown" />
          {outcomeData.length === 0 ? (
            <div className="flex items-center justify-center h-40 text-[#A1A1AA] text-sm">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={outcomeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  nameKey="name"
                >
                  {outcomeData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
                <Legend
                  formatter={(value) => (
                    <span style={{ color: '#A1A1AA', fontSize: 12 }}>{outcomeLabel(value)}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Sentiment Bar */}
        <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
          <SectionHeader title="Sentiment Breakdown" subtitle="Carrier sentiment across all calls" />
          {sentimentData.every((s) => s.value === 0) ? (
            <div className="flex items-center justify-center h-40 text-[#A1A1AA] text-sm">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={sentimentData}
                layout="vertical"
                margin={{ top: 4, right: 16, bottom: 4, left: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#A1A1AA', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fill: '#A1A1AA', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={sentimentLabel}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null
                    return (
                      <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs">
                        <div className="font-medium text-[#FAFAFA]">{sentimentLabel(payload[0].payload.name)}</div>
                        <div className="text-[#A1A1AA]">{payload[0].value} calls</div>
                      </div>
                    )
                  }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {sentimentData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <SectionHeader title="Recent Activity" subtitle="Last 8 calls" />
        {recentCalls.length === 0 ? (
          <div className="flex items-center justify-center h-20 text-[#A1A1AA] text-sm">No calls yet</div>
        ) : (
          <div className="flex flex-col divide-y divide-[#1F1F23]">
            {recentCalls.map((call) => (
              <div key={call.id} className="py-3 flex items-center gap-3">
                <Badge color={outcomeColor(call.outcome)}>
                  {outcomeLabel(call.outcome)}
                </Badge>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-[#FAFAFA] truncate">
                    {call.carrier_name || `MC ${call.carrier_mc}` || 'Unknown Carrier'}
                  </div>
                  {call.load_id && (
                    <div className="text-xs text-[#A1A1AA] truncate">Load #{call.load_id}</div>
                  )}
                </div>
                <div className="text-right shrink-0">
                  {call.agreed_rate ? (
                    <div className="text-sm font-semibold text-[#FAFAFA]">{fmtMoney(call.agreed_rate)}</div>
                  ) : call.initial_offer ? (
                    <div className="text-sm text-[#A1A1AA]">Offered {fmtMoney(call.initial_offer)}</div>
                  ) : null}
                  <div className="text-xs text-[#A1A1AA]">{fmtShortDate(call.created_at)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
