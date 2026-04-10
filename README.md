# 🔱 Artha Sutra

_The AI Treasury for Automated Alpha._

Artha Sutra is an autonomous, multi-agent quantitative trading laboratory. Powered by **LangGraph** and **Adaptive RAG**, it researches global financial news, writes its own Python backtesting strategies, validates them against historical data, and executes trades via the **Zerodha Kite** API.

### The Sanskrit Architecture

- **Artha (Wealth/Purpose):** The core intelligence orchestrator finding market opportunities.
- **Sutra (Formula):** The LLM-driven coder that writes backtesting scripts.
- **Kosh (Treasury):** The memory layer using **MongoDB** (logs/state) and **Qdrant** (alpha vector embeddings).
- **Mudra (Seal of Authority):** The **Pydantic** execution gateway ensuring strict risk-management before live trading.

---

## 🏗️ Tech Stack

- **AI & Orchestration:** LangGraph, LangChain, OpenAI (`gpt-4o-mini`)
- **Research & RAG:** Tavily API, Qdrant (Vector DB)
- **Backend:** FastAPI, Python 3.10+, Uvicorn
- **Data & State:** MongoDB (Motor Async), Pydantic V2
- **Frontend:** Streamlit
- **Broker Integration:** Zerodha Kite Connect

---

## 📁 Repository Structure

```text
artha-sutra/
├── .github/workflows/      # CI/CD pipelines
├── backend/                # FastAPI Application & AI Engine
│   ├── app/
│   │   ├── api/            # REST endpoints (/backtest, /approve)
│   │   ├── core/           # App configuration and Pydantic Settings
│   │   ├── db/             # MongoDB and Qdrant client connections
│   │   ├── engine/         # Artha-Engine: LangGraph nodes & state
│   │   ├── execution/      # Mudra-Validator: Backtesting & Broker API
│   │   └── main.py         # FastAPI entry point
│   ├── tests/              # Pytest suite
│   └── requirements.txt
├── frontend/               # Streamlit Dashboard
│   ├── app.py              # Main dashboard view
│   ├── components/         # UI Widgets (Charts, Watchlists)
│   └── requirements.txt
├── docker-compose.yml      # Infrastructure (MongoDB, Qdrant)
├── .env.example            # Environment variables template
└── README.md
```
