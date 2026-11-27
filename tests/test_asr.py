import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.services import asr  # noqa: E402


def run(coro):
    return asyncio.run(coro)


def test_extract_text_variants():
    assert asr.extract_text({"text": " Болит нога "}) == "Болит нога"
    assert asr.extract_text({"result": "Течёт нос"}) == "Течёт нос"
    assert asr.extract_text({"transcript": "Плачут глазки"}) == "Плачут глазки"
    assert asr.extract_text({"result": {"text": "Попа болит"}}) == "Попа болит"
    assert asr.extract_text({"error": "nope"}) == ""
    assert asr.extract_text("plain text") == "plain text"


def test_gigaam_api_requires_url(monkeypatch):
    monkeypatch.setattr(asr, "GIGAAM_API_URL", "")
    try:
        run(asr.transcribe_gigaam_api("/tmp/does-not-matter.wav"))
    except RuntimeError as exc:
        assert "GIGAAM_API_URL" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected RuntimeError")


def test_default_engine_uses_remote_gigaam(monkeypatch):
    calls = []

    async def fake_remote(wav_path):
        calls.append(wav_path)
        return "Болит нога"

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam_api")
    monkeypatch.setattr(asr, "transcribe_gigaam_api", fake_remote)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "Болит нога"
    assert calls == ["/tmp/a.wav"]


def test_fallback_to_openrouter_on_remote_error(monkeypatch):
    async def fake_remote(wav_path):
        raise RuntimeError("service is down")

    async def fake_openrouter(wav_path):
        return "whisper text"

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam_api")
    monkeypatch.setattr(asr, "ASR_FALLBACK_OPENROUTER", True)
    monkeypatch.setattr(asr, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(asr, "transcribe_gigaam_api", fake_remote)
    monkeypatch.setattr(asr, "transcribe_audio_base64", fake_openrouter)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "whisper text"


def test_no_fallback_when_disabled(monkeypatch):
    async def fake_remote(wav_path):
        raise RuntimeError("service is down")

    monkeypatch.setattr(asr, "ASR_ENGINE", "gigaam_api")
    monkeypatch.setattr(asr, "ASR_FALLBACK_OPENROUTER", False)
    monkeypatch.setattr(asr, "transcribe_gigaam_api", fake_remote)

    try:
        run(asr.transcribe_audio_file("/tmp/a.wav"))
    except RuntimeError as exc:
        assert "down" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected RuntimeError")


def test_openrouter_engine_skips_remote(monkeypatch):
    async def fake_openrouter(wav_path):
        return "whisper text"

    async def fake_remote(wav_path):  # pragma: no cover - не должен вызваться
        raise AssertionError("GigaAM API must not be called")

    monkeypatch.setattr(asr, "ASR_ENGINE", "openrouter")
    monkeypatch.setattr(asr, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(asr, "transcribe_gigaam_api", fake_remote)
    monkeypatch.setattr(asr, "transcribe_audio_base64", fake_openrouter)

    assert run(asr.transcribe_audio_file("/tmp/a.wav")) == "whisper text"


def test_filter_hallucinations_empty():
    assert asr.filter_hallucinations(" Thank you. ") == ""
    assert asr.filter_hallucinations("Болит нога") == "Болит нога"
