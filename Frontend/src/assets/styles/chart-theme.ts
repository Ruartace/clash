// ECharts unified color theme for Clash — Dark Gold Edition
// 与 global.css 中的 CSS 变量保持同步：
//   CHART_COLORS.income  ↔  --color-income  (#4caf82)
//   CHART_COLORS.expense ↔  --color-expense (#e05c5c)
//   CHART_COLORS.primary ↔  --color-accent  (#c8ad7e)

export const CHART_COLORS = {
  primary:   '#c8ad7e', // 金色（主强调）
  secondary: '#bfbebf', // 浅灰
  success:   '#4caf82', // 收入绿
  warning:   '#e6a817', // 警告黄
  danger:    '#e05c5c', // 危险红
  income:    '#4caf82', // 收入专用绿（与 --color-income 一致）
  expense:   '#e05c5c', // 支出专用红（与 --color-expense 一致）
  neutral:   '#7a7874', // 弱化灰
  palette: [
    '#c8ad7e', // 金
    '#4caf82', // 绿
    '#e05c5c', // 红
    '#bfbebf', // 灰
    '#e6a817', // 黄
    '#9e8660', // 暗金
    '#2dd4bf', // 青
    '#a78bfa', // 紫
    '#fb923c', // 橙
    '#60a5fa', // 蓝
  ],
}

export const CHART_THEME = {
  backgroundColor: 'transparent',
  textStyle: {
    color: '#bfbebf',
    fontFamily: "'DM Sans', 'Noto Sans SC', sans-serif",
  },
  title: {
    textStyle: { color: '#bfbebf', fontSize: 14, fontWeight: '600' },
  },
  legend: {
    textStyle: { color: '#bfbebf' },
  },
  tooltip: {
    backgroundColor: '#1e1d1b',
    borderColor: '#2e2b27',
    textStyle: { color: '#bfbebf' },
    extraCssText: 'box-shadow: 0 4px 16px rgba(0,0,0,0.55);',
  },
  grid: {
    borderColor: '#2e2b27',
  },
  categoryAxis: {
    axisLine:  { lineStyle: { color: '#2e2b27' } },
    axisTick:  { lineStyle: { color: '#2e2b27' } },
    axisLabel: { color: '#7a7874' },
    splitLine: { lineStyle: { color: '#1e1d1b' } },
  },
  valueAxis: {
    axisLine:  { lineStyle: { color: '#2e2b27' } },
    axisTick:  { lineStyle: { color: '#2e2b27' } },
    axisLabel: { color: '#7a7874' },
    splitLine: { lineStyle: { color: '#2e2b27', type: 'dashed', opacity: 0.5 } },
  },
  color: CHART_COLORS.palette,
}
