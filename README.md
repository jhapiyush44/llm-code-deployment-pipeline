# LLM Code Deployment Pipeline

A robust FastAPI service that automatically generates, deploys, and manages web applications using LLM (Gemini) for code generation and GitHub Pages for hosting. The system handles multi-round task assignments, processes attachments, and provides automated evaluation feedback.

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Code Generation | Leverages Gemini API for intelligent code generation based on task requirements |
| 🚀 Automated Deployment | Seamlessly deploys generated applications to GitHub Pages |
| 📊 Multi-Round Support | Handles multiple rounds of task submissions and improvements |
| 🖼️ Attachment Processing | Processes image attachments with Base64/Data URI support |
| 🔄 Evaluation Integration | Built-in evaluation server notification system |
| 🔐 Secure Configuration | Environment-based configuration with secret management |

## 🏗️ Architecture

| Component | Purpose |
|-----------|---------|
| `main.py` | FastAPI application entry point and endpoint definitions |
| `helpers.py` | Utility functions for LLM integration and file operations |
| `models.py` | Pydantic models for request/response validation |
| `config.py` | Configuration management using environment variables |
| `constants.py` | System-wide constants and API endpoints |

## 📋 API Endpoints

| Endpoint | Description |
|----------|-------------|
| POST `/task` | Receives task assignments and triggers code generation |
| GET `/status` | Retrieves current task processing status |

## 🔧 Setup

1. Clone the repository:
```bash
git clone https://github.com/jhapiyush44/llm-code-deployment-pipeline.git
cd llm-code-deployment-pipeline
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
# - GEMINI_API_KEY
# - GITHUB_TOKEN
# - GITHUB_USERNAME
# - STUDENT_SECRET
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app:app --reload
```

## 🔄 Workflow

1. **Task Reception**
   - System receives task details and attachments
   - Validates student credentials and task parameters

2. **Code Generation**
   - Processes task requirements
   - Generates web application using Gemini API
   - Creates necessary documentation

3. **Deployment**
   - Creates/updates GitHub repository
   - Deploys to GitHub Pages
   - Notifies evaluation server

4. **Evaluation**
   - Handles evaluation server feedback
   - Supports multiple rounds of improvements

## 🛠️ Configuration

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Authentication for Gemini API | Yes |
| `GITHUB_TOKEN` | GitHub API authentication | Yes |
| `GITHUB_USERNAME` | GitHub account for deployments | Yes |
| `STUDENT_SECRET` | Authentication for task submissions | Yes |

## 📦 Generated Artifacts

Each task generates:

| File | Description |
|------|-------------|
| `index.html` | Main web application file |
| `README.md` | Project documentation |
| `LICENSE` | MIT license file |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔍 Error Handling

| Error Type | Handling Strategy |
|------------|------------------|
| API Failures | Automatic retries with exponential backoff |
| Invalid Requests | Detailed error responses via FastAPI |
| Deployment Issues | Robust cleanup and recovery mechanisms |

## 🔗 Dependencies

| Package | Usage |
|---------|--------|
| FastAPI | Web framework |
| Pydantic | Data validation |
| httpx | Async HTTP client |
| GitPython | Git operations |
| python-dotenv | Environment management |

## 📝 Notes

- Ensure proper GitHub permissions for repository creation and Pages deployment
- Configure GitHub token with appropriate scopes
- Monitor API rate limits for both Gemini and GitHub
- Keep secrets secure and never commit them to version control

## 🚀 Deploying to Hugging Face Spaces

You can deploy the generated web app to Hugging Face Spaces either as a Python (Gradio/Streamlit) Space using `requirements.txt` or as a Docker-based Space using the provided `Dockerfile`.

Below are concise steps and PowerShell-friendly commands to get you started.

### Option A — Python Space (Gradio / Streamlit)

1. Install the Hugging Face CLI and log in:

```powershell
pip install huggingface_hub
huggingface-cli login
# Follow the prompt to paste your HF token
```

2. Create a new Space on Hugging Face (via web UI) or from the CLI:

```powershell
# Create from CLI (replace YOUR-USERNAME and space-name)
hf api repos/create -y --type=space --name YOUR-USERNAME/space-name
```

3. Prepare your repository

- Ensure `requirements.txt` lists runtime dependencies (FastAPI, uvicorn, gradio/streamlit if used, etc.).
- Add a minimal `app.py` or `app` entrypoint expected by your chosen frontend (Gradio/Streamlit). For a pure backend FastAPI app, you can include a tiny `app.py` that starts the server or use Docker (Option B).

4. Push code to the Space

```powershell
git init
git remote add origin https://huggingface.co/spaces/YOUR-USERNAME/space-name
git add .
git commit -m "Initial commit: deploy app to HF Spaces"
git push origin main
```

Notes:
- The Space will install packages from `requirements.txt` automatically.
- For Gradio/Streamlit front-ends, HF will detect and run them automatically.

### Option B — Docker-based Space

If your project already contains a `Dockerfile` (this repo does), you can deploy using Docker. This gives you full control over the runtime.

1. Create a Space and enable Docker in the Space settings (choose "Dockerfile" type) via the Hugging Face web UI.

2. Push your repository to the Space (same push commands as above). The Space build will use your `Dockerfile`.

3. Troubleshooting tips

- If builds fail, check the build logs on the Space page for missing packages or permission errors.
- Ensure any runtime secrets (API keys) are set using the Space's "Secrets" settings — do NOT commit secrets to git.

### Quick checklist before deploying

- [ ] Add/verify `requirements.txt` contains everything needed for the app to run.
- [ ] If using Docker, confirm `Dockerfile` builds locally: `docker build -t test-app .` (optional)
- [ ] Add a short `README.md` in the generated artifact folder to explain the Space's purpose.
- [ ] Configure HF Space secrets for any API keys (Gemini/GitHub tokens) rather than committing them.