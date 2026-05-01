# cloudsec-rag-agent

CloudSec RAG Agent has a FastAPI backend and a Streamlit frontend.

## Backend

The backend is deployed on Render:

```text
https://cloudsec-rag-agent.onrender.com
```

Health check:

```text
https://cloudsec-rag-agent.onrender.com/health
```

## Frontend Deployment

Recommended platform: Streamlit Community Cloud.

Use this app entrypoint:

```text
frontend/streamlit_app.py
```

The frontend has its own lightweight dependency file at:

```text
frontend/requirements.txt
```

Streamlit Community Cloud checks the entrypoint directory before the repository
root, so this keeps the frontend build from installing backend/RAG packages like
FAISS, sentence-transformers, LangChain, and NumPy.

Set this secret/environment variable in the frontend deployment:

```text
CLOUDSEC_API_URL=https://cloudsec-rag-agent.onrender.com
```

Choose Python 3.11 from Streamlit Community Cloud's deploy/redeploy advanced
settings. Community Cloud does not use `runtime.txt` to select Python.

For local frontend testing:

```bash
streamlit run frontend/streamlit_app.py
```

If you deploy the frontend to Render instead, use this start command:

```bash
streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```
