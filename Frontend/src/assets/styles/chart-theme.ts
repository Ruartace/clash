// ECharts unified color theme for Clash
export const CHART_COLORS = {
  primary: '#38bdf8',
  secondary: '#818cf8',
  success: '#34d399',
  warning: '#fbbf24',
  danger: '#f87171',
  income: '#34d399',
  expense: '#f87171',
  neutral: '#94a3b8',
  palette: [
    '#38bdf8',
    '#818cf8',
    '#34d399',
    '#fbbf24',
    '#f87171',
    '#a78bfa',
    '#fb7185',
    '#2dd4bf',
    '#facc15',
    '#60a5fa',
  ],
}

export const CHART_THEME = {
  backgroundColor: 'transparent',
  textStyle: {
    color: '#94a3b8',
    fontFamily: "'DM Sans', 'Noto Sans SC', sans-serif",
  },
  title: {
    textStyle: { color: '#f1f5f9', fontSize: 14 },
  },
  legend: {
    textStyle: { color: '#94a3b8' },
  },
  tooltip: {
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#f1f5f9' },
  },
  grid: {
    borderColor: '#334155',
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#334155' } },
    axisTick: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#1e293b' } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: '#334155' } },
    axisTick: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
  },
  color: CHART_COLORS.palette,
}
