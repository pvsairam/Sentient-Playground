# 🌐 Sentient Playground

**An interactive educational platform showcasing Sentient GRID's multi-agent workflow orchestration**

Experience how the Sentient GRID routes queries through specialized AI agents, visualized in real-time with beautiful WebSocket-powered visualizations.

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.11-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange)

## 🎯 Features

- **🔴 Live Playground**: Submit queries and watch GRID orchestrate multi-agent workflows in real-time
- **🔑 User-Provided API Keys**: Bring your own OpenAI, Anthropic, or Fireworks AI keys
- **🔐 Web3 Wallet Integration**: Connect MetaMask to save settings across devices (no sign-up required!)
- **🤖 Dobby AI Support**: First "Loyal AI" - community-owned, pro-freedom AI model
- **📚 Educational Content**: Learn about GRID, OML, Agents, ROMA, and Model Fingerprinting
- **🔌 Real-time Streaming**: WebSocket-powered event streaming with live workflow visualization
- **🌙 Futuristic UI**: Dark theme with gradient colors and smooth animations
- **⚡ Production-Ready**: FastAPI backend with SQLAlchemy ORM and PostgreSQL database
- **🚀 Decentralized dApp**: No centralized API keys, users control their own data

## 🏗️ Architecture

```
sentient-playground/
├── agent-service/           # Python FastAPI backend (serves everything)
│   ├── main.py             # FastAPI app entry + static file serving
│   ├── agents/             # Educational GRID agents
│   │   └── educational_router.py  # Multi-agent workflow simulation
│   ├── models/             # SQLAlchemy database models
│   │   └── database.py     # Lessons, topics, usage logs schemas
│   ├── static/             # HTML/CSS/JS frontend
│   │   └── index.html      # Interactive playground UI
│   └── requirements.txt    # Python dependencies
├── web/                    # Next.js frontend (for local development)
│   ├── app/                # Next.js 15 App Router
│   ├── components/         # React components  
│   └── prisma/             # Database schema
└── infra/                  # Infrastructure
    ├── init.sql            # Database initialization
    └── docker-compose.yml  # Docker setup

```

### How It Works

1. **User submits query** via frontend HTML form
2. **Backend creates job** and returns `jobId`
3. **WebSocket connection** established to `/ws/stream?jobId={id}`
4. **EducationalRouterAgent** simulates GRID workflow:
   - Routes query to appropriate agent type
   - Classifies query complexity
   - Plans multi-agent workflow
   - Assigns tasks to specialized agents
   - Composes final response
5. **Real-time events** streamed to frontend via WebSocket
6. **Frontend visualizes** workflow events with animations

## 🚀 Quick Start

### For Users

1. **Visit the playground** - No installation required!
2. **Click "⚙️ Settings"** in the navigation
3. **Optional: Connect your wallet** - MetaMask to save settings across devices
4. **Add your API keys**:
   - OpenAI API Key → [Get yours](https://platform.openai.com/api-keys)
   - Anthropic API Key → [Get yours](https://console.anthropic.com/settings/keys)
   - Fireworks AI Key → [Get yours](https://fireworks.ai/) (for Dobby AI)
5. **Save settings** and start asking questions!

Your API keys are stored locally in your browser and sent directly to AI providers - never stored on our servers.

### Local Development

#### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker Compose)
- Node.js 18+ (optional, for Next.js frontend development)

#### Setup

1. **Clone and install dependencies**

```bash
# Install Python dependencies
cd agent-service && pip install -r requirements.txt && cd ..

# Optional: Install Node dependencies for Next.js frontend
npm install
```

2. **Set up environment variables**

```bash
# Create .env in agent-service/
cd agent-service
cat > .env << EOF
DATABASE_URL="postgresql://user:password@localhost:5432/sentient_playground"
SESSION_SECRET="your-secret-key-here"
EOF
```

3. **Start PostgreSQL**

```bash
# Option 1: Docker Compose
docker-compose up -d

# Option 2: Local PostgreSQL
# Make sure PostgreSQL is running on port 5432
```

4. **Run the application**

```bash
cd agent-service
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

5. **Access the application**

- Playground: http://localhost:5000
- API Docs: http://localhost:5000/docs
- Health Check: http://localhost:5000/health

## 📖 API Endpoints

### POST `/api/ask`

Create a new GRID workflow job.

**Request:**
```json
{
  "prompt": "Explain Bitcoin halving in simple terms"
}
```

**Headers (Optional):**
```
X-OpenAI-Key: sk-...
X-Anthropic-Key: sk-ant-...
X-Fireworks-Key: fw_...
X-Dobby-Model: accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new
```

**Response:**
```json
{
  "jobId": "uuid-here",
  "wsUrl": "ws://localhost:5000/ws/stream?jobId=uuid-here"
}
```

If API keys are provided in headers, the system uses real-time LLM mode. Otherwise, it falls back to educational demo mode.

### WebSocket `/ws/stream?jobId={id}`

Real-time workflow event stream.

**Event Types:**
- `ROUTED` - Query routed to agent
- `CLASSIFIED` - Query complexity classified
- `WORKFLOW_PLANNED` - Multi-agent plan created
- `TASK_ASSIGNED` - Task assigned to specialist
- `TASK_UPDATE` - Task progress update
- `TASK_DONE` - Task completed
- `COMPOSE_START` - Composing final answer
- `COMPOSE_DONE` - Composition complete
- `FINAL` - Final answer ready
- `COMPLETE` - Workflow finished

**Example Event:**
```json
{
  "type": "ROUTED",
  "detail": "Query routed to Knowledge Agent (expertise: crypto/blockchain)",
  "ts": "2025-10-26T04:30:00.000Z"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T04:30:00.000Z"
}
```

## 🎨 Frontend

### Static HTML (Production)

The production frontend is a single `index.html` file with vanilla JavaScript and CSS served by FastAPI at the root path.

**Features:**
- Real-time WebSocket connection
- Event visualization with animations
- Example prompts for quick testing
- Futuristic gradient design
- Fully responsive layout

### Next.js Frontend (Local Development)

For local development with hot module replacement, use the Next.js frontend:

```bash
cd web
npm run dev
```

**Note:** The static HTML frontend is used in production for reliability and simplicity.

## 🧩 Database Schema

### Lessons
```sql
CREATE TABLE lessons (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  slug VARCHAR(100) UNIQUE,
  summary TEXT,
  content TEXT,
  level VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Topics
```sql
CREATE TABLE topics (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  description TEXT,
  icon VARCHAR(50)
);
```

### Usage Logs
```sql
CREATE TABLE usage_logs (
  id SERIAL PRIMARY KEY,
  job_id VARCHAR(100),
  prompt TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Development

### Running Tests

```bash
cd agent-service
pytest
```

### Code Quality

```bash
# Format code
black agent-service/

# Lint
flake8 agent-service/

# Type check
mypy agent-service/
```

### Database Migrations

```bash
# Using Alembic
cd agent-service
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 🚢 Deployment

### Backend Deployment (Railway/Render/Fly.io)

```bash
cd agent-service

# Build command
pip install -r requirements.txt

# Start command
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Secret key for sessions

#### Frontend (Optional - Vercel/Netlify)

If using the Next.js frontend:

```bash
cd web
vercel
```

**Environment Variables:**
- `DATABASE_URL`
- `NEXT_PUBLIC_WS_BASE` - WebSocket URL
- `NEXT_PUBLIC_API_BASE` - API URL

## ⚠️ Known Limitations

### Frontend Options

**For local development:**
- Use the Next.js frontend for hot module replacement
- Use `npm run dev` in the `web/` directory

**For production deployment:**
- Use the static HTML frontend in `agent-service/static/`
- Served automatically by FastAPI on port 5000
- Lightweight, fast, and reliable

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push to your branch
7. Open a Pull Request

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details

## 🔗 Resources

- [Sentient GRID Documentation](https://grid.sentient.xyz/)
- [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)
- [GRID Blog Post](https://blog.sentient.xyz/posts/what-is-grid)
- [Sentient Community](https://discord.gg/sentient)

## 💬 Support

- **Discord**: [Join our community](https://discord.gg/sentient)
- **GitHub Issues**: [Report bugs](https://github.com/pvsairam/-Sentient-Playground/issues)
- **Twitter**: [@SentientAGI](https://twitter.com/SentientAGI)

## 🎓 Educational Content

This platform demonstrates:

- **Multi-Agent Routing**: How GRID routes queries to specialized agents
- **Task Decomposition**: Breaking complex queries into subtasks
- **Agent Composition**: Combining results from multiple agents
- **Real-time Orchestration**: Streaming workflow events via WebSocket
- **Production Architecture**: FastAPI + PostgreSQL + WebSocket stack
- **Decentralized Authentication**: Web3 wallet integration without centralized sign-up
- **User-Controlled Data**: Client-side API key storage and management

## 🤖 Supported AI Models

### OpenAI
- GPT-4o (Router & Composer)
- GPT-4o-mini (Fast worker tasks)

### Anthropic
- Claude 3.5 Sonnet (Router & Composer) ⭐ Recommended
- Claude 3.5 Haiku (Fast worker tasks)

### Fireworks AI (Dobby)
- **Dobby Unhinged 70B** - Community-owned, pro-freedom AI
- **Dobby Mini Unhinged 8B** - Faster, smaller variant
- **Dobby Mini Leashed 8B** - More controlled responses

**What is Dobby?**
Dobby is Sentient's first "Loyal AI" - owned by 650K+ NFT holders, not corporations. It's designed to be pro-freedom, pro-crypto, and has an authentic "unhinged" personality that makes conversations feel more human.

## 🚀 Deployment

### Deploy to Railway (Recommended - Full WebSocket Support)

Railway is the best platform for this app because it fully supports **WebSockets + PostgreSQL**.

**Quick Deploy Steps:**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy Sentient Playground"
   git push origin main
   ```

2. **Sign up for Railway**
   - Visit [railway.app](https://railway.app)
   - Login with GitHub

3. **Deploy Your App**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `sentient-playground`
   - Railway auto-detects and deploys!

4. **Add PostgreSQL Database**
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway automatically adds `DATABASE_URL`

5. **Add Environment Variable**
   - Click your service → "Variables" tab
   - Add `SESSION_SECRET` (generate with `openssl rand -hex 32`)

6. **Done!** Your app is live at `your-app.up.railway.app`

### Alternative Platforms

- **Render**: Also supports WebSockets + PostgreSQL
- **⚠️ Vercel NOT recommended**: No WebSocket support (serverless only)

---

Built with ❤️ by the Sentient community

**GitHub**: [sentient-playground](https://github.com/pvsairam/-Sentient-Playground)  
**Live Demo**: Deploy your own in minutes! 🚀
