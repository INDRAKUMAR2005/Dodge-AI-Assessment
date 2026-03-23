# How to Explain This Project Structure

To easily explain this project to anyone (like an interviewer, peer, or client), you can describe it as following a **Clean 3-Tier Architecture**.

Here is how you can explain the flow:

### The Backend (Python / FastAPI)
The folder `backend/` handles data extraction and AI reasoning. It is divided into three highly specific files so responsibilities never overlap:

1. **`main.py` (The API Router)**
   - **What it does**: Exposes clear Web URLs (`/api/graph`, `/api/chat`) for the frontend to communicate with.
   - **How to explain it**: *"This is our traffic cop. It doesn't do heavy lifting; it just passes the React frontend's requests to the correct internal engine."*

2. **`database.py` (The Data Layer)**
   - **What it does**: Directly connects to `o2c_graph.db`. It transforms raw tables into Graph Nodes and Links.
   - **How to explain it**: *"This layer encapsulates all SQLite logic so our API and AI never have to write direct raw SQL loops. It translates tabular Orders and Customers into Graph networks."*

3. **`agent.py` (The Intelligence Layer)**
   - **What it does**: Utilizes the ultra-fast Groq API (Llama 3.3). 
   - **How to explain it**: *"This is the brain. It takes natural language from the user, injects our database schema, and outputs SQL. It then runs that SQL through the Data Layer, grabs the results, and synthesizes a human-readable summary."*

### The Frontend (React / Vite / Tailwind)
The folder `frontend/` handles visual representation.

1. **`App.jsx`**: The main layout. It splits the screen into a 70% Graph view and a 30% Chat side-panel.
2. **`components/GraphView.jsx`**: Uses `react-force-graph-2d` to render dynamic physics-based nodes.
3. **`components/ChatInterface.jsx`**: Handles the UI states of users chatting with the Agent, mirroring premium AI aesthetics.

### The Flow (Example: "Which products have the most billing documents?")
If anyone asks how a query traverses the system, say this:
1. User types in `ChatInterface.jsx`.
2. Frontend POSTs data to `main.py` at `/api/chat`.
3. `main.py` hands the string to `agent.py`.
4. `agent.py` asks Groq to build SQL for that string.
5. `agent.py` runs the SQL via `database.py`.
6. Results flow back to `agent.py`, where Groq summarizes it locally.
7. Summary flows up to `main.py`, out to the Frontend, and renders cleanly in the Chat Panel.
