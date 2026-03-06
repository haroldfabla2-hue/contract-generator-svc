# 🤖 Contract Generator SaaS

AI-powered contract generation service that creates professional legal documents using GLM LLM.

## 🚀 Features

- **AI-Powered Generation** - Uses GLM-4 to generate legally-structured contracts
- **Multiple Contract Types** - NDA, Contractor Agreement, Employment, Lease, Services
- **Professional Output** - Valid legal document format
- **Fast API Backend** - Built with FastAPI for high performance
- **Modern Frontend** - Clean TailwindCSS UI
- **Professional Landing Page** - Dedicated marketing page under `landing/`
- **Docker Ready** - Easy deployment with Docker

## 🛠️ Tech Stack

- **Backend**: Python FastAPI
- **AI**: GLM-4 (Z.ai)
- **Frontend (App)**: HTML + TailwindCSS
- **Frontend (Landing)**: HTML + TailwindCSS + Nginx static serving
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

### With Docker (App + Landing)

```bash
# Build and run all services
docker-compose up --build
```

Services:
- App: `http://localhost:8001`
- Landing: `http://localhost:8002`

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `GLM_API_KEY` | Your GLM API key from Z.ai |
| `MERCADO_PAGO_KEY` | Mercado Pago for payments |

### Landing configuration

Edit `landing/config.js` to set:
- App URL (`APP_URL`)
- Mercado Pago / PayPal checkout links
- Contact form action URL (optional)

> ⚠️ Do not store API keys or credentials in `landing/config.js`.

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main app page |
| POST | `/api/generate` | Generate contract |
| GET | `/api/contract-types` | Available types |
| POST | `/api/payment/initiate` | Create payment |

## 📄 Example Request

```bash
curl -X POST http://localhost:8001/api/generate \
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
3. Deploy both services from docker-compose

## 📝 License

MIT License - feel free to use!

---

Built with 💜 by Silhouette Automated Agency
