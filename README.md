# cloudsec-rag-agent

CloudSec RAG Agent is an authenticated cloud security assistant with a FastAPI
backend and a Streamlit frontend. It can review IAM policies, inspect cloud log
snippets, flag common misconfiguration patterns, answer cloud-security questions
from local RAG documents, and handle general assistant prompts through OpenAI.

## Features

- FastAPI backend with health, auth, and protected agent endpoints.
- Streamlit frontend with signup, login, persisted browser sessions, chat, file
  upload, quick actions, and chat export.
- Email/password authentication with bcrypt password hashes and JWT bearer
  tokens.
- SQLAlchemy user storage. SQLite is used locally by default, and another
  database can be supplied with `DATABASE_URL`.
- RAG over local files in `data/`, with FAISS when available and a fallback
  vector/keyword search path when it is not.
- Dedicated analyzers for IAM policy JSON, cloud log text, and basic
  misconfiguration indicators.
- Prompt-injection cleanup for common instruction-bypass patterns in user text
  and uploaded text files.

## Project Structure

```text
app.py                    Backend entrypoint
app/
  main.py                 FastAPI routes, auth dependencies, request models
  agent.py                Agent routing, OpenAI calls, attachment handling
  auth.py                 Password hashing and JWT helpers
  database.py             SQLAlchemy user model and sessions
  ingest.py               Vectorstore build entrypoint
  retriever.py            RAG retrieval and vectorstore persistence
  security/               IAM, log, and misconfiguration analyzers
frontend/
  streamlit_app.py        Auth-gated chat workspace
  auth_api.py             Frontend API client
  auth_storage.py         Cookie persistence helpers
  pages/login.py          Login page
  pages/signup.py         Signup page
data/                     Source documents and sample security inputs
vectorstore/              Generated vector indexes and document cache
```

## Requirements

- Python 3.11 is recommended for local development and Streamlit Community
  Cloud.
- An OpenAI API key is required for live model responses.
- The app can still return deterministic fallback output for some flows when
  OpenAI is not configured, but production use should set `OPENAI_API_KEY`.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and set at least:

```text
OPENAI_API_KEY=sk-...
SECRET_KEY=replace-with-a-long-random-secret
CLOUDSEC_API_URL=http://127.0.0.1:8000
```

Start the backend:

```bash
python app.py
```

In a second terminal, start the frontend:

```bash
streamlit run frontend/streamlit_app.py
```

Open the Streamlit URL, create an account, log in, and use the chat workspace.

## RAG Data And Ingestion

The retriever reads supported text-like files from `data/` and persists indexes
under `vectorstore/`.

Build or refresh the vectorstore manually:

```bash
python -m app.ingest
```

Supported source formats include `.txt`, `.md`, `.json`, `.yaml`, `.yml`,
`.log`, `.cfg`, `.conf`, `.ini`, `.tf`, `.hcl`, `.py`, `.js`, `.ts`, `.sql`,
`.xml`, and `.csv`.

If FAISS is available, the app writes `vectorstore/faiss.index`. If FAISS or the
local sentence-transformer model is unavailable, the code falls back to local
hash embeddings and keyword search so the app can still run.

## Environment Variables

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Production yes | Empty | API key for OpenAI Responses API calls. |
| `OPENAI_MODEL` | No | `gpt-4.1-mini` | Model used by the backend. |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | Base URL for OpenAI-compatible Responses API. |
| `OPENAI_MAX_OUTPUT_TOKENS` | No | `400` | Maximum model output tokens. |
| `REQUEST_TIMEOUT_SECONDS` | No | `45` | Backend timeout for model calls. |
| `SECRET_KEY` | Production yes | Random per process | JWT signing key. Set this in production. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | JWT lifetime in minutes. |
| `DATABASE_URL` | No | `sqlite:///data/users.db` | SQLAlchemy database URL for user accounts. |
| `CORS_ORIGINS` | Production recommended | `*` | Comma-separated allowed frontend origins. |
| `CLOUDSEC_API_URL` | Frontend yes | Render backend URL in frontend client | Backend URL used by the Streamlit app. |
| `BACKEND_URL` | No | `http://127.0.0.1:8000` | Alternate local backend URL setting. |
| `HOST` | No | `0.0.0.0` | Backend bind host. |
| `PORT` | No | `8000` | Backend bind port. |
| `ENVIRONMENT` | No | `development` | Environment label returned by the root endpoint. |
| `DATA_DIR` | No | `data` | Directory containing RAG source documents. |
| `VECTORSTORE_DIR` | No | `vectorstore` | Directory for generated vector indexes. |
| `MAX_QUERY_CHARS` | No | `4000` | Maximum `/ask` query length. |
| `MAX_ATTACHMENT_CHARS` | No | `12000` | Maximum text content per attachment. |
| `MAX_ATTACHMENT_COUNT` | No | `5` | Maximum attachments per `/ask` request. |

Important: if `SECRET_KEY` is not set, the backend generates a new signing key
when the process starts. That is convenient locally, but it can invalidate user
sessions after restarts and should not be used for production deployments.

## API

Base backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```http
GET /health
```

Signup:

```http
POST /signup
Content-Type: application/json

{
  "email": "you@example.com",
  "password": "at-least-8-characters"
}
```

Login:

```http
POST /login
Content-Type: application/json

{
  "email": "you@example.com",
  "password": "at-least-8-characters"
}
```

Ask the agent:

```http
POST /ask
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "Analyze this IAM policy for least-privilege issues.",
  "attachments": [
    {
      "name": "policy.json",
      "mime_type": "application/json",
      "size_bytes": 1234,
      "kind": "json",
      "text_content": "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  ]
}
```

`/ask` requires either a non-empty `query` or at least one attachment.

## Attachment Behavior

The frontend accepts text, JSON/data, document, image, video, audio, archive,
and other file types. Text-like uploads are decoded and sent to the backend for
analysis. Image, audio, and video uploads are accepted in the UI, but this
version does not inspect their media content directly unless usable text is
included separately.

The backend enforces attachment count, attachment text length, and query length
limits through environment variables.

## Backend Deployment On Render

This repository includes `render.yaml` and a `Procfile` that start the backend
with:

```bash
python app.py
```

For Render, set these environment variables on the backend service:

```text
OPENAI_API_KEY=sk-...
SECRET_KEY=replace-with-a-long-random-secret
OPENAI_MODEL=gpt-4.1-mini
CORS_ORIGINS=https://your-streamlit-app-url.streamlit.app
```

For persistent production user accounts, configure `DATABASE_URL` to point to a
managed database. If you rely on the default SQLite database on an ephemeral
service, user accounts may not survive rebuilds or instance replacement.

After changing environment variables, redeploy or restart the backend service.

The current Render backend URL used by the frontend defaults to:

```text
https://cloudsec-rag-agent.onrender.com
```

Health check:

```text
https://cloudsec-rag-agent.onrender.com/health
```

## Frontend Deployment On Streamlit Community Cloud

Recommended platform: Streamlit Community Cloud.

Use this app entrypoint:

```text
frontend/streamlit_app.py
```

The frontend has its own lightweight dependency file:

```text
frontend/requirements.txt
```

Streamlit Community Cloud checks the entrypoint directory before the repository
root, so this keeps the frontend build from installing backend/RAG packages like
FAISS, sentence-transformers, LangChain, and NumPy.

Set this secret or environment variable in the frontend deployment:

```text
CLOUDSEC_API_URL=https://cloudsec-rag-agent.onrender.com
```

Choose Python 3.11 from Streamlit Community Cloud's deploy/redeploy advanced
settings. Community Cloud does not use `runtime.txt` to select Python.

If you deploy the frontend to Render instead, use this start command:

```bash
streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

## Troubleshooting

- `401 Unauthorized` from `/ask`: log in again and send the returned token as
  `Authorization: Bearer <token>`.
- `Email already registered`: use the existing account or remove/reset the local
  SQLite database during local testing.
- `The OpenAI API is not configured or could not be reached`: set
  `OPENAI_API_KEY`, confirm `OPENAI_BASE_URL`, and restart the backend.
- Frontend cannot reach backend: verify `CLOUDSEC_API_URL` in the Streamlit
  environment and check the backend `/health` endpoint.
- Login sessions disappear after restart: set a stable `SECRET_KEY`.
- New files in `data/` are not reflected in RAG answers: run
  `python -m app.ingest` or restart so the retriever can rebuild/load the index.

## Limitations

- Media files can be uploaded, but image/audio/video content is not directly
  inspected by the backend in this version.
- The built-in IAM, log, and misconfiguration analyzers are heuristic helpers,
  not a replacement for a full cloud security scanner.
- Local SQLite is suitable for development. Use a managed database for durable
  production accounts.
