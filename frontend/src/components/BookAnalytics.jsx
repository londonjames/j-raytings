import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function BookAnalytics() {
  const [yearData, setYearData] = useState([])
  const [typeData, setTypeData] = useState([])
  const [formData, setFormData] = useState([])
  const [authorData, setAuthorData] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllAnalytics()
  }, [])

  const fetchAllAnalytics = async () => {
    try {
      const [yearResponse, typeResponse, formResponse, authorResponse, summaryResponse] = await Promise.all([
        fetch(`${API_URL}/analytics/books/by-year`),
        fetch(`${API_URL}/analytics/books/by-type`),
        fetch(`${API_URL}/analytics/books/by-form`),
        fetch(`${API_URL}/analytics/books/by-author`),
        fetch(`${API_URL}/analytics/books/summary`)
      ])

      const yearAnalytics = await yearResponse.json()
      const typeAnalytics = await typeResponse.json()
      const formAnalytics = await formResponse.json()
      const authorAnalytics = await authorResponse.json()
      const summaryData = await summaryResponse.json()

      setYearData(yearAnalytics)
      setTypeData(typeAnalytics)
      setFormData(formAnalytics)
      setAuthorData(authorAnalytics)
      setSummary(summaryData)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching book analytics:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>
  }

  return (
    <div className="analytics-container">
      {/* Summary Stats */}
      {summary && (
        <div className="analytics-summary">
          <h2>Summary</h2>
          <div className="summary-stats">
            <div className="summary-stat">
              <div className="stat-value">{summary.total_books || 0}</div>
              <div className="stat-label">Total Books</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{summary.avg_score ? summary.avg_score.toFixed(2) : 'N/A'}</div>
              <div className="stat-label">Average Score</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{summary.total_pages ? summary.total_pages.toLocaleString() : 'N/A'}</div>
              <div className="stat-label">Total Pages</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{summary.avg_pages ? summary.avg_pages.toFixed(0) : 'N/A'}</div>
              <div className="stat-label">Avg Pages/Book</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{summary.avg_goodreads_rating ? summary.avg_goodreads_rating.toFixed(2) : 'N/A'}</div>
              <div className="stat-label">Avg Goodreads Rating</div>
            </div>
          </div>
        </div>
      )}

      <AnalyticsSection
        title="BY YEAR READ"
        data={yearData}
        dataKey="year"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange="auto"
      />

      <AnalyticsSection
        title="BY TYPE"
        data={typeData}
        dataKey="type"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange="auto"
      />

      <AnalyticsSection
        title="BY FORM"
        data={formData}
        dataKey="form"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange="auto"
      />

      {/* Top Authors - Simple list */}
      {authorData.length > 0 && (
        <div className="analytics-section">
          <h2 className="analytics-section-title">TOP AUTHORS</h2>
          <div className="author-list">
            {authorData.slice(0, 10).map((author, index) => (
              <div key={author.author} className="author-item">
                <span className="author-rank">{index + 1}.</span>
                <span className="author-name">{author.author}</span>
                <span className="author-count">{author.count} books</span>
                {author.avg_score && (
                  <span className="author-score">Avg: {author.avg_score.toFixed(1)}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function AnalyticsSection({ title, data, dataKey, formatLabel, scoreRange, countRange }) {
  if (data.length === 0) {
    return null
  }

  // Chart dimensions
  const width = 1100
  const height = 220
  const bottomPadding = 35
  const padding = { top: 25, right: 30, bottom: bottomPadding, left: 55 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Get data ranges
  const counts = data.map(d => d.count)
  const scores = data.map(d => d.avg_score)

  const maxCount = Math.max(...counts)
  const totalPoints = data.length

  // Calculate max Y for count
  let maxCountY
  let countStep
  if (countRange === 'auto') {
    maxCountY = Math.ceil(maxCount / 20) * 20
    countStep = 20
  } else {
    maxCountY = countRange.max
    countStep = countRange.step
  }

  // Scale functions
  const scaleX = (index) => {
    const spacing = chartWidth / totalPoints
    return padding.left + (spacing * 0.4) + (index * spacing)
  }

  const scaleYCount = (count) => {
    return padding.top + chartHeight - (count / maxCountY) * chartHeight
  }

  const scaleYScore = (score) => {
    const minScore = scoreRange.min
    const maxScore = scoreRange.max
    return padding.top + chartHeight - ((score - minScore) / (maxScore - minScore)) * chartHeight
  }

  // Generate paths
  const countPath = data.map((d, i) => {
    const x = scaleX(i)
    const y = scaleYCount(d.count)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  const scorePath = data.map((d, i) => {
    const x = scaleX(i)
    const y = scaleYScore(d.avg_score)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  // Generate Y-axis ticks
  const countTicks = []
  for (let i = 0; i <= maxCountY; i += countStep) {
    countTicks.push(i)
  }

  const scoreTicks = scoreRange.ticks

  return (
    <div className="analytics-section">
      <h2 className="analytics-section-title">{title}</h2>

      {/* Chart 1: Total Books */}
      <div className="chart-section">
        <div className="chart-container">
          <svg width={width} height={height}>
            {/* Grid lines */}
            {countTicks.map(tick => (
              <line
                key={`count-grid-${tick}`}
                x1={padding.left}
                y1={scaleYCount(tick)}
                x2={width - padding.right}
                y2={scaleYCount(tick)}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Axes */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />
            <line
              x1={padding.left}
              y1={padding.top}
              x2={padding.left}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* X-axis labels */}
            {data.map((d, i) => {
              const x = scaleX(i)
              return (
                <text
                  key={`count-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor="middle"
                  fill="#999"
                  fontSize="13"
                >
                  {formatLabel(d[dataKey])}
                </text>
              )
            })}

            {/* Y-axis labels */}
            {countTicks.map(tick => (
              <text
                key={`count-y-${tick}`}
                x={padding.left - 10}
                y={scaleYCount(tick)}
                textAnchor="end"
                fill="#999"
                fontSize="12"
                alignmentBaseline="middle"
              >
                {tick}
              </text>
            ))}

            {/* Y-axis title */}
            <text
              x={padding.left - 45}
              y={height / 2}
              textAnchor="middle"
              fill="#999"
              fontSize="13"
              fontWeight="500"
              transform={`rotate(-90, ${padding.left - 45}, ${height / 2})`}
            >
              Total Books Read
            </text>

            {/* Count line */}
            <path
              d={countPath}
              fill="none"
              stroke="#4a9eff"
              strokeWidth="3"
            />

            {/* Data points */}
            {data.map((d, i) => {
              const x = scaleX(i)
              const y = scaleYCount(d.count)
              return (
                <g key={`count-data-${d[dataKey]}`}>
                  <circle cx={x} cy={y} r="4" fill="#4a9eff" />
                  <text
                    x={x}
                    y={y - 10}
                    textAnchor="middle"
                    fill="#4a9eff"
                    fontSize="12"
                    fontWeight="600"
                  >
                    {d.count}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>

      {/* Chart 2: Average Rating */}
      <div className="chart-section">
        <div className="chart-container">
          <svg width={width} height={height}>
            {/* Grid lines */}
            {scoreTicks.map(tick => (
              <line
                key={`score-grid-${tick}`}
                x1={padding.left}
                y1={scaleYScore(tick)}
                x2={width - padding.right}
                y2={scaleYScore(tick)}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Axes */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />
            <line
              x1={padding.left}
              y1={padding.top}
              x2={padding.left}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* X-axis labels */}
            {data.map((d, i) => {
              const x = scaleX(i)
              return (
                <text
                  key={`score-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor="middle"
                  fill="#999"
                  fontSize="13"
                >
                  {formatLabel(d[dataKey])}
                </text>
              )
            })}

            {/* Y-axis labels */}
            {scoreTicks.map(tick => (
              <text
                key={`score-y-${tick}`}
                x={padding.left - 10}
                y={scaleYScore(tick)}
                textAnchor="end"
                fill="#999"
                fontSize="12"
                alignmentBaseline="middle"
              >
                {tick}
              </text>
            ))}

            {/* Y-axis title */}
            <text
              x={padding.left - 45}
              y={height / 2}
              textAnchor="middle"
              fill="#999"
              fontSize="13"
              fontWeight="500"
              transform={`rotate(-90, ${padding.left - 45}, ${height / 2})`}
            >
              Average J-Rayting
            </text>

            {/* Score line */}
            <path
              d={scorePath}
              fill="none"
              stroke="#ff6b6b"
              strokeWidth="3"
            />

            {/* Data points */}
            {data.map((d, i) => {
              const x = scaleX(i)
              const y = scaleYScore(d.avg_score)
              return (
                <g key={`score-data-${d[dataKey]}`}>
                  <circle cx={x} cy={y} r="4" fill="#ff6b6b" />
                  <text
                    x={x}
                    y={y - 10}
                    textAnchor="middle"
                    fill="#ff6b6b"
                    fontSize="12"
                    fontWeight="600"
                  >
                    {d.avg_score.toFixed(1)}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>
    </div>
  )
}

export default BookAnalytics

