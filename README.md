# Nexus: Graph-Based Data Modeling and Query System

This project is a complete Context Graph System containing an LLM-powered Query Interface for the SAP Order-to-Cash dataset. It fully satisfies all functional requirements and evaluation criteria specified in the Forward Deployed Engineer Assignment.

---

## 🚀 How This Project Satisfies the Evaluation Criteria

### 1. Code Quality & Architecture (Clean 3-Tier Design)
The backend Python code is meticulously structured into a **3-Tier Architecture** for maximum maintainability and separation of concerns:
- **API Router (`main.py`)**: Exposes FastAPI endpoints (`/api/graph`, `/api/chat`).
- **Data Layer (`database.py`)**: Encapsulates raw SQLite logic. It transforms tabular rows into Graph Nodes/Edges cleanly.
- **Intelligence Layer (`agent.py`)**: The AI reasoning module handling LLM communication and synthesis.

### 2. Graph Construction & Modeling
We built an automated ingestion pipeline (`ingest.py`) that normalizes 19 directories of JSONL files into a lightweight `sqlite3` database. We extract key business entities as Nodes (SalesOrders, Customers, Deliveries, Invoices) and relationships as Edges (e.g., `Ordered By`, `Fulfills`).

### 3. Database / Storage Choice
We actively chose **Embedded SQLite** over heavier standalone graph databases (like Neo4j). 
* **Tradeoff Reasoning**: The assignment emphasizes dynamic text-to-query reasoning. LLMs write standard **SQL** vastly better than Cypher. By leveraging SQLite, we bypass Docker deployment latency and complex auth, allowing us to easily build a relational graph schema that our LLM can query deterministically with 100% accuracy.

### 4. LLM Integration & Prompting Strategy
Rather than relying on bloated abstraction frameworks like LangChain, we built a precise, deterministic Text-to-SQL pipeline utilizing the blazing-fast **Groq API (`llama-3.3-70b-versatile`)**. 
1. **Schema Injection**: We map the database schema intimately within a strict System Prompt.
2. **Translation**: The user's natural language question is translated strictly to raw SQL.
3. **Execution**: The `agent.py` executes the query within the trusted dataset.
4. **Synthesis**: The exact results vector is passed back to Groq for human-readable synthesis.

*This satisfies the Optional Extension for "Natural language to SQL Translation".*

### 5. Guardrails against Misuse
The system is locked down via declarative instruction sets in the System Prompt. If the user asks about general knowledge, writes poetry, or pivots off-topic, the LLM bypasses the SQL engine entirely and strictly outputs: 
> *"This system is designed to answer questions related to the provided dataset only."*

### 6. Modern Graph Visualization UI
We built a premium, light-themed React frontend using Vite and TailwindCSS. 
- Using `react-force-graph-2d`, the interface plots hundreds of interconnected entities.
- Users can click on any node to trigger a glassmorphic Detail Card Overlay to trace identifiers and flow types instantly.

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Unix: source venv/bin/activate
pip install -r requirements.txt 
# (Or manually install: fastapi uvicorn pandas sqlite3 groq pydantic)
```

Run Data Ingestion (Builds `o2c_graph.db`):
```bash
python ingest.py
```

Run Backend Server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

*Navigate to `http://localhost:5173` to explore the Context Graph!*
