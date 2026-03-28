<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as d3Force from 'd3-force'
import { ElMessage } from 'element-plus'

import { CHART_COLORS } from '@/assets/styles/chart-theme'
import { createFlowRecord, getFlowGraph } from '@/api/statistics'
import { formatCurrency } from '@/utils/format'

interface FlowNode extends d3Force.SimulationNodeDatum {
  id: string
  label: string
  type: 'account' | 'income' | 'expense' | 'asset' | 'liability' | 'goal'
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

const loading = ref(false)
const visible = ref(false)
const year = ref(new Date().getFullYear())
const month = ref(new Date().getMonth() + 1)

const statsTotal = ref({ income: 0, expense: 0, flow: 0 })
const nodes = ref<FlowNode[]>([])
const links = ref<FlowLink[]>([])

const canvasEl = ref<HTMLCanvasElement | null>(null)
const containerEl = ref<HTMLDivElement | null>(null)
const tooltip = ref({ visible: false, x: 0, y: 0, text: '', sub: '' })

const dialogVisible = ref(false)
const submitting = ref(false)
const form = ref({
  source_name: '',
  source_type: 'income' as FlowNode['type'],
  target_name: '',
  target_type: 'account' as FlowNode['type'],
  amount: '',
  flow_date: '',
  description: '',
})

const typeOptions = [
  { label: '收入', value: 'income' },
  { label: '账户', value: 'account' },
  { label: '支出', value: 'expense' },
  { label: '资产', value: 'asset' },
  { label: '负债', value: 'liability' },
  { label: '目标', value: 'goal' },
]

let simulation: d3Force.Simulation<FlowNode, FlowLink> | null = null
let animationId = 0
let dpr = 1
let W = 0
let H = 0

const nodeRadius = (n: FlowNode) => {
  const base = Math.sqrt(Math.max(1, n.value) / 120)
  return Math.max(20, Math.min(52, base))
}

const nodeColor = (type: FlowNode['type']) => {
  if (type === 'income') return CHART_COLORS.income
  if (type === 'expense') return CHART_COLORS.expense
  if (type === 'asset') return '#34d399'
  if (type === 'liability') return '#f87171'
  if (type === 'goal') return '#a78bfa'
  return '#60a5fa'
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
    const s = link.source as FlowNode
    const t = link.target as FlowNode
    if (s.x == null || t.x == null) continue

    const dx = t.x - s.x
    const dy = (t.y || 0) - (s.y || 0)
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const ux = dx / dist
    const uy = dy / dist
    const x1 = s.x + ux * nodeRadius(s)
    const y1 = (s.y || 0) + uy * nodeRadius(s)
    const x2 = (t.x || 0) - ux * nodeRadius(t)
    const y2 = (t.y || 0) - uy * nodeRadius(t)

    const maxAmt = Math.max(1, ...links.value.map((l) => l.amount))
    const lineW = 1 + (link.amount / maxAmt) * 4

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = 'rgba(200,173,126,0.45)'
    ctx.lineWidth = lineW
    ctx.stroke()
  }

  for (const node of nodes.value) {
    if (node.x == null || node.y == null) continue
    const r = nodeRadius(node)
    const color = nodeColor(node.type)

    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
    ctx.fillStyle = '#1e1d1b'
    ctx.fill()
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.stroke()

    ctx.fillStyle = '#bfbebf'
    ctx.font = "500 11px 'DM Sans', sans-serif"
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.label, node.x, node.y - 4)

    ctx.fillStyle = color
    ctx.font = "600 10px 'DM Sans', sans-serif"
    ctx.fillText(`¥${Math.round(node.value).toLocaleString('zh-CN')}`, node.x, node.y + 9)
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

  simulation?.stop()
  simulation = d3Force
    .forceSimulation<FlowNode>(nodes.value)
    .force('link', d3Force.forceLink<FlowNode, FlowLink>(links.value).id((d) => d.id).distance(140).strength(0.45))
    .force('charge', d3Force.forceManyBody().strength(-520))
    .force('center', d3Force.forceCenter(W / 2, H / 2))
    .force('collision', d3Force.forceCollide<FlowNode>().radius((d) => nodeRadius(d) + 14))
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

  for (const node of nodes.value) {
    if (node.x == null || node.y == null) continue
    const r = nodeRadius(node)
    const dx = mx - node.x
    const dy = my - node.y
    if (dx * dx + dy * dy < r * r) {
      tooltip.value = {
        visible: true,
        x: e.clientX,
        y: e.clientY - 56,
        text: node.label,
        sub: formatCurrency(String(node.value)),
      }
      return
    }
  }
  tooltip.value.visible = false
}

async function fetchFlowGraph() {
  loading.value = true
  try {
    const res = await getFlowGraph({ year: year.value, month: month.value })
    const data = res.data.data
    nodes.value = data.nodes.map((n) => ({ ...n }))
    links.value = data.links.map((l) => ({ ...l }))
    statsTotal.value = data.summary
    requestAnimationFrame(() => initSim())
  } finally {
    loading.value = false
  }
}

async function submitRecord() {
  if (!form.value.source_name || !form.value.target_name || !form.value.amount) {
    ElMessage.warning('请填写完整流向信息')
    return
  }
  submitting.value = true
  try {
    await createFlowRecord(form.value)
    ElMessage.success('已写入流向记录')
    dialogVisible.value = false
    await fetchFlowGraph()
  } finally {
    submitting.value = false
  }
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => initSim())
  : null

onMounted(async () => {
  await fetchFlowGraph()
  if (resizeObs && containerEl.value) resizeObs.observe(containerEl.value)
  requestAnimationFrame(() => { visible.value = true })
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  simulation?.stop()
  resizeObs?.disconnect()
})
</script>

<template>
  <div class="flow-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">资金流向<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <el-date-picker v-model="year" type="year" value-format="YYYY" style="width: 120px" @change="fetchFlowGraph" />
        <el-input-number v-model="month" :min="1" :max="12" size="default" @change="fetchFlowGraph" />
        <el-button type="primary" @click="dialogVisible = true">＋ 写入流向</el-button>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">总收入节点</span><span class="summary-value finance-summary-value income">{{ formatCurrency(String(statsTotal.income)) }}</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">总支出节点</span><span class="summary-value finance-summary-value expense">{{ formatCurrency(String(statsTotal.expense)) }}</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item summary-count finance-summary-count"><span class="summary-label finance-summary-label">流转总额</span><span class="summary-value finance-summary-value">{{ formatCurrency(String(statsTotal.flow)) }}</span></div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <div ref="containerEl" class="canvas-wrap" v-loading="loading">
      <canvas ref="canvasEl" class="force-canvas" @mousemove="handleMouseMove" @mouseleave="tooltip.visible = false" />
      <div v-if="nodes.length === 0 && !loading" class="empty">暂无流向数据，请先写入记录</div>
    </div>

    <el-dialog v-model="dialogVisible" title="写入资金流向" width="min(520px, 92vw)" align-center>
      <el-form :model="form" label-width="88px" class="finance-dialog-form">
        <el-form-item label="来源名称"><el-input v-model="form.source_name" placeholder="例：工资" /></el-form-item>
        <el-form-item label="来源类型"><el-select v-model="form.source_type" style="width:100%"><el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" /></el-select></el-form-item>
        <el-form-item label="去向名称"><el-input v-model="form.target_name" placeholder="例：招商银行" /></el-form-item>
        <el-form-item label="去向类型"><el-select v-model="form.target_type" style="width:100%"><el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" /></el-select></el-form-item>
        <el-form-item label="金额"><el-input v-model="form.amount" placeholder="0.00" /></el-form-item>
        <el-form-item label="日期"><el-date-picker v-model="form.flow_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.description" type="textarea" rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <div class="finance-dialog-footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="submitting" @click="submitRecord">确认</el-button></div>
      </template>
    </el-dialog>

    <Teleport to="body">
      <div v-if="tooltip.visible" class="flow-tooltip" :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }">
        <span class="tt-title">{{ tooltip.text }}</span>
        <span class="tt-val">{{ tooltip.sub }}</span>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.finance-summary-value.income { color: var(--color-income); }
.finance-summary-value.expense { color: var(--color-expense); }
.canvas-wrap { min-height: 460px; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; position: relative; }
.force-canvas { width: 100%; height: 100%; display: block; cursor: crosshair; }
.empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
</style>

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
.flow-tooltip .tt-val { font-size: 12px; color: #c8ad7e; font-family: 'JetBrains Mono', monospace; }
</style>
