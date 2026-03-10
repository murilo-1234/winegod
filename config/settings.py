"""Configurações gerais do WineGod."""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://winegod:winegod_dev@localhost:5433/winegod")

# AI APIs
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Proxy (ML / Amazon)
PROXY_HOST = os.getenv("PROXY_HOST", "geo.iproyal.com")
PROXY_PORT = os.getenv("PROXY_PORT", "12321")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

# Limites
MEMORIA_LIMITE_MB = int(os.getenv("MEMORIA_LIMITE_MB", "350"))
MAX_BROWSERS_SIMULTANEOS = int(os.getenv("MAX_BROWSERS", "2"))

# Rate limits (segundos entre requests)
RATE_LIMIT_DEFAULT = 1.0
RATE_LIMIT_AGGRESSIVE = 2.0  # Para sites sensíveis
RATE_LIMIT_GENTLE = 0.5      # Para APIs públicas

# User Agent padrão
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
