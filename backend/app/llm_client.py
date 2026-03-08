"""Local LLM client using llama-cpp-python.

Loads a GGUF model from backend/models/ and runs inference locally.
Auto-downloads the model on first use.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

# Model configuration
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = MODEL_DIR / MODEL_FILENAME
MODEL_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"

# System prompt that defines our AI's personality
SYSTEM_PROMPT = """Sei Devin AI Assistant, un assistente intelligente per Windows.
Rispondi in modo utile, preciso e conciso. Puoi parlare in italiano e inglese.
Se non sai qualcosa, dillo onestamente. Sei sempre pronto ad imparare dall'utente.
Hai accesso a strumenti per leggere/scrivere file, eseguire comandi PowerShell e cercare nel codice."""


class LocalLLM:
    """Local LLM inference using llama-cpp-python."""

    def __init__(self, n_ctx: int = 2048, n_gpu_layers: int = 0) -> None:
        self._model = None
        self._available: bool | None = None
        self._n_ctx = n_ctx
        self._n_gpu_layers = n_gpu_layers
        self._download_attempted = False

    def _ensure_model_dir(self) -> None:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def _download_model(self) -> bool:
        """Download the model from HuggingFace Hub."""
        if self._download_attempted:
            return MODEL_PATH.exists()
        self._download_attempted = True

        if MODEL_PATH.exists():
            return True

        self._ensure_model_dir()
        print(f"[LLM] Downloading model {MODEL_FILENAME} from {MODEL_REPO}...")
        print(f"[LLM] This will take a few minutes (~637MB)...")

        try:
            from huggingface_hub import hf_hub_download

            hf_hub_download(
                repo_id=MODEL_REPO,
                filename=MODEL_FILENAME,
                local_dir=str(MODEL_DIR),
                local_dir_use_symlinks=False,
            )
            print(f"[LLM] Model downloaded to {MODEL_PATH}")
            return True
        except ImportError:
            print("[LLM] huggingface_hub not installed. Run: pip install huggingface-hub")
            return False
        except Exception as e:
            print(f"[LLM] Download failed: {e}")
            return False

    def _load_model(self) -> bool:
        """Load the GGUF model into memory."""
        if self._model is not None:
            return True

        if not self._download_model():
            return False

        try:
            from llama_cpp import Llama

            print(f"[LLM] Loading model from {MODEL_PATH}...")
            self._model = Llama(
                model_path=str(MODEL_PATH),
                n_ctx=self._n_ctx,
                n_gpu_layers=self._n_gpu_layers,
                verbose=False,
            )
            print("[LLM] Model loaded successfully!")
            return True
        except ImportError:
            print("[LLM] llama-cpp-python not installed. Run: pip install llama-cpp-python")
            return False
        except Exception as e:
            print(f"[LLM] Failed to load model: {e}")
            return False

    def is_available(self) -> bool:
        """Check if the LLM is ready for inference."""
        if self._available is not None:
            return self._available
        try:
            self._available = self._load_model()
        except Exception:
            self._available = False
        return self._available

    def generate(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 256,
        temperature: float = 0.7,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a response from the local LLM.

        Returns dict with 'text', 'tokens_used', 'success'.
        """
        if not self.is_available():
            return {
                "text": "",
                "tokens_used": 0,
                "success": False,
                "error": "Model not available",
            }

        try:
            # Build chat messages in ChatML format
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})

            messages.append({"role": "user", "content": prompt})

            response = self._model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop or ["</s>", "<|im_end|>"],
            )

            text = response["choices"][0]["message"]["content"].strip()
            tokens = response.get("usage", {}).get("total_tokens", 0)

            return {
                "text": text,
                "tokens_used": tokens,
                "success": True,
            }
        except Exception as e:
            return {
                "text": "",
                "tokens_used": 0,
                "success": False,
                "error": str(e),
            }

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model": MODEL_FILENAME,
            "repo": MODEL_REPO,
            "path": str(MODEL_PATH),
            "loaded": self._model is not None,
            "available": self.is_available() if self._available is not None else "unknown",
            "context_size": self._n_ctx,
        }


# Singleton instance
llm = LocalLLM()
