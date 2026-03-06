# 🤖 Contract Generator SaaS

AI-powered contract generation service that creates professional legal documents using GLM LLM.

## 🚀 Features

- **AI-Powered Generation** - Uses GLM-4 to generate legally-structured contracts
- **Multiple Contract Types** - NDA, Contractor Agreement, Employment, Lease, Services
- **Professional Output** - Valid legal document format
- **Fast API Backend** - Built with FastAPI for high performance
- **Modern Frontend** - Clean TailwindCSS UI
- **Docker Ready** - Easy deployment with Docker

## 🛠️ Tech Stack

- **Backend**: Python FastAPI
- **AI**: GLM-4 (Z.ai)
- **Frontend**: HTML + TailwindCSS
- **Deployment**: Docker + Coolify

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Development

```bash
# Clone the repository
git clone https://github.com/haroldfabla2-hue/contract-generator-svc.git
cd contract-generator-svc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your GLM_API_KEY

# Run the server
uvicorn app.main:app --reload
```

### With Docker

```bash
# Build and run
docker-compose up --build

# Or with environment
GLM_API_KEY=your_key docker-compose up
```

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `GLM_API_KEY` | Your GLM API key from Z.ai |
| `MERCADO_PAGO_KEY` | Mercado Pago for payments |

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main page |
| POST | `/api/generate` | Generate contract |
| GET | `/api/contract-types` | Available types |
| POST | `/api/payment/initiate` | Create payment |

## 📄 Example Request

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "nda",
    "parties": ["Empresa A", "Empresa B"],
    "terms": "Confidencialidad por 2 años"
  }'
```

## 🚢 Deployment

Deploy to your Coolify instance:

1. Connect your GitHub repository
2. Set environment variables
3. Deploy!

The app runs on port 8000.

## 📝 License

MIT License - feel free to use!

---

Built with 💜 by Silhouette Automated Agency
