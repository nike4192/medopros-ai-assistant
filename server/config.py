import os
from dotenv import load_dotenv

load_dotenv()

# --- Server Config ---
PORT = int(os.getenv("PORT", 8001))
SITE_URL = os.getenv("SITE_URL", "http://localhost:8001")
SITE_NAME = os.getenv("SITE_NAME", "Medopros MVP")
SECRET_KEY = os.getenv("SECRET_KEY", "medopros_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

# --- AI Models ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "openrouter/free")

# Голосовое распознавание: GigaAM-v3 (Сбер) локально через onnx-asr.
# `ASR_ENGINE=openrouter` возвращает прежнее поведение (Whisper через OpenRouter).
ASR_ENGINE = (os.getenv("ASR_ENGINE") or "gigaam").strip().lower()
GIGAAM_MODEL = os.getenv("GIGAAM_MODEL", "gigaam-v3-e2e-rnnt")
GIGAAM_QUANTIZATION = os.getenv("GIGAAM_QUANTIZATION", "int8")
GIGAAM_MAX_SPEECH_S = float(os.getenv("GIGAAM_MAX_SPEECH_S", "25"))
# Греть модель в фоне при старте (первый запрос не ждёт загрузки).
GIGAAM_WARMUP = os.getenv("GIGAAM_WARMUP", "1").strip().lower() not in ("0", "false", "no")
# Если GigaAM недоступна/упала — попробовать OpenRouter (Whisper) как запасной движок.
ASR_FALLBACK_OPENROUTER = os.getenv("ASR_FALLBACK_OPENROUTER", "1").strip().lower() not in ("0", "false", "no")

# Параметры OpenRouter (используются только при ASR_ENGINE=openrouter или как fallback)
AUDIO_MODEL = os.getenv("AUDIO_MODEL", "openai/whisper-large-v3-turbo")
FALLBACK_AUDIO_MODELS = os.getenv("FALLBACK_AUDIO_MODELS", "google/chirp-3,nvidia/parakeet-tdt-0.6b-v3,openai/whisper-1").split(",")

# --- Notifications ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Auth ---
LOGIN_USER = os.getenv("LOGIN_USER", "admin")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "admin")
UGMK_API_KEY = os.getenv("UGMK_API_KEY")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RECORDINGS_DIR = os.path.join(DATA_DIR, "recordings")
FAILED_DIR = os.path.join(DATA_DIR, "failed")

if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
