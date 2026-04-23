import React, { useState, useEffect, useCallback } from 'react'
import { RefreshCw, AlertCircle } from 'lucide-react'
import Sidebar from './components/Sidebar.jsx'
import Overview from './pages/Overview.jsx'
import Analytics from './pages/Analytics.jsx'
import Operations from './pages/Operations.jsx'
import RouteMap from './pages/RouteMap.jsx'
import Carriers from './pages/Carriers.jsx'
import { fetchAllData } from './lib/api.js'

const PAGE_TITLES = {
  overview: 'Overview',
  analytics: 'Analytics',
  operations: 'Operations',
  map: 'Network Map',
  carriers: 'Carriers',
}

export default function App() {
  const [activePage, setActivePage] = useState('overview')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)
    setError(null)
    try {
      const result = await fetchAllData()
      setData(result)
      setLastUpdated(new Date().toISOString())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    loadData()
    const interval = setInterval(() => loadData(true), 60000)
    return () => clearInterval(interval)
  }, [loadData])

  const renderPage = () => {
    if (loading) {
      return (
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-4 gap-4">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="skeleton h-28 rounded-xl" />
            ))}
          </div>
          <div className="skeleton h-64 rounded-xl" />
          <div className="grid grid-cols-2 gap-4">
            <div className="skeleton h-48 rounded-xl" />
            <div className="skeleton h-48 rounded-xl" />
          </div>
        </div>
      )
    }
    if (error) {
      return (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <AlertCircle size={40} className="text-red-400" />
          <div className="text-center">
            <div className="text-lg font-semibold text-[#FAFAFA] mb-1">Failed to load data</div>
            <div className="text-sm text-[#A1A1AA] mb-4">{error}</div>
            <button
              onClick={() => loadData()}
              className="px-4 py-2 bg-[#6366F1] text-white rounded-lg text-sm font-medium hover:bg-[#5558E3] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )
    }
    if (!data) return null
    switch (activePage) {
      case 'overview': return <Overview data={data} />
      case 'analytics': return <Analytics data={data} />
      case 'operations': return <Operations data={data} />
      case 'map': return <RouteMap data={data} />
      case 'carriers': return <Carriers data={data} />
      default: return <Overview data={data} />
    }
  }

  return (
    <div className="min-h-screen bg-[#09090B] flex">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        lastUpdated={lastUpdated}
      />
      <div className="flex-1 flex flex-col min-h-screen" style={{ marginLeft: 220 }}>
        {/* Top bar */}
        <header
          className="sticky top-0 z-30 flex items-center justify-between px-6 py-4"
          style={{
            background: 'rgba(9,9,11,0.85)',
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid #1F1F23',
          }}
        >
          <h1 className="text-base font-semibold text-[#FAFAFA]">
            {PAGE_TITLES[activePage] || 'Dashboard'}
          </h1>
          <button
            onClick={() => loadData(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-[#A1A1AA] bg-[#111113] border border-[#1F1F23] hover:text-[#FAFAFA] hover:border-[#2a2a30] transition-all disabled:opacity-50"
          >
            <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </header>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          {renderPage()}
        </main>
      </div>
    </div>
  )
}
