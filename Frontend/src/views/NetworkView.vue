<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as d3Force from 'd3-force'

import { getAssetNetwork } from '@/api/statistics'
import type { NetworkCategory } from '@/types'

const loading = ref(false)
const visible = ref(false)

type NodeCategory = NetworkCategory

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

const CAT_COLOR: Record<NodeCategory, string> = {
  user: '#c8ad7e',
  account: '#60a5fa',
  asset: '#4caf82',
  liability: '#e05c5c',
  goal: '#a78bfa',
}

const CAT_LABEL: Record<NodeCategory, string> = {
  user: '本人',
  account: '账户',
  asset: '资产',
  liability: '负债',
  goal: '目标',
}

const canvasEl = ref<HTMLCanvasElement | null>(null)
const containerEl = ref<HTMLDivElement | null>(null)
const tooltip = ref({ visible: false, x: 0, y: 0, node: null as NetNode | null })
const hoveredId = ref<string | null>(null)

const nodes = ref<NetNode[]>([])
const links = ref<NetLink[]>([])

let simulation: d3Force.Simulation<NetNode, NetLink> | null = null
let animId = 0
let dpr = 1
let W = 0
let H = 0

const nodeRadius = (n: NetNode) => {
  if (n.category === 'user') return 34
  const base = Math.cbrt(Math.max(1, n.value) / 500)
  return Math.max(20, Math.min(42, base * 11))
}

function draw() {
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, W * dpr, H * dpr)
  ctx.save()
  ctx.scale(dpr, dpr)

  for (const link of links.value) {
    const s = link.source as NetNode
    const t = link.target as NetNode
    if (s.x == null || t.x == null || s.y == null || t.y == null) continue

    const isHovered = hoveredId.value === s.id || hoveredId.value === t.id
    ctx.beginPath()
    ctx.moveTo(s.x, s.y)
    ctx.lineTo(t.x, t.y)
    ctx.strokeStyle = `rgba(200,173,126,${isHovered ? 0.7 : 0.22})`
    ctx.lineWidth = isHovered ? 2 : 1
    ctx.stroke()
  }

  for (const node of nodes.value) {
    if (node.x == null || node.y == null) continue
    const r = nodeRadius(node)
    const color = CAT_COLOR[node.category]
    const isHov = hoveredId.value === node.id

    if (isHov || node.category === 'user') {
      const grd = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, r * 2.2)
      grd.addColorStop(0, `${color}44`)
      grd.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(node.x, node.y, r * 2.2, 0, Math.PI * 2)
      ctx.fillStyle = grd
      ctx.fill()
    }

    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
    ctx.fillStyle = '#1e1d1b'
    ctx.fill()

    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
    ctx.strokeStyle = color
    ctx.lineWidth = isHov ? 2.5 : 1.5
    ctx.stroke()

    ctx.fillStyle = isHov ? '#fff' : '#bfbebf'
    ctx.font = `${node.category === 'user' ? 600 : 500} 11px 'DM Sans', sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.label, node.x, node.y - (node.sub ? 5 : 0))

    if (node.sub) {
      ctx.fillStyle = color
      ctx.font = "500 9px 'DM Sans', sans-serif"
      ctx.fillText(node.sub, node.x, node.y + 7)
    }
  }

  ctx.restore()
  animId = requestAnimationFrame(draw)
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

  simulation?.stop()
  simulation = d3Force
    .forceSimulation<NetNode>(nodes.value)
    .force('link', d3Force.forceLink<NetNode, NetLink>(links.value).id((d) => d.id).distance(120).strength((l) => (l as NetLink).strength ?? 0.5))
    .force('charge', d3Force.forceManyBody<NetNode>().strength((d) => (d.category === 'user' ? -900 : -400)))
    .force('center', d3Force.forceCenter(W / 2, H / 2))
    .force('collision', d3Force.forceCollide<NetNode>().radius((d) => nodeRadius(d) + 16))
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

  for (const node of nodes.value) {
    if (node.x == null || node.y == null) continue
    const r = nodeRadius(node)
    if ((mx - node.x) ** 2 + (my - node.y) ** 2 < r * r) {
      hoveredId.value = node.id
      tooltip.value = { visible: true, x: e.clientX, y: e.clientY - 70, node }
      return
    }
  }
  hoveredId.value = null
  tooltip.value.visible = false
}

async function fetchNetwork() {
  loading.value = true
  try {
    const res = await getAssetNetwork()
    nodes.value = res.data.data.nodes.map((n) => ({ ...n }))
    links.value = res.data.data.links.map((l) => ({ ...l }))
    requestAnimationFrame(() => initSim())
  } finally {
    loading.value = false
  }
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => initSim())
  : null

onMounted(async () => {
  await fetchNetwork()
  if (resizeObs && containerEl.value) resizeObs.observe(containerEl.value)
  requestAnimationFrame(() => { visible.value = true })
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  simulation?.stop()
  resizeObs?.disconnect()
})

const legendEntries = computed(() => Object.entries(CAT_COLOR) as [NodeCategory, string][])
</script>

<template>
  <div class="net-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">资产网络<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <el-button @click="fetchNetwork">刷新网络</el-button>
      </div>
    </header>

    <div class="legend">
      <span v-for="entry in legendEntries" :key="entry[0]" class="legend-item">
        <span class="dot" :style="{ background: entry[1] }"></span>
        {{ CAT_LABEL[entry[0]] }}
      </span>
    </div>

    <div ref="containerEl" class="canvas-wrap" v-loading="loading">
      <canvas ref="canvasEl" class="net-canvas" @mousemove="handleMouseMove" @mouseleave="tooltip.visible = false; hoveredId = null" />
      <div v-if="nodes.length === 0 && !loading" class="empty">暂无网络数据</div>
      <div class="hint">鼠标悬停节点查看详情</div>
    </div>

    <Teleport to="body">
      <div v-if="tooltip.visible && tooltip.node" class="net-tooltip" :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }">
        <span class="tt-cat" :style="{ color: CAT_COLOR[tooltip.node.category] }">{{ CAT_LABEL[tooltip.node.category] }}</span>
        <span class="tt-name">{{ tooltip.node.label }}</span>
        <span v-if="tooltip.node.sub" class="tt-val">{{ tooltip.node.sub }}</span>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.legend { display: flex; gap: 18px; flex-wrap: wrap; margin-bottom: 14px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--color-text-muted); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.canvas-wrap { min-height: 500px; position: relative; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.net-canvas { display: block; width: 100%; height: 100%; cursor: crosshair; }
.hint { position: absolute; bottom: 14px; right: 18px; font-size: 11px; color: var(--color-text-muted); pointer-events: none; }
.empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
</style>

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
.net-tooltip .tt-cat { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.net-tooltip .tt-name { font-size: 14px; font-weight: 700; color: #bfbebf; }
.net-tooltip .tt-val { font-size: 12px; color: #c8ad7e; font-family: 'JetBrains Mono', monospace; }
</style>
