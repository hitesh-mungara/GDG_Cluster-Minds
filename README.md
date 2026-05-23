# AI-Powered Security Scanning & Automated PR System

An intelligent security scanning system that automatically analyzes repositories using Trivy, prioritizes vulnerabilities using AI, and creates pull requests with security fixes.

## 🌐 Deployment

### Quick Deploy to Google Cloud Run

```bash
# Install gcloud CLI
brew install --cask google-cloud-sdk

# Run deployment script
./deploy.sh
```

📚 **Deployment Guides:**
- **Quick Start**: See `QUICK_START.md` for fast deployment
- **Step-by-Step Commands**: See `COMMANDS_TO_RUN.md` for copy-paste commands
- **Complete Guide**: See `DEPLOYMENT_GUIDE.md` for detailed documentation

## 🚀 Features

- **Automated Security Scanning**: Scans repositories using Trivy API for vulnerabilities, secrets, and misconfigurations
- **AI-Powered Analysis**: Uses Google Gemini AI to analyze vulnerabilities and generate remediation plans
- **Risk Prioritization**: Intelligent risk scoring based on severity, exploitability, and threat intelligence
- **Automatic Fixes**: Generates and applies security fixes for Node.js and Maven projects
- **Smart PR Creation**: AI decides whether to automatically create PRs based on risk assessment
- **Multi-Agent Pipeline**: Coordinated workflow using LangGraph agents

## 📋 Prerequisites

- Python 3.8+
- Git
- GitHub Personal Access Token
- Google API Key (for Gemini AI)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd security
```

2. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
GITHUB_TOKEN=your_github_token_here
GOOGLE_API_KEY=your_google_api_key_here
```

## 🎯 Usage

### Start the API Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Scan a Repository

Send a POST request to `/analyze`:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/owner/repo.git",
    "severity": "CRITICAL,HIGH",
    "scanners": "vuln,secret,misconfig"
  }'
```

**Parameters:**
- `repo_url` (required): Git repository URL
- `severity` (optional): Comma-separated severity levels (default: "CRITICAL,HIGH")
- `scanners` (optional): Comma-separated scanner types (default: "vuln,secret,misconfig")

## 🔄 Agent Pipeline

The system uses a multi-agent workflow:

1. **Parse Agent**: Extracts vulnerabilities from Trivy scan results
2. **Intel Agent**: Enriches findings with threat intelligence from NVD
3. **Risk Agent**: Calculates risk scores and prioritizes vulnerabilities
4. **Remediation Agent**: AI generates remediation strategies
5. **Fix Agent**: Automatically updates package.json or pom.xml with fixed versions
6. **PR Decision Agent**: AI decides if automatic PR creation is safe
7. **PR Agent**: Creates and pushes a pull request with fixes
8. **Workflow Agent**: Triggers additional actions (Slack alerts, JIRA tickets)

## 🛠️ Supported Project Types

- **Node.js**: Automatically updates `package.json` dependencies
- **Maven**: Automatically updates `pom.xml` dependencies

## 🔐 Security Notes

- Never commit `.env` file with real credentials
- GitHub token requires `repo` scope for creating PRs
- Tokens are loaded from environment variables, not hardcoded
- The system detects the default branch dynamically (main/master)

## 📊 API Response

The API returns a comprehensive analysis including:
- Parsed vulnerabilities
- Enriched threat intelligence
- Risk scores and prioritization
- AI-generated remediation plans
- Applied fixes
- PR creation status

## 🐛 Troubleshooting

### Common Issues

1. **"Trivy scan failed"**
   - Check if the Trivy API is accessible
   - Verify the repository URL is correct and public

2. **"Git push failed"**
   - Ensure GITHUB_TOKEN has correct permissions
   - Check if you have write access to the repository

3. **"AI rejected PR creation"**
   - The AI determined the changes might break the application
   - Review the fixes manually and create PR yourself

4. **Import errors**
   - Run `pip install -r backend/requirements.txt`
   - Ensure you're using Python 3.8+

## 📝 Configuration

### Trivy API Endpoint
The system uses an external Trivy API. To change the endpoint, edit `backend/main.py`:
```python
trivy_response = requests.post(
    "https://your-trivy-api-endpoint.com/scan",
    json=trivy_payload,
    timeout=600
)
```

### AI Model
To change the AI model, edit `agents/pr_decision_agent.py` and `agents/remediation_agent.py`:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",  # Change model here
    google_api_key=os.getenv("GOOGLE_API_KEY", "")
)
```

## 🤝 Contributing

Contributions are welcome! Please ensure:
- No hardcoded secrets
- Proper error handling
- Updated documentation

## 📄 License

[Add your license here]

## 🔗 Related Tools

- [Trivy](https://github.com/aquasecurity/trivy) - Vulnerability scanner
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework