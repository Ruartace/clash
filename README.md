# Clash - 个人财务管理系统

> 一个面向个人用户的现金流与资产可视化管理平台，帮助你清晰掌握收支动态、合理规划财富。

---

## 项目简介

**Clash** 是一套面向个人用户的综合财务管理系统，聚焦于个人现金流追踪与资产全生命周期管理。支持收入/支出记录、账户余额管理、资产配置分析以及财务目标规划，通过直观的可视化仪表盘让你随时了解自己的财务健康状况。

---

## 功能特性

- **现金流记录**：快速录入收入与支出，支持自定义分类标签，自动汇总每日 / 月度 / 年度流水。
- **账户管理**：支持多账户（储蓄卡、信用卡、支付宝、微信钱包等），实时同步各账户余额。
- **资产登记与追踪**：记录固定资产（房产、车辆、设备等）与金融资产（股票、基金、存款），追踪资产净值变化。
- **负债管理**：记录贷款、信用卡欠款等负债信息，自动计算净资产（资产 - 负债）。
- **预算规划**：按分类设置月度预算上限，超支时触发提醒，帮助养成健康消费习惯。
- **财务目标**：设定储蓄目标并追踪进度，直观展示距目标的差距与预计完成时间。
- **可视化仪表盘**：以图表形式呈现收支趋势、资产分布、净资产曲线、预算执行率等核心指标。
- **数据导入 / 导出**：支持 CSV / Excel 格式批量导入账单，支持导出财务报告。

---

## 技术栈

### 后端（Backend）

| 技术 | 说明 |
|------|------|
| Python | 主要开发语言 |
| Django | 后端核心框架 |
| Django REST Framework | RESTful API 构建 |
| Django ORM | 数据访问层 |
| PostgreSQL | 关系型数据库 |
| Redis | 缓存 / 会话管理 |
| djangorestframework-simplejwt | JWT 身份认证与授权 |
| pip / pipenv | 依赖管理 |

### 前端（Frontend）

| 技术 | 说明 |
|------|------|
| Vue 3 | 前端框架 |
| TypeScript | 类型安全 |
| Vite | 构建工具 |
| Element Plus | UI 组件库 |
| ECharts | 数据可视化图表 |
| Axios | HTTP 请求 |
| Pinia | 状态管理 |

---

## 项目结构

```
clash/
├── Backend/                  # 后端 Django 项目
│   ├── apps/
│   │   ├── users/            # 用户与认证 App
│   │   ├── accounts/         # 账户管理 App
│   │   ├── transactions/     # 收支流水 App
│   │   ├── assets/           # 资产管理 App
│   │   ├── liabilities/      # 负债管理 App
│   │   ├── budgets/          # 预算规划 App
│   │   ├── goals/            # 财务目标 App
│   │   └── statistics/       # 统计报表 App
│   ├── clash/                # 项目配置目录
│   │   ├── settings.py       # 项目配置
│   │   ├── urls.py           # 根路由
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt      # Python 依赖
│   └── .env.example          # 环境变量示例
├── Frontend/                 # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/              # 接口请求封装
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # 公共组件
│   │   ├── router/           # 路由配置
│   │   ├── store/            # 状态管理（Pinia）
│   │   ├── views/            # 页面视图
│   │   └── main.ts
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7.0+

### 后端启动

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-org/clash.git
   cd clash/Backend
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   复制示例配置文件并按需修改：
   ```bash
   cp .env.example .env
   ```
   `.env` 关键配置项：
   ```ini
   DEBUG=True
   SECRET_KEY=your_secret_key
   DB_NAME=clash
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   REDIS_URL=redis://127.0.0.1:6379/0
   ```

5. **创建数据库**
   ```sql
   -- 在 psql 中执行
   CREATE DATABASE clash;
   ```

6. **数据库迁移**
   ```bash
   python manage.py migrate
   ```

7. **创建超级管理员**
   ```bash
   python manage.py createsuperuser
   ```

8. **启动服务**
   ```bash
   python manage.py runserver
   ```
   服务默认运行在 `http://localhost:8000`

### 前端启动

```bash
cd clash/Frontend
npm install
npm run dev
```
前端默认运行在 `http://localhost:5173`

---

## 核心模块说明

| 模块 | 路径 | 说明 |
|------|------|------|
| 用户认证 | `/api/auth/` | 注册、登录、登出、Token 刷新 |
| 账户管理 | `/api/accounts/` | 多账户 CRUD、余额同步 |
| 收支流水 | `/api/transactions/` | 收入/支出记录、分类筛选 |
| 资产管理 | `/api/assets/` | 固定资产与金融资产管理 |
| 负债管理 | `/api/liabilities/` | 贷款与信用卡负债记录 |
| 预算规划 | `/api/budgets/` | 月度预算设置与执行追踪 |
| 财务目标 | `/api/goals/` | 储蓄目标设定与进度追踪 |
| 统计报表 | `/api/statistics/` | 净资产、收支趋势等可视化数据 |

---

## 开发规范

- 后端代码遵循 **PEP 8** Python 编码规范
- Git 提交信息遵循 **Conventional Commits** 规范（`feat:` / `fix:` / `docs:` / `refactor:` 等）
- 接口设计遵循 **RESTful** 风格，基于 Django REST Framework
- 统一响应格式：`{ code, message, data }`

---

## 贡献指南

1. Fork 本仓库
2. 新建功能分支：`git checkout -b feat/your-feature`
3. 提交变更：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feat/your-feature`
5. 发起 Pull Request

---

## License

[MIT](LICENSE) © 2026 Clash Team
