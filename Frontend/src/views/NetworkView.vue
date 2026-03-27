<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as d3Force from 'd3-force'
import { CHART_COLORS } from '@/assets/styles/chart-theme'

// ── Types ────────────────────────────────────────────────────────────────────
type NodeCategory = 'user' | 'account' | 'asset' | 'liability' | 'goal'

interface NetNode extends d3Force.SimulationNodeDatum {
  id: string
  label: string
  category: NodeCategory
  value: number
  sub?: string
}

interface NetLink extends d3Force.SimulationLinkDatum<NetNode> {
  source: string | NetNode
  target: string | NetNode
  label?: string
  strength?: number
}

// ── Mock data ─────────────────────────────────────────────────────────────────
const RAW_NODES: NetNode[] = [
  { id: 'user',      label: '我',       category: 'user',      value: 100 },
  { id: 'wechat',    label: '微信',     category: 'account',   value: 3200,   sub: '¥3,200' },
  { id: 'alipay',    label: '支付宝',   category: 'account',   value: 8600,   sub: '¥8,600' },
  { id: 'cmb',       label: '招商银行', category: 'account',   value: 42000,  sub: '¥42,000' },
  { id: 'icbc',      label: '工商银行', category: 'account',   value: 15000,  sub: '¥15,000' },
  { id: 'house',     label: '房产',     category: 'asset',     value: 800000, sub: '¥800,000' },
  { id: 'car',       label: '汽车',     category: 'asset',     value: 120000, sub: '¥120,000' },
  { id: 'stock',     label: 'A股账户',  category: 'asset',     value: 55000,  sub: '¥55,000' },
  { id: 'fund',      label: '基金',     category: 'asset',     value: 30000,  sub: '¥30,000' },
  { id: 'gold',      label: '黄金',     category: 'asset',     value: 18000,  sub: '¥18,000' },
  { id: 'mortgage',  label: '房贷',     category: 'liability', value: 500000, sub: '-¥500,000' },
  { id: 'carloan',   label: '车贷',     category: 'liability', value: 60000,  sub: '-¥60,000' },
  { id: 'credit',    label: '信用卡',   category: 'liability', value: 8000,   sub: '-¥8,000' },
  { id: 'retire',    label: '退休目标', category: 'goal',      value: 200000, sub: '40%' },
  { id: 'travel',    label: '旅行基金', category: 'goal',      value: 20000,  sub: '65%' },
  { id: 'emergency', label: '应急储备', category: 'goal',      value: 30000,  sub: '80%' },
]

const RAW_LINKS: NetLink[] = [
  { source: 'user',   target: 'wechat',   label: '日常消费', strength: 0.8 },
  { source: 'user',   target: 'alipay',   label: '支付宝',   strength: 0.8 },
  { source: 'user',   target: 'cmb',      label: '主账户',   strength: 0.9 },
  { source: 'user',   target: 'icbc',     label: '薪资卡',   strength: 0.7 },
  { source: 'cmb',    target: 'stock',    label: '投资',     strength: 0.5 },
  { source: 'cmb',    target: 'fund',     label: '理财',     strength: 0.5 },
  { source: 'cmb',    target: 'house',    label: '房产',     strength: 0.4 },
  { source: 'icbc',   target: 'car',      label: '购车',     strength: 0.4 },
  { source: 'cmb',    target: 'gold',     label: '黄金',     strength: 0.4 },
  { source: 'cmb',    target: 'mortgage', label: '还贷',     strength: 0.6 },
  { source: 'icbc',   target: 'carloan',  label: '还款',     strength: 0.5 },
  { source: 'alipay', target: 'credit',   label: '还款',     strength: 0.5 },
  { source: 'cmb',    target: 'retire',   label: '储蓄',     strength: 0.4 },
  { source: 'alipay', target: 'travel',   label: '储蓄',     strength: 0.4 },
  { source: 'icbc',   target: 'emergency',label: '备用',     strength: 0.4 },
]

// ── Color map per category ───────────────────────────────────────────────────
const CAT_COLOR: Record<NodeCategory, string> = {
  user:      '#c8ad7e',
  account:   '#60a5fa',
  asset:     '#4caf82',
  liability: '#e05c5c',
  goal:      '#a78bfa',
}

const CAT_LABEL: Record<NodeCategory, string> = {
  user:      '本人',
  account:   '账户',
  asset:     '资产',
  liability: '负债',
  goal:      '目标',
}

// ── Canvas state ─────────────────────────────────────────────────────────────
const canvasEl    = ref<HTMLCanvasElement | null>(null)
const containerEl = ref<HTMLDivElement | null>(null)
const tooltip     = ref({ visible: false, x: 0, y: 0, node: null as NetNode | null })
const hoveredId   = ref<string | null>(null)

let simulation: d3Force.Simulation<NetNode, NetLink> | null = null
let animId = 0
let dpr = 1, W = 0, H = 0

const nodes: NetNode[] = RAW_NODES.map(n => ({ ...n }))
const links: NetLink[] = RAW_LINKS.map(l => ({ ...l }))

const nodeRadius = (n: NetNode) => {
  if (n.category === 'user') return 36
  const base = Math.cbrt(n.value / 500)
  return Math.max(22, Math.min(44, base * 12))
}

function draw() {
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  ctx.clearRect(0, 0, W * dpr, H * dpr)
  ctx.save()
  ctx.scale(dpr, dpr)

  // ── Draw links ──
  for (const link of links) {
    const s = link.source as NetNode
    const t = link.target as NetNode
    if (s.x == null || t.x == null) continue

    const isHovered = hoveredId.value === s.id || hoveredId.value === t.id
    const alpha = isHovered ? 0.7 : 0.22

    ctx.beginPath()
    ctx.moveTo(s.x, s.y!)
    ctx.lineTo(t.x, t.y!)
    ctx.strokeStyle = `rgba(200,173,126,${alpha})`
    ctx.lineWidth = isHovered ? 2 : 1
    ctx.shadowColor = isHovered ? '#c8ad7e' : 'transparent'
    ctx.shadowBlur  = isHovered ? 8 : 0
    ctx.stroke()
    ctx.shadowBlur = 0
  }

  // ── Draw nodes ──
  for (const node of nodes) {
    if (node.x == null) continue
    const r     = nodeRadius(node)
    const color = CAT_COLOR[node.category]
    const isHov = hoveredId.value === node.id

    // Glow
    if (isHov || node.category === 'user') {
      const grd = ctx.createRadialGradient(node.x, node.y!, 0, node.x, node.y!, r * 2.2)
      grd.addColorStop(0, color + '44')
      grd.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(node.x, node.y!, r * 2.2, 0, Math.PI * 2)
      ctx.fillStyle = grd
      ctx.fill()
    }

    // Fill
    ctx.beginPath()
    ctx.arc(node.x, node.y!, r, 0, Math.PI * 2)
    ctx.fillStyle = '#1e1d1b'
    ctx.fill()

    // Border
    ctx.beginPath()
    ctx.arc(node.x, node.y!, r, 0, Math.PI * 2)
    ctx.strokeStyle = color
    ctx.lineWidth = isHov ? 2.5 : 1.5
    ctx.shadowColor = color
    ctx.shadowBlur  = isHov ? 18 : 8
    ctx.stroke()
    ctx.shadowBlur = 0

    // Label
    ctx.fillStyle = isHov ? '#fff' : '#bfbebf'
    ctx.font = `${node.category === 'user' ? 600 : 500} 11px 'DM Sans', sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.label, node.x, node.y! - (node.sub ? 5 : 0))

    if (node.sub) {
      ctx.fillStyle = color
      ctx.font = `500 9px 'DM Sans', sans-serif`
      ctx.fillText(node.sub, node.x, node.y! + 7)
    }
  }

  ctx.restore()
  animId = requestAnimationFrame(draw)
}

function initSim() {
  const canvas    = canvasEl.value
  const container = containerEl.value
  if (!canvas || !container) return

  dpr = window.devicePixelRatio || 1
  W   = container.clientWidth
  H   = container.clientHeight
  canvas.width  = W * dpr
  canvas.height = H * dpr
  canvas.style.width  = `${W}px`
  canvas.style.height = `${H}px`

  simulation = d3Force
    .forceSimulation<NetNode>(nodes)
    .force('link',      d3Force.forceLink<NetNode, NetLink>(links).id(d => d.id).distance(130).strength(l => (l as NetLink).strength ?? 0.5))
    .force('charge',    d3Force.forceManyBody<NetNode>().strength(d => d.category === 'user' ? -900 : -400))
    .force('center',    d3Force.forceCenter(W / 2, H / 2))
    .force('collision', d3Force.forceCollide<NetNode>().radius(d => nodeRadius(d) + 18))
    .on('tick', () => {})

  cancelAnimationFrame(animId)
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
    if ((mx - node.x) ** 2 + (my - node.y!) ** 2 < r * r) {
      hoveredId.value   = node.id
      tooltip.value = { visible: true, x: e.clientX, y: e.clientY - 70, node }
      return
    }
  }
  hoveredId.value       = null
  tooltip.value.visible = false
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => { cancelAnimationFrame(animId); initSim() })
  : null

onMounted(() => {
  initSim()
  if (resizeObs && containerEl.value) resizeObs.observe(containerEl.value)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  simulation?.stop()
  resizeObs?.disconnect()
})
</script>

<template>
  <div class="net-page">
    <header class="page-header">
      <h1 class="page-title">资产网络</h1>
      <p class="page-subtitle">Canvas + D3-Force 财务关系力导向网络图</p>
    </header>

    <!-- Legend -->
    <div class="legend">
      <span
        v-for="(color, cat) in CAT_COLOR"
        :key="cat"
        class="legend-item"
      >
        <span class="dot" :style="{ background: color }"></span>
        {{ CAT_LABEL[cat as NodeCategory] }}
      </span>
    </div>

    <!-- Canvas -->
    <div ref="containerEl" class="canvas-wrap">
      <canvas
        ref="canvasEl"
        class="net-canvas"
        @mousemove="handleMouseMove"
        @mouseleave="tooltip.visible = false; hoveredId = null"
      />
      <div class="hint">鼠标悬停节点查看详情</div>
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible && tooltip.node"
        class="net-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <span
          class="tt-cat"
          :style="{ color: CAT_COLOR[tooltip.node.category] }"
        >{{ CAT_LABEL[tooltip.node.category] }}</span>
        <span class="tt-name">{{ tooltip.node.label }}</span>
        <span v-if="tooltip.node.sub" class="tt-val">{{ tooltip.node.sub }}</span>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.net-page { display: flex; flex-direction: column; height: 100%; }

.page-header { margin-bottom: 20px; }
.page-title  { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }

.legend {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.canvas-wrap {
  flex: 1;
  min-height: 480px;
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.net-canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: crosshair;
}

.hint {
  position: absolute;
  bottom: 14px;
  right: 18px;
  font-size: 11px;
  color: var(--color-text-muted);
  pointer-events: none;
}
</style>

<!-- Tooltip global styles -->
<style>
.net-tooltip {
  position: fixed;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 10px 16px;
  background: #1e1d1b;
  border: 1px solid #c8ad7e44;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.65);
  z-index: 9999;
  transform: translateX(-50%);
}
.net-tooltip .tt-cat  { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.net-tooltip .tt-name { font-size: 14px; font-weight: 700; color: #bfbebf; }
.net-tooltip .tt-val  { font-size: 12px; color: #c8ad7e; font-family: 'JetBrains Mono', monospace; }
</style>
