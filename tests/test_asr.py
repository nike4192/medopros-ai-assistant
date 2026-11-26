import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.services import asr  # noqa: E402


def run(coro):
    return asyncio.run(coro)


def test_filter_hallucinations_empty():
    assert asr.filter_hallucinations(" Thank you. ") == ""
    assert asr.filter_hallucinations("Болит нога") == "Болит нога"


def test_gigaam_is_default(monkeypatch):
    calls = []

    def fake_sync(wav_path):
        calls.append(wav_path)
        return "Болит нога"

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam")
    monkeypatch.setattr(asr, "_transcribe_gigaam_sync", fake_sync)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "Болит нога"
    assert calls == ["/tmp/a.wav"]


def test_fallback_to_openrouter_on_gigaam_error(monkeypatch):
    async def fake_openrouter(wav_path):
        return "whisper text"

    def fake_sync(wav_path):
        raise RuntimeError("model is broken")

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam")
    monkeypatch.setattr(asr, "ASR_FALLBACK_OPENROUTER", True)
    monkeypatch.setattr(asr, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(asr, "_transcribe_gigaam_sync", fake_sync)
    monkeypatch.setattr(asr, "transcribe_audio_base64", fake_openrouter)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "whisper text"


def test_no_fallback_when_disabled(monkeypatch):
    def fake_sync(wav_path):
        raise RuntimeError("model is broken")

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam")
    monkeypatch.setattr(asr, "ASR_FALLBACK_OPENROUTER", False)
    monkeypatch.setattr(asr, "_transcribe_gigaam_sync", fake_sync)

    try:
        run(asr.transcribe_audio_file("/tmp/a.wav"))
    except RuntimeError as exc:
        assert "broken" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected RuntimeError")


def test_openrouter_engine_skips_gigaam(monkeypatch):
    async def fake_openrouter(wav_path):
        return "whisper text"

    def fake_sync(wav_path):  # pragma: no cover - не должен вызваться
        raise AssertionError("GigaAM must not be called")

    monkeypatch.setattr(asr, "ASR_ENGINE", "openrouter")
    monkeypatch.setattr(asr, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(asr, "_transcribe_gigaam_sync", fake_sync)
    monkeypatch.setattr(asr, "transcribe_audio_base64", fake_openrouter)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "whisper text"
