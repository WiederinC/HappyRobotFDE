import React, { useMemo, useState, useCallback } from 'react'
import { ComposableMap, Geographies, Geography, Marker, Line } from 'react-simple-maps'
import { geoAlbersUsa } from 'd3-geo'
import { fmtMoney, fmtDate } from '../lib/utils.js'

const GEO_URL = 'https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json'

const CITY_COORDS = {
  'Atlanta GA': [33.749, -84.388],
  'Boston MA': [42.360, -71.059],
  'Charlotte NC': [35.227, -80.843],
  'Chicago IL': [41.878, -87.630],
  'Dallas TX': [32.779, -96.800],
  'Denver CO': [39.739, -104.990],
  'Houston TX': [29.760, -95.370],
  'Indianapolis IN': [39.768, -86.158],
  'Kansas City MO': [39.099, -94.579],
  'Las Vegas NV': [36.175, -115.137],
  'Los Angeles CA': [34.052, -118.244],
  'Memphis TN': [35.149, -90.048],
  'Miami FL': [25.775, -80.208],
  'Minneapolis MN': [44.977, -93.265],
  'Nashville TN': [36.162, -86.781],
  'New York NY': [40.713, -74.006],
  'Philadelphia PA': [39.952, -75.165],
  'Phoenix AZ': [33.448, -112.074],
  'Seattle WA': [47.606, -122.332],
}

// Convert [lat, lng] to [lng, lat] for d3/react-simple-maps
function toGeoCoord([lat, lng]) {
  return [lng, lat]
}

function findCityCoord(cityStr) {
  if (!cityStr) return null
  // Try direct match first
  const direct = CITY_COORDS[cityStr]
  if (direct) return toGeoCoord(direct)
  // Try partial match (city name contains one of our keys)
  for (const [key, coords] of Object.entries(CITY_COORDS)) {
    const cityName = key.split(' ').slice(0, -1).join(' ')
    if (cityStr.toLowerCase().includes(cityName.toLowerCase())) {
      return toGeoCoord(coords)
    }
  }
  return null
}

function Tooltip({ info, x, y }) {
  if (!info) return null
  return (
    <div
      className="absolute z-50 pointer-events-none"
      style={{ left: x + 12, top: y - 8, minWidth: 180 }}
    >
      <div className="bg-[#111113] border border-[#1F1F23] rounded-lg p-3 text-xs shadow-2xl">
        <div className="font-semibold text-[#FAFAFA] mb-1">
          {info.origin} → {info.destination}
        </div>
        {info.rate && <div className="text-green-400">Rate: {fmtMoney(info.rate)}</div>}
        {info.equipment && <div className="text-[#A1A1AA]">{info.equipment}</div>}
        {info.pickup && <div className="text-[#A1A1AA]">Pickup: {fmtDate(info.pickup)}</div>}
        {info.status && (
          <div
            className={`mt-1 font-medium ${
              info.status === 'booked'
                ? 'text-green-400'
                : info.status === 'available'
                ? 'text-blue-400'
                : 'text-amber-400'
            }`}
          >
            {info.status}
          </div>
        )}
      </div>
    </div>
  )
}

export default function RouteMap({ data }) {
  const { loads = [], waitlist = {} } = data
  const waitlistEntries = waitlist.entries || []

  const [tooltip, setTooltip] = useState(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  const routes = useMemo(() => {
    return loads.map((load) => {
      const from = findCityCoord(load.origin)
      const to = findCityCoord(load.destination)
      if (!from || !to) return null
      return {
        id: load.load_id,
        from,
        to,
        status: load.status,
        info: {
          origin: load.origin,
          destination: load.destination,
          rate: load.loadboard_rate,
          equipment: load.equipment_type,
          pickup: load.pickup_datetime,
          status: load.status,
        },
      }
    }).filter(Boolean)
  }, [loads])

  // City activity volumes
  const cityActivity = useMemo(() => {
    const counts = {}
    loads.forEach((l) => {
      counts[l.origin] = (counts[l.origin] || 0) + 1
      counts[l.destination] = (counts[l.destination] || 0) + 1
    })
    return counts
  }, [loads])

  // Waiting carrier cities from waitlist
  const waitingCities = useMemo(() => {
    const cities = new Set()
    waitlistEntries.forEach((e) => {
      if (e.origin) cities.add(e.origin)
    })
    return cities
  }, [waitlistEntries])

  const handleMouseMove = useCallback((e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }, [])

  return (
    <div className="flex flex-col gap-4">
      {/* Legend */}
      <div className="flex items-center gap-6 bg-[#111113] border border-[#1F1F23] rounded-xl px-5 py-3">
        <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
          <div className="w-8 h-0.5 bg-green-500" />
          Booked loads
        </div>
        <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
          <div className="w-8 h-0.5 bg-blue-500" />
          Available loads
        </div>
        <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          Waiting carriers
        </div>
        <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
          <div className="w-3 h-3 rounded-full bg-[#6366F1]" />
          Cities (size = activity)
        </div>
        <div className="ml-auto text-xs text-[#A1A1AA]">
          {routes.filter((r) => r.status === 'booked').length} booked ·{' '}
          {routes.filter((r) => r.status !== 'booked').length} available
        </div>
      </div>

      {/* Map */}
      <div
        className="bg-[#111113] border border-[#1F1F23] rounded-xl overflow-hidden relative"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip(null)}
      >
        <ComposableMap
          projection="geoAlbersUsa"
          style={{ width: '100%', height: 520, background: '#111113' }}
        >
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  style={{
                    default: { fill: '#1A1A1F', stroke: '#1F1F23', strokeWidth: 0.5, outline: 'none' },
                    hover: { fill: '#1F1F25', stroke: '#1F1F23', strokeWidth: 0.5, outline: 'none' },
                    pressed: { fill: '#1A1A1F', stroke: '#1F1F23', strokeWidth: 0.5, outline: 'none' },
                  }}
                />
              ))
            }
          </Geographies>

          {/* Routes */}
          {routes.map((route) => (
            <Line
              key={route.id}
              from={route.from}
              to={route.to}
              stroke={route.status === 'booked' ? '#22C55E' : '#3B82F6'}
              strokeWidth={route.status === 'booked' ? 2 : 1.5}
              strokeOpacity={0.7}
              strokeLinecap="round"
              onMouseEnter={() => setTooltip(route.info)}
              onMouseLeave={() => setTooltip(null)}
              style={{ cursor: 'pointer' }}
            />
          ))}

          {/* City markers */}
          {Object.entries(CITY_COORDS).map(([city, [lat, lng]]) => {
            const coord = toGeoCoord([lat, lng])
            const activity = cityActivity[city] || 0
            const isWaiting = waitingCities.has(city)
            const radius = Math.max(3, Math.min(8, 3 + activity * 0.8))

            return (
              <Marker key={city} coordinates={coord}>
                {isWaiting && (
                  <circle
                    r={radius + 4}
                    fill="#F59E0B"
                    fillOpacity={0.2}
                    stroke="#F59E0B"
                    strokeWidth={1}
                    strokeOpacity={0.4}
                  />
                )}
                <circle
                  r={radius}
                  fill={isWaiting ? '#F59E0B' : '#6366F1'}
                  fillOpacity={0.9}
                  stroke={isWaiting ? '#F59E0B' : '#4F46E5'}
                  strokeWidth={1}
                />
                {activity > 2 && (
                  <text
                    textAnchor="middle"
                    y={-radius - 3}
                    style={{
                      fontSize: 9,
                      fill: '#A1A1AA',
                      fontFamily: 'Inter, sans-serif',
                      pointerEvents: 'none',
                    }}
                  >
                    {city.split(' ').slice(0, -1).join(' ')}
                  </text>
                )}
              </Marker>
            )
          })}
        </ComposableMap>

        <Tooltip info={tooltip} x={mousePos.x} y={mousePos.y} />
      </div>

      {/* Route list */}
      <div className="bg-[#111113] border border-[#1F1F23] rounded-xl p-5">
        <div className="text-sm font-semibold text-[#FAFAFA] mb-3">All Routes</div>
        <div className="grid grid-cols-3 gap-2">
          {routes.map((r) => (
            <div
              key={r.id}
              className="flex items-center gap-2 text-xs py-2 px-3 rounded-lg bg-[#1F1F23]"
            >
              <div
                className="w-2 h-2 rounded-full shrink-0"
                style={{ background: r.status === 'booked' ? '#22C55E' : '#3B82F6' }}
              />
              <span className="text-[#FAFAFA] truncate">
                {r.info.origin} → {r.info.destination}
              </span>
              {r.info.rate && (
                <span className="text-[#A1A1AA] shrink-0 ml-auto">{fmtMoney(r.info.rate)}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
