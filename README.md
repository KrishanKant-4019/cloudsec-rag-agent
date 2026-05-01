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

Set this secret/environment variable in the frontend deployment:

```text
CLOUDSEC_API_URL=https://cloudsec-rag-agent.onrender.com
```

For local frontend testing:

```bash
streamlit run frontend/streamlit_app.py
```

If you deploy the frontend to Render instead, use this start command:

```bash
streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```
