1) Quick Start

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/prod.txt
ollama list
python -c "from api.database import init_db; init_db()"
uvicorn api.main:app --host 0.0.0.0 --port 8000
streamlit run dashboard/dashboard.py

echo "http://localhost:1234/api/v0/docs"




# Clone repository
git clone https://github.com/EduCoreAi/Ai-Brain.git
cd Ai-Brain

# Install dependencies
docker-compose -f docker/docker-compose.yml up -d

# Access interfaces
echo "Dashboard: http://localhost:8501 | API: http://localhost:8000"


2) Detailed Setup

## Install Prerequisites
Docker
Python 3.11
NVIDIA CUDA Toolkit
Ollama


## Install Models

1) Pull a model (e.g., Llama 3)
ollama pull llama3
ollama pull mistral
ollama pull phi4-mini
ollama pull deepseek-llm
ollama pull gemma:2b
ollama pull gemma:7b

2) Verify models
ollama list


### Configure Environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/prod.txt


### Initialize Database
python -c "from api.database import init_db; init_db()"

### Start Services : Manual Start (Backend)
uvicorn api.main:app --host 0.0.0.0 --port 8000
streamlit run dashboard/dashboard.py

echo "http://localhost:1234/api/v0/docs"
echo "Dashboard: http://localhost:8501 | API: http://localhost:8000"


### Verify
curl http://localhost:8000/health  # Should return "OK"

