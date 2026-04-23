import { format, parseISO, isValid } from 'date-fns'

export function fmtMoney(val, decimals = 0) {
  if (val == null || isNaN(val)) return '$—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(val)
}

export function fmtPct(val, decimals = 1) {
  if (val == null || isNaN(val)) return '—%'
  return `${Number(val).toFixed(decimals)}%`
}

export function fmtNum(val) {
  if (val == null || isNaN(val)) return '—'
  return new Intl.NumberFormat('en-US').format(val)
}

export function fmtDate(dateStr, fmt = 'MMM d') {
  if (!dateStr) return '—'
  try {
    const d = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
    if (!isValid(d)) return '—'
    return format(d, fmt)
  } catch {
    return '—'
  }
}

export function fmtDateTime(dateStr) {
  return fmtDate(dateStr, 'MMM d, yyyy')
}

export function fmtShortDate(dateStr) {
  return fmtDate(dateStr, 'MMM d')
}

export function calcRPM(rate, miles) {
  if (!rate || !miles || miles === 0) return null
  return rate / miles
}

export function fmtRPM(rate, miles) {
  const rpm = calcRPM(rate, miles)
  if (rpm == null) return '—'
  return `$${rpm.toFixed(2)}/mi`
}

export function outcomeColor(outcome) {
  switch (outcome) {
    case 'booked': return 'green'
    case 'no_deal': return 'amber'
    case 'carrier_ineligible': return 'red'
    default: return 'blue'
  }
}

export function outcomeLabel(outcome) {
  switch (outcome) {
    case 'booked': return 'Booked'
    case 'no_deal': return 'No Deal'
    case 'carrier_ineligible': return 'Ineligible'
    default: return outcome || 'Unknown'
  }
}

export function sentimentColor(sentiment) {
  switch (sentiment) {
    case 'positive': return 'green'
    case 'neutral': return 'blue'
    case 'negative': return 'red'
    default: return 'subtext'
  }
}

export function sentimentLabel(sentiment) {
  if (!sentiment) return 'Unknown'
  return sentiment.charAt(0).toUpperCase() + sentiment.slice(1)
}

export function groupCallsByDay(calls) {
  const map = {}
  calls.forEach((c) => {
    const day = fmtDate(c.created_at, 'yyyy-MM-dd')
    if (!map[day]) map[day] = { date: day, total: 0, booked: 0 }
    map[day].total++
    if (c.outcome === 'booked') map[day].booked++
  })
  return Object.values(map)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((d) => ({
      ...d,
      label: fmtDate(d.date + 'T00:00:00', 'MMM d'),
      bookingRate: d.total > 0 ? (d.booked / d.total) * 100 : 0,
    }))
}

export function buildCarrierStats(calls) {
  const map = {}
  calls.forEach((c) => {
    const key = c.carrier_mc || c.carrier_name || 'Unknown'
    if (!map[key]) {
      map[key] = {
        mc: c.carrier_mc || '—',
        name: c.carrier_name || 'Unknown Carrier',
        calls: 0,
        bookings: 0,
        revenue: 0,
        totalRounds: 0,
        lastSentiment: null,
        lastCallDate: null,
        history: [],
      }
    }
    const s = map[key]
    s.calls++
    if (c.outcome === 'booked') {
      s.bookings++
      s.revenue += c.agreed_rate || 0
    }
    s.totalRounds += c.num_negotiations || 0
    s.lastSentiment = c.sentiment
    if (!s.lastCallDate || c.created_at > s.lastCallDate) {
      s.lastCallDate = c.created_at
    }
    s.history.push(c)
  })
  return Object.values(map).map((s) => ({
    ...s,
    avgRounds: s.calls > 0 ? s.totalRounds / s.calls : 0,
    bookingRate: s.calls > 0 ? (s.bookings / s.calls) * 100 : 0,
  }))
}
