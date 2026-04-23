const BASE_URL = '/api'
const API_KEY = 'hr-dev-key-change-in-prod'

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json',
}

async function fetchJSON(path) {
  const res = await fetch(`${BASE_URL}${path}`, { headers })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`)
  }
  return res.json()
}

export async function getCalls() {
  return fetchJSON('/calls/')
}

export async function getLoads() {
  return fetchJSON('/loads/')
}

export async function getWaitlist() {
  return fetchJSON('/waitlist/')
}

export async function getMatches() {
  return fetchJSON('/matches/')
}

export async function getMetrics() {
  return fetchJSON('/metrics/')
}

export async function fetchAllData() {
  const [calls, loads, waitlist, matches, metrics] = await Promise.all([
    getCalls(),
    getLoads(),
    getWaitlist(),
    getMatches(),
    getMetrics(),
  ])
  return { calls, loads, waitlist, matches, metrics }
}
