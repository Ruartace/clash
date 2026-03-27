<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as d3Force from 'd3-force'
import { CHART_COLORS } from '@/assets/styles/chart-theme'

// ── Types ────────────────────────────────────────────────────────────────────
interface FlowNode extends d3Force.SimulationNodeDatum {
  id: string
  label: string
  type: 'account' | 'income' | 'expense'
  value: number
  x?: number
  y?: number
}

interface FlowLink extends d3Force.SimulationLinkDatum<FlowNode> {
  source: string | FlowNode
  target: string | FlowNode
  amount: number
  label: string
}

// ── Mock data (replace with real API when ready) ─────────────────────────────
const RAW_NODES: FlowNode[] = [
  { id: 'salary',    label: '工资收入',   type: 'income',  value: 18000 },
  { id: 'freelance', label: '自由职业',   type: 'income',  value: 4500  },
  { id: 'invest',    label: '投资收益',   type: 'income',  value: 2200  },
  { id: 'checking',  label: '活期账户',   type: 'account', value: 12000 },
  { id: 'savings',   label: '储蓄账户',   type: 'account', value: 30000 },
  { id: 'rent',      label: '房租',       type: 'expense', value: 4200  },
  { id: 'food',      label: '餐饮',       type: 'expense', value: 2100  },
  { id: 'transport', label: '交通',       type: 'expense', value: 800   },
  { id: 'shopping',  label: '购物',       type: 'expense', value: 1500  },
  { id: 'utility',   label: '水电',       type: 'expense', value: 600   },
  { id: 'health',    label: '医疗',       type: 'expense', value: 900   },
]

const RAW_LINKS: FlowLink[] = [
  { source: 'salary',    target: 'checking',  amount: 18000, label: '¥18,000' },
  { source: 'freelance', target: 'checking',  amount: 4500,  label: '¥4,500'  },
  { source: 'invest',    target: 'savings',   amount: 2200,  label: '¥2,200'  },
  { source: 'checking',  target: 'savings',   amount: 5000,  label: '¥5,000'  },
  { source: 'checking',  target: 'rent',      amount: 4200,  label: '¥4,200'  },
  { source: 'checking',  target: 'food',      amount: 2100,  label: '¥2,100'  },
  { source: 'checking',  target: 'transport', amount: 800,   label: '¥800'    },
  { source: 'checking',  target: 'shopping',  amount: 1500,  label: '¥1,500'  },
  { source: 'savings',   target: 'utility',   amount: 600,   label: '¥600'    },
  { source: 'savings',   target: 'health',    amount: 900,   label: '¥900'    },
]

// ── Canvas / Sim state ───────────────────────────────────────────────────────
const canvasEl = ref<HTMLCanvasElement | null>(null)
const containerEl = ref<HTMLDivElement | null>(null)
const tooltip = ref({ visible: false, x: 0, y: 0, text: '', sub: '' })
const statsTotal = ref({ income: 0, expense: 0, flow: 0 })

let simulation: d3Force.Simulation<FlowNode, FlowLink> | null = null
let animationId = 0
let dpr = 1
let W = 0, H = 0

const nodes: FlowNode[] = RAW_NODES.map(n => ({ ...n }))
const links: FlowLink[] = RAW_LINKS.map(l => ({ ...l }))

// compute stats
statsTotal.value.income  = nodes.filter(n => n.type === 'income').reduce((s, n) => s + n.value, 0)
statsTotal.value.expense = nodes.filter(n => n.type === 'expense').reduce((s, n) => s + n.value, 0)
statsTotal.value.flow    = links.reduce((s, l) => s + l.amount, 0)

const nodeRadius = (n: FlowNode) => {
  const base = Math.sqrt(n.value / 100)
  return Math.max(28, Math.min(54, base))
}

const nodeColor = (type: FlowNode['type']) => {
  if (type === 'income')  return CHART_COLORS.income
  if (type === 'expense') return CHART_COLORS.expense
  return CHART_COLORS.primary
}

function draw() {
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  ctx.clearRect(0, 0, W * dpr, H * dpr)
  ctx.save()
  ctx.scale(dpr, dpr)

  // Draw links
  for (const link of links) {
    const s = link.source as FlowNode
    const t = link.target as FlowNode
    if (s.x == null || t.x == null) continue

    const dx = t.x - s.x
    const dy = t.y! - s.y!
    const dist = Math.sqrt(dx * dx + dy * dy)
    const ux = dx / dist, uy = dy / dist
    const sr = nodeRadius(s), tr = nodeRadius(t)

    const x1 = s.x + ux * sr, y1 = s.y! + uy * sr
    const x2 = t.x! - ux * tr, y2 = t.y! - uy * tr

    // glow line
    const maxAmt = Math.max(...links.map(l => l.amount))
    const lineW = 1 + (link.amount / maxAmt) * 4
    const alpha = 0.25 + (link.amount / maxAmt) * 0.55

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = `rgba(200,173,126,${alpha})`
    ctx.lineWidth = lineW
    ctx.shadowColor = '#c8ad7e'
    ctx.shadowBlur = 6
    ctx.stroke()
    ctx.shadowBlur = 0

    // arrowhead
    const angle = Math.atan2(y2 - y1, x2 - x1)
    const aw = 8
    ctx.beginPath()
    ctx.moveTo(x2, y2)
    ctx.lineTo(x2 - aw * Math.cos(angle - 0.4), y2 - aw * Math.sin(angle - 0.4))
    ctx.lineTo(x2 - aw * Math.cos(angle + 0.4), y2 - aw * Math.sin(angle + 0.4))
    ctx.closePath()
    ctx.fillStyle = `rgba(200,173,126,${alpha + 0.2})`
    ctx.fill()
  }

  // Draw nodes
  for (const node of nodes) {
    if (node.x == null) continue
    const r = nodeRadius(node)
    const color = nodeColor(node.type)

    // Outer glow ring
    const grad = ctx.createRadialGradient(node.x, node.y!, r * 0.3, node.x, node.y!, r * 1.6)
    grad.addColorStop(0, color + '33')
    grad.addColorStop(1, 'transparent')
    ctx.beginPath()
    ctx.arc(node.x, node.y!, r * 1.6, 0, Math.PI * 2)
    ctx.fillStyle = grad
    ctx.fill()

    // Node circle
    ctx.beginPath()
    ctx.arc(node.x, node.y!, r, 0, Math.PI * 2)
    ctx.fillStyle = '#1e1d1b'
    ctx.fill()
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.shadowColor = color
    ctx.shadowBlur = 14
    ctx.stroke()
    ctx.shadowBlur = 0

    // Label
    ctx.fillStyle = '#bfbebf'
    ctx.font = `500 11px 'DM Sans', sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.label, node.x, node.y! - 5)

    // Amount
    ctx.fillStyle = color
    ctx.font = `600 10px 'DM Sans', sans-serif`
    ctx.fillText(`¥${(node.value / 1000).toFixed(1)}k`, node.x, node.y! + 8)
  }

  ctx.restore()
  animationId = requestAnimationFrame(draw)
}

function initSim() {
  const canvas = canvasEl.value
  const container = containerEl.value
  if (!canvas || !container) return

  dpr = window.devicePixelRatio || 1
  W = container.clientWidth
  H = container.clientHeight
  canvas.width = W * dpr
  canvas.height = H * dpr
  canvas.style.width = `${W}px`
  canvas.style.height = `${H}px`

  simulation = d3Force
    .forceSimulation<FlowNode>(nodes)
    .force('link', d3Force.forceLink<FlowNode, FlowLink>(links).id(d => d.id).distance(160).strength(0.4))
    .force('charge', d3Force.forceManyBody().strength(-600))
    .force('center', d3Force.forceCenter(W / 2, H / 2))
    .force('collision', d3Force.forceCollide<FlowNode>().radius(d => nodeRadius(d) + 20))
    .on('tick', () => {})

  cancelAnimationFrame(animationId)
  draw()
}

function handleMouseMove(e: MouseEvent) {
  const canvas = canvasEl.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const mx = e.clientX - rect.left
  const my = e.clientY - rect.top

  for (const node of nodes) {
    if (node.x == null) continue
    const r = nodeRadius(node)
    const dx = mx - node.x, dy = my - node.y!
    if (dx * dx + dy * dy < r * r) {
      tooltip.value = {
        visible: true,
        x: e.clientX,
        y: e.clientY - 60,
        text: node.label,
        sub: `¥${node.value.toLocaleString('zh-CN')}`,
      }
      return
    }
  }
  tooltip.value.visible = false
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => { cancelAnimationFrame(animationId); initSim() })
  : null

onMounted(() => {
  initSim()
  if (resizeObs && containerEl.value) resizeObs.observe(containerEl.value)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  simulation?.stop()
  resizeObs?.disconnect()
})

const fmt = (v: number) => `¥${v.toLocaleString('zh-CN')}`
</script>

<template>
  <div class="flow-page">
    <header class="page-header">
      <h1 class="page-title">资金流向</h1>
      <p class="page-subtitle">基于 D3-Force 的实时资金流向力导向图</p>
    </header>

    <!-- Stats bar -->
    <div class="stat-bar">
      <div class="stat-chip income">
        <span class="chip-dot"></span>
        <span class="chip-label">总收入</span>
        <span class="chip-val">{{ fmt(statsTotal.income) }}</span>
      </div>
      <div class="stat-chip expense">
        <span class="chip-dot"></span>
        <span class="chip-label">总支出</span>
        <span class="chip-val">{{ fmt(statsTotal.expense) }}</span>
      </div>
      <div class="stat-chip flow">
        <span class="chip-dot"></span>
        <span class="chip-label">流转总额</span>
        <span class="chip-val">{{ fmt(statsTotal.flow) }}</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend">
      <span class="legend-item">
        <span class="dot income"></span>收入来源
      </span>
      <span class="legend-item">
        <span class="dot account"></span>账户
      </span>
      <span class="legend-item">
        <span class="dot expense"></span>支出类别
      </span>
      <span class="legend-item arrow">── 箭头粗细代表资金量</span>
    </div>

    <!-- Canvas container -->
    <div ref="containerEl" class="canvas-wrap">
      <canvas
        ref="canvasEl"
        class="force-canvas"
        @mousemove="handleMouseMove"
        @mouseleave="tooltip.visible = false"
      />
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible"
        class="flow-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <span class="tt-title">{{ tooltip.text }}</span>
        <span class="tt-val">{{ tooltip.sub }}</span>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.flow-page { display: flex; flex-direction: column; height: 100%; }

.page-header { margin-bottom: 20px; }
.page-title  { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }

.stat-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 13px;
}
.stat-chip .chip-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.stat-chip.income  .chip-dot { background: var(--color-income); }
.stat-chip.expense .chip-dot { background: var(--color-expense); }
.stat-chip.flow    .chip-dot { background: var(--color-accent); }
.chip-label { color: var(--color-text-muted); }
.chip-val   { font-family: var(--font-mono); font-weight: 600; color: var(--color-text-primary); }

.legend {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.legend-item.arrow { color: var(--color-text-muted); font-style: italic; }
.dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.dot.income  { background: var(--color-income); }
.dot.account { background: var(--color-accent); }
.dot.expense { background: var(--color-expense); }

.canvas-wrap {
  flex: 1;
  min-height: 440px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
}

.force-canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: crosshair;
}
</style>

<!-- Tooltip is teleported to body — global styles -->
<style>
.flow-tooltip {
  position: fixed;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 14px;
  background: #1e1d1b;
  border: 1px solid #c8ad7e55;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.6);
  z-index: 9999;
  transform: translateX(-50%);
}
.flow-tooltip .tt-title { font-size: 13px; color: #bfbebf; font-weight: 600; }
.flow-tooltip .tt-val   { font-size: 12px; color: #c8ad7e; font-family: 'JetBrains Mono', monospace; }
</style>
