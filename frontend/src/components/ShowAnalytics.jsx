import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function ShowAnalytics() {
  const [summary, setSummary] = useState(null)
  const [byYear, setByYear] = useState([])
  const [byGenre, setByGenre] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [summaryRes, yearRes, genreRes] = await Promise.all([
          fetch(`${API_URL}/analytics/shows/summary`),
          fetch(`${API_URL}/analytics/shows/by-year`),
          fetch(`${API_URL}/analytics/shows/by-genre`)
        ])

        const summaryData = await summaryRes.json()
        const yearData = await yearRes.json()
        const genreData = await genreRes.json()

        setSummary(summaryData)
        setByYear(yearData)
        setByGenre(genreData)
      } catch (error) {
        console.error('Error fetching analytics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>
  }

  return (
    <div className="analytics-container">
      {summary && (
        <div className="analytics-summary">
          <div className="summary-stat">
            <span className="stat-value">{summary.total_shows || 0}</span>
            <span className="stat-label">Total Shows</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{summary.avg_score || '-'}</span>
            <span className="stat-label">Avg Score</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{summary.total_seasons || 0}</span>
            <span className="stat-label">Total Seasons</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{summary.total_episodes || 0}</span>
            <span className="stat-label">Total Episodes</span>
          </div>
          {summary.avg_imdb_rating && (
            <div className="summary-stat">
              <span className="stat-value">{summary.avg_imdb_rating}</span>
              <span className="stat-label">Avg IMDB</span>
            </div>
          )}
        </div>
      )}

      {byYear.length > 0 && (
        <div className="analytics-section">
          <h3>By Decade</h3>
          <div className="analytics-chart">
            {byYear.map(item => (
              <div key={item.decade} className="chart-bar-row">
                <span className="bar-label">{item.decade}</span>
                <div className="bar-container">
                  <div
                    className="bar"
                    style={{ width: `${(item.count / Math.max(...byYear.map(i => i.count))) * 100}%` }}
                  />
                </div>
                <span className="bar-value">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {byGenre.length > 0 && (
        <div className="analytics-section">
          <h3>By Genre</h3>
          <div className="analytics-chart">
            {byGenre.slice(0, 10).map(item => (
              <div key={item.genre} className="chart-bar-row">
                <span className="bar-label">{item.genre}</span>
                <div className="bar-container">
                  <div
                    className="bar"
                    style={{ width: `${(item.count / Math.max(...byGenre.map(i => i.count))) * 100}%` }}
                  />
                </div>
                <span className="bar-value">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ShowAnalytics
