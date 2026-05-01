# ⚡ LLM Code Deployment Pipeline

> **A fully automated FastAPI service** that takes a plain-text task description, generates a complete web application using Gemini, deploys it live to GitHub Pages, and notifies an evaluation server — all in a single API call.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/LLM-Gemini_API-4285F4?style=flat&logo=google&logoColor=white)](https://aistudio.google.com)
[![GitHub Pages](https://img.shields.io/badge/Hosting-GitHub_Pages-181717?style=flat&logo=github&logoColor=white)](https://pages.github.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## 📌 Overview

This project automates the entire lifecycle of **LLM-powered web app creation and deployment** — from a raw task specification to a publicly hosted, live application — without any manual steps in between.

The system was built to handle multi-round assignment pipelines (as used in the **TDS course at IIT Madras**), where each round delivers a new task, expects a deployed result, and scores based on the output. The pipeline handles all of it:

- Receives structured task assignments via a REST endpoint
- Processes attached images (Base64 / Data URI)
- Prompts **Gemini** to generate a complete, self-contained web application
- Creates or updates a **GitHub repository** programmatically
- Deploys the output to **GitHub Pages** and waits for it to go live
- Notifies the **evaluation server** with the live URL
- Handles multi-round feedback loops and iterative improvements

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Incoming Request                         │
│           POST /task  { task_description, attachments }         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
│                          app.py                                 │
│                                                                 │
│   ┌──────────────────┐        ┌──────────────────────────────┐  │
│   │  models.py       │        │  config.py                   │  │
│   │  Pydantic request│        │  Env vars + secret mgmt      │  │
│   │  / response      │        │  (Gemini key, GitHub token)  │  │
│   └──────────────────┘        └──────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼────────────────┐
                │               │                │
                ▼               ▼                ▼
    ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  helpers.py   │ │  helpers.py  │ │   helpers.py     │
    │               │ │              │ │                  │
    │  Attachment   │ │  Gemini API  │ │  GitHub API      │
    │  Processing   │ │  Code Gen    │ │  Repo + Pages    │
    │  Base64/URI   │ │  Prompting   │ │  Deployment      │
    └───────────────┘ └──────┬───────┘ └──────┬───────────┘
                             │                │
                             ▼                ▼
                    ┌─────────────┐   ┌──────────────────┐
                    │ Generated   │──▶│  GitHub Pages    │
                    │ index.html  │   │  Live public URL │
                    │ README.md   │   └──────────────────┘
                    │ LICENSE     │            │
                    └─────────────┘            ▼
                                    ┌──────────────────────┐
                                    │  Evaluation Server   │
                                    │  Notified with URL   │
                                    └──────────────────────┘
```

---

## 🔄 End-to-End Workflow

### Step 1 — Task Reception
The service receives a `POST /task` request containing the task description, round number, student credentials, and optional image attachments. Pydantic models in `models.py` validate and parse the incoming payload. Attachments are decoded from Base64 or Data URI format and prepared for the prompt.

### Step 2 — Code Generation via Gemini
The task description (and any decoded images) are structured into a detailed prompt and sent to the **Gemini API** via `helpers.py`. The LLM returns a complete, self-contained `index.html` web application — styled, functional, and ready to deploy. The prompt is engineered to produce clean, standalone HTML/CSS/JS with no external build steps required.

### Step 3 — GitHub Repository Management
Using the **GitHub REST API** (via `httpx`), the pipeline:
- Creates a new repository if it doesn't exist, or updates the existing one
- Commits `index.html`, `README.md`, and `LICENSE` in a single push
- Enables **GitHub Pages** on the `main` branch
- Polls the Pages API until the deployment is confirmed live

### Step 4 — Evaluation Notification
Once the live URL is confirmed, the pipeline POSTs the URL back to the **evaluation server** along with student credentials and round metadata. The evaluation server scores the submission and may return a new task for the next round.

### Step 5 — Multi-Round Loop
If the evaluation response contains a follow-up task, the pipeline re-enters the workflow from Step 2, incorporating any feedback or new requirements — supporting iterative improvement across multiple rounds.

```
┌──────────────────────────────────────────────────────────┐
│                  Multi-Round Flow                        │
│                                                          │
│  Round 1 Task ──▶ Generate ──▶ Deploy ──▶ Evaluate      │
│                                               │          │
│                    ┌──────────────────────────┘          │
│                    │  Feedback + Round 2 Task            │
│                    ▼                                     │
│  Round 2 Task ──▶ Generate ──▶ Deploy ──▶ Evaluate      │
│                                               │          │
│                    ┌──────────────────────────┘          │
│                    │  ... continues until END            │
└──────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Capability | Details |
|-----------|---------|
| 🤖 AI Code Generation | Gemini API generates complete, self-contained web apps from a text prompt |
| 🖼️ Attachment Processing | Decodes Base64 and Data URI image attachments for multimodal prompting |
| 🚀 Automated Deployment | Creates GitHub repos and enables Pages — no manual steps |
| 🔁 Multi-Round Support | Handles iterative evaluation loops with feedback-aware re-generation |
| 📬 Evaluation Integration | Auto-notifies the scoring server with the live URL after each deployment |
| 🔐 Secure Config | All secrets managed via environment variables — nothing hardcoded |
| 🐳 Docker-Ready | Single `docker run` spins up the full service |
| ⚡ Async Throughout | Built on `httpx` async client for non-blocking GitHub + Gemini API calls |
| 🛡️ Error Handling | Exponential backoff retries on API failures; structured error responses |

---

## 📁 Project Structure

```
llm-code-deployment-pipeline/
├── app.py              # FastAPI application — endpoints, startup, routing
├── helpers.py          # Core logic: Gemini prompting, GitHub API, deployment
├── models.py           # Pydantic schemas for request/response validation
├── config.py           # Environment variable loading & configuration
├── constants.py        # API base URLs, prompt templates, system constants
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition for deployment
├── .gitignore
└── README.md
```

### File Responsibilities

**`app.py`** — The FastAPI entry point. Defines `/task` and `/status` endpoints. Handles request routing, dependency injection, and startup events.

**`helpers.py`** — The engine of the pipeline. Contains the Gemini API integration (prompt construction, response parsing), GitHub repository creation/update logic, Pages deployment polling, and evaluation server notification.

**`models.py`** — Pydantic models that validate all incoming task payloads and outgoing responses. Ensures type safety and provides clear API contracts.

**`config.py`** — Loads all secrets and configuration from environment variables. Single source of truth for API keys, GitHub credentials, and runtime settings.

**`constants.py`** — Stores GitHub API base URLs, Gemini model names, prompt system instructions, and other values that should not be scattered across the codebase.

---

## 🌐 API Reference

### `POST /task`

Receives a task assignment and triggers the full generate → deploy → notify pipeline.

**Request body:**

```json
{
  "email": "your.email@example.com",
  "secret": "your_student_secret",
  "round": 1,
  "task": "Create a responsive calculator web app with a dark theme and keyboard support.",
  "attachments": [
    {
      "filename": "mockup.png",
      "data": "data:image/png;base64,iVBORw0KGgo..."
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "round": 1,
  "deployed_url": "https://jhapiyush44.github.io/task-round-1/",
  "message": "Deployed and evaluation server notified."
}
```

---

### `GET /status`

Returns the current processing state of the pipeline.

**Response:**

```json
{
  "status": "idle",
  "last_round": 1,
  "last_deployed_url": "https://jhapiyush44.github.io/task-round-1/"
}
```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
STUDENT_SECRET=your_task_submission_secret
```

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Authenticates calls to the Gemini generation API | ✅ |
| `GITHUB_TOKEN` | PAT with `repo` and `pages` scopes for repo + Pages management | ✅ |
| `GITHUB_USERNAME` | GitHub account under which repos are created | ✅ |
| `STUDENT_SECRET` | Auth token for task submission validation | ✅ |

**GitHub token scopes required:**
- `repo` — full repository access (create, push, update)
- `pages` — enable and configure GitHub Pages

Generate a Gemini API key at: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)  
Generate a GitHub PAT at: [github.com/settings/tokens](https://github.com/settings/tokens)

---

## 📦 Generated Artifacts

Each successful task execution creates the following files in the deployed GitHub repository:

| File | Description |
|------|-------------|
| `index.html` | Complete self-contained web application (HTML + CSS + JS in one file) |
| `README.md` | Auto-generated documentation describing the app and its features |
| `LICENSE` | MIT license applied to the generated project |

---

## ▶️ Running Locally

### Prerequisites

- Python 3.10+
- A GitHub account with a Personal Access Token
- A Gemini API key

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/jhapiyush44/llm-code-deployment-pipeline.git
cd llm-code-deployment-pipeline

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env            # then fill in your values

# 5. Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`  
Interactive docs at: `http://localhost:8000/docs`

### Quick test

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "your_secret",
    "round": 1,
    "task": "Build a Pomodoro timer with start/stop/reset controls and a clean UI.",
    "attachments": []
  }'
```

---

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t llm-deploy-pipeline .

# Run with environment variables
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_key" \
  -e GITHUB_TOKEN="your_token" \
  -e GITHUB_USERNAME="your_username" \
  -e STUDENT_SECRET="your_secret" \
  llm-deploy-pipeline
```

---

## 🤗 Deploying to Hugging Face Spaces

This repo includes a `Dockerfile` configured for Hugging Face Spaces (port `7860`).

```bash
# 1. Create a new Docker Space on huggingface.co

# 2. Add your secrets in the Space settings:
#    GEMINI_API_KEY, GITHUB_TOKEN, GITHUB_USERNAME, STUDENT_SECRET

# 3. Push this repo to your Space
git remote add hf https://huggingface.co/spaces/YOUR_HF_USERNAME/space-name
git push hf main
```

The Space will build from the Dockerfile and your service will be live at `https://huggingface.co/spaces/YOUR_HF_USERNAME/space-name`.

> ⚠️ Never commit API keys or tokens to git. Always use the Space's "Secrets" settings panel.

---

## 🛡️ Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Gemini API failure | Automatic retry with exponential backoff |
| GitHub API rate limit | Detects 429 responses, backs off, retries |
| Pages deployment delay | Polls the Pages API until live (with timeout) |
| Invalid task payload | Pydantic raises a structured `422 Unprocessable Entity` |
| Missing environment variables | Config module raises at startup with a clear message |
| Evaluation server unreachable | Logs the failure, returns partial success with deployed URL |

---

## 🔮 Roadmap

- [ ] Support for multiple LLM backends (OpenAI GPT-4o, Claude, local Ollama)
- [ ] Vercel / Netlify deployment as alternatives to GitHub Pages
- [ ] Screenshot-based visual evaluation of deployed apps
- [ ] Web UI dashboard for task history and deployment status
- [ ] Prompt versioning and A/B testing for code generation quality

---

## 👨‍💻 Author

**Piyush Jha** — ML Engineer & Python Developer  
[GitHub](https://github.com/jhapiyush44) · [LinkedIn](https://www.linkedin.com/in/piyush-jha-3904a81a6/) · jhapiyush44@gmail.com

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Found this useful? Consider leaving a ⭐ — it helps others discover the project!*
