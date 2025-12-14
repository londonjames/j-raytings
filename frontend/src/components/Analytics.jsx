import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function Analytics() {
  const [yearData, setYearData] = useState([])
  const [filmYearData, setFilmYearData] = useState([])
  const [rtData, setRtData] = useState([])
  const [genreData, setGenreData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllAnalytics()
  }, [])

  const fetchAllAnalytics = async () => {
    try {
      const [yearResponse, filmYearResponse, rtResponse, genreResponse] = await Promise.all([
        fetch(`${API_URL}/analytics/by-year`),
        fetch(`${API_URL}/analytics/by-film-year`),
        fetch(`${API_URL}/analytics/by-rt-score`),
        fetch(`${API_URL}/analytics/by-genre`)
      ])

      // Parse responses (try to parse even if status is not 200)
      let yearAnalytics, filmYearAnalytics, rtAnalytics, genreAnalytics
      
      try {
        yearAnalytics = await yearResponse.json()
      } catch (e) {
        console.error('Error parsing year analytics:', e)
        yearAnalytics = []
      }
      
      try {
        filmYearAnalytics = await filmYearResponse.json()
      } catch (e) {
        console.error('Error parsing film year analytics:', e)
        filmYearAnalytics = []
      }
      
      try {
        rtAnalytics = await rtResponse.json()
      } catch (e) {
        console.error('Error parsing RT analytics:', e)
        rtAnalytics = []
      }
      
      try {
        genreAnalytics = await genreResponse.json()
      } catch (e) {
        console.error('Error parsing genre analytics:', e)
        genreAnalytics = []
      }
      
      // Log warnings for non-200 responses but don't throw
      if (!yearResponse.ok) console.warn(`Year analytics returned ${yearResponse.status}`)
      if (!filmYearResponse.ok) console.warn(`Film year analytics returned ${filmYearResponse.status}`)
      if (!rtResponse.ok) console.warn(`RT analytics returned ${rtResponse.status}`)
      if (!genreResponse.ok) console.warn(`Genre analytics returned ${genreResponse.status}`)

      setYearData(Array.isArray(yearAnalytics) ? yearAnalytics : [])
      setFilmYearData(Array.isArray(filmYearAnalytics) ? filmYearAnalytics : [])
      setRtData(Array.isArray(rtAnalytics) ? rtAnalytics : [])
      setGenreData(Array.isArray(genreAnalytics) ? genreAnalytics : [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching analytics:', error)
      setYearData([])
      setFilmYearData([])
      setRtData([])
      setGenreData([])
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>
  }

  return (
    <div className="analytics-container">
      <AnalyticsSection
        title="BY YEAR SEEN"
        data={yearData}
        dataKey="year_watched"
        formatLabel={(val) => val === 'Pre-2006' ? 'Pre-06' : val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange="auto"
      />

      <AnalyticsSection
        title="BY FILM YEAR"
        data={filmYearData}
        dataKey="decade"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange={{ max: 500, step: 100 }}
      />

      <AnalyticsSection
        title="BY ROTTEN TOMATOES"
        data={rtData}
        dataKey="rt_range"
        formatLabel={(val) => val}
        scoreRange={{ min: 8, max: 15, ticks: [8, 9, 10, 11, 12, 13, 14, 15] }}
        countRange={{ max: 500, step: 100 }}
      />

      <AnalyticsSection
        title="BY GENRE"
        data={genreData}
        dataKey="genre"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: 15, ticks: [10, 11, 12, 13, 14, 15] }}
        countRange={{ max: 800, step: 200 }}
      />
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
  // Add extra bottom padding for BY GENRE charts to fit rotated labels
  const bottomPadding = title === 'BY GENRE' ? 80 : 35
  const padding = { top: 25, right: 30, bottom: bottomPadding, left: 55 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Get data ranges
  const counts = data.map(d => d.count || 0)
  const scores = data.map(d => d.avg_score || 0)

  // For "BY YEAR SEEN", exclude Pre-2006 from max calculation since we cap it at 110
  let maxCount
  if (title === 'BY YEAR SEEN') {
    const filteredCounts = counts.filter((_, i) => data[i][dataKey] !== 'Pre-2006')
    maxCount = filteredCounts.length > 0 ? Math.max(...filteredCounts) : 0
  } else {
    maxCount = counts.length > 0 ? Math.max(...counts) : 0
  }

  // Total number of points
  const totalPoints = data.length

  // Calculate max Y for count based on countRange prop
  let maxCountY
  let countStep
  if (countRange === 'auto') {
    maxCountY = maxCount > 0 ? Math.ceil(maxCount / 20) * 20 : 20
    countStep = 20
  } else {
    maxCountY = countRange.max || 20
    countStep = countRange.step || 20
  }

  // Scale functions - evenly space all data points
  // Add a consistent offset to shift points slightly right from axis
  const scaleX = (index) => {
    // Use totalPoints to calculate the full width, then offset by 0.4 units
    const spacing = chartWidth / totalPoints
    return padding.left + (spacing * 0.4) + (index * spacing)
  }

  const scaleYCount = (count) => {
    return padding.top + chartHeight - (count / maxCountY) * chartHeight
  }

  const scaleYScore = (score) => {
    if (score == null || isNaN(score)) return padding.top + chartHeight // Default to bottom if null/NaN
    const minScore = scoreRange.min
    const maxScore = scoreRange.max
    return padding.top + chartHeight - ((score - minScore) / (maxScore - minScore)) * chartHeight
  }

  // Generate path for count line
  const countPath = data.map((d, i) => {
    const x = scaleX(i)
    // Cap Pre-2006 at 110 visually for "BY YEAR SEEN"
    const visualCount = (title === 'BY YEAR SEEN' && d[dataKey] === 'Pre-2006') ? 110 : d.count
    const y = scaleYCount(visualCount)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  // Generate path for score line
  const scorePath = data
    .filter(d => d.avg_score != null && !isNaN(d.avg_score)) // Filter out null/NaN scores
    .map((d, i, filteredData) => {
      const originalIndex = data.indexOf(d)
      const x = scaleX(originalIndex)
      const y = scaleYScore(d.avg_score)
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')

  // Generate Y-axis ticks for count
  const countTicks = []
  for (let i = 0; i <= maxCountY; i += countStep) {
    countTicks.push(i)
  }

  // Use score range ticks from prop
  const scoreTicks = scoreRange.ticks

  return (
    <div className="analytics-section">
      <h2 className="analytics-section-title">{title}</h2>

      {/* Chart 1: Total Films */}
      <div 
        className="chart-section"
        onWheel={(e) => {
          // Enable horizontal scrolling with mouse wheel (when holding Shift or on trackpad)
          if (e.shiftKey || Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
            e.preventDefault()
            e.currentTarget.scrollLeft += e.deltaX || e.deltaY
          }
        }}
      >
        <div className="chart-container">
          <svg width={width} height={height} style={{ minWidth: width }}>
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

            {/* X-axis */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* Y-axis */}
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
              const isGenreChart = title === 'BY GENRE'
              return (
                <text
                  key={`count-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor={isGenreChart ? "end" : "middle"}
                  fill="#999"
                  fontSize="13"
                  transform={isGenreChart ? `rotate(-45, ${x}, ${height - padding.bottom + 20})` : undefined}
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
              Total Films Watched
            </text>

            {/* Count line */}
            <path
              d={countPath}
              fill="none"
              stroke="#4a9eff"
              strokeWidth="3"
            />

            {/* Data points and labels */}
            {data.map((d, i) => {
              const x = scaleX(i)
              // Cap Pre-2006 at 110 visually for "BY YEAR SEEN"
              const visualCount = (title === 'BY YEAR SEEN' && d[dataKey] === 'Pre-2006') ? 110 : d.count
              const y = scaleYCount(visualCount)
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
      <div 
        className="chart-section"
        onWheel={(e) => {
          // Enable horizontal scrolling with mouse wheel (when holding Shift or on trackpad)
          if (e.shiftKey || Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
            e.preventDefault()
            e.currentTarget.scrollLeft += e.deltaX || e.deltaY
          }
        }}
      >
        <div className="chart-container">
          <svg width={width} height={height} style={{ minWidth: width }}>
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

            {/* X-axis */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* Y-axis */}
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
              const isGenreChart = title === 'BY GENRE'
              return (
                <text
                  key={`score-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor={isGenreChart ? "end" : "middle"}
                  fill="#999"
                  fontSize="13"
                  transform={isGenreChart ? `rotate(-45, ${x}, ${height - padding.bottom + 20})` : undefined}
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

            {/* Data points and labels */}
            {data.map((d, i) => {
              if (d.avg_score == null || isNaN(d.avg_score)) return null // Skip null/NaN scores
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

export default Analytics
