import json
import os
import socket
import threading
import time
import uuid
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


APP_HOME = os.environ.get("WRITE_APP_HOME", os.path.join(os.path.expanduser("~"), "Write"))
DATA_FILE = os.path.join(APP_HOME, "data.json")
AI_REQUEST_TIMEOUT_SEC = 180


@dataclass
class Block:
    id: str
    type: str = "paragraph"
    content: str = ""
    checked: bool = False
    language: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "checked": self.checked,
            "language": self.language,
        }


class WriteBackend:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self._lock = threading.RLock()
        self._autosave_interval = 30
        self._autosave_thread: Optional[threading.Thread] = None
        self._stop_autosave = threading.Event()
        self._dirty = False
        self._last_saved_at: Optional[str] = None

        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.data = self._load_or_initialize()
        self._ensure_defaults()

    def _current_timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _load_or_initialize(self) -> Dict:
        if not os.path.exists(self.data_file):
            data = self._build_default_store()
            self._write_json(data)
            return data

        try:
            with open(self.data_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            data = self._build_default_store()
            self._write_json(data)

        return data

    def _build_default_store(self) -> Dict:
        default_page = self._new_page(title="Untitled", blocks=[self._new_block(type_="paragraph", content="")])
        return {
            "pages": [default_page],
            "settings": {
                "theme": "light",
                "font_family": "Segoe UI",
                "font_size": 13,
                "autosave_interval_sec": 30,
                "ai_api_key": "",
                "ai_provider": "openai",
            },
            "session": {
                "last_open_page_id": default_page["id"],
                "focus_score": 85,
                "chat_history": [],
                "ai_context_page_ids": [],
                "last_activity_at": self._current_timestamp(),
            },
        }

    def _ensure_defaults(self) -> None:
        with self._lock:
            if not isinstance(self.data.get("pages"), list):
                self.data["pages"] = []
            if not isinstance(self.data.get("settings"), dict):
                self.data["settings"] = {}

            defaults = {
                "theme": "light",
                "font_family": "Segoe UI",
                "font_size": 13,
                "autosave_interval_sec": 30,
                "ai_api_key": "",
                "ai_provider": "openai",
            }
            for key, value in defaults.items():
                self.data["settings"].setdefault(key, value)

            if not isinstance(self.data.get("session"), dict):
                self.data["session"] = {}

            session_defaults = {
                "last_open_page_id": None,
                "focus_score": 85,
                "chat_history": [],
                "ai_context_page_ids": [],
                "last_activity_at": self._current_timestamp(),
            }
            for key, value in session_defaults.items():
                self.data["session"].setdefault(key, value)

            if not self.data["pages"]:
                default_page = self._new_page(title="Untitled", blocks=[self._new_block(type_="paragraph", content="")])
                self.data["pages"].append(default_page)

            active = self.data["session"].get("last_open_page_id")
            if not active or not any(page["id"] == active for page in self.data["pages"]):
                self.data["session"]["last_open_page_id"] = self.data["pages"][0]["id"]

            self._autosave_interval = int(self.data["settings"].get("autosave_interval_sec") or 30)
            self._dirty = True
            self.save(force=True)

    def _new_block(self, type_: str = "paragraph", content: str = "", checked: bool = False, language: Optional[str] = None) -> Dict:
        return {
            "id": str(uuid.uuid4()),
            "type": type_,
            "content": content,
            "checked": checked,
            "language": language,
        }

    def _new_page(self, title: str = "Untitled", blocks: Optional[List[Dict]] = None) -> Dict:
        now = self._current_timestamp()
        page = {
            "id": str(uuid.uuid4()),
            "title": title,
            "created_at": now,
            "updated_at": now,
            "blocks": blocks or [],
        }
        return page

    def _write_json(self, payload: Dict) -> None:
        tmp_path = f"{self.data_file}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.replace(tmp_path, self.data_file)

    def save(self, force: bool = False) -> Dict:
        with self._lock:
            if not force and not self._dirty:
                return self._snapshot_status()

            self._write_json(self.data)
            self._dirty = False
            self._last_saved_at = self._current_timestamp()
            self.data["session"]["last_activity_at"] = self._last_saved_at
            return self._snapshot_status()

    def _snapshot_status(self) -> Dict:
        return {
            "saved_at": self._last_saved_at,
            "dirty": self._dirty,
            "page_count": len(self.data.get("pages") or []),
            "active_page_id": self.data["session"].get("last_open_page_id"),
        }

    def list_pages(self, search: Optional[str] = None) -> List[Dict]:
        pages = list(self.data.get("pages") or [])
        if search:
            query = search.lower()
            pages = [page for page in pages if query in page.get("title", "").lower()]
        return sorted(pages, key=lambda item: item.get("updated_at") or "", reverse=True)

    def create_page(self, title: str = "Untitled") -> Dict:
        page = self._new_page(title=title, blocks=[self._new_block(type_="paragraph", content="")])
        self.data["pages"].append(page)
        self.data["session"]["last_open_page_id"] = page["id"]
        self._dirty = True
        self.save(force=True)
        return page

    def get_page(self, page_id: Optional[str] = None) -> Optional[Dict]:
        if page_id is None:
            page_id = self.data["session"].get("last_open_page_id")
        for page in self.data["pages"]:
            if page["id"] == page_id:
                return page
        return None

    def select_page(self, page_id: str) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError(f"Page '{page_id}' not found")
        self.data["session"]["last_open_page_id"] = page_id
        self._dirty = True
        self.save(force=True)
        return page

    def update_page_metadata(self, page_id: str, title: Optional[str] = None, blocks: Optional[List[Dict]] = None) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError(f"Page '{page_id}' not found")

        if title is not None:
            page["title"] = title

        if blocks is not None:
            page["blocks"] = [
                {
                    "id": block.get("id") or str(uuid.uuid4()),
                    "type": block.get("type"),
                    "content": block.get("content"),
                    "checked": bool(block.get("checked")),
                    "language": block.get("language"),
                }
                for block in blocks
            ]

        page["updated_at"] = self._current_timestamp()
        self._dirty = True
        self.save(force=True)
        return page

    def set_title(self, page_id: str, title: str) -> Dict:
        return self.update_page_metadata(page_id=page_id, title=title)

    def set_blocks(self, page_id: str, blocks: List[Dict]) -> Dict:
        return self.update_page_metadata(page_id=page_id, blocks=blocks)

    def apply_block_operation(self, page_id: str, operation: str, block_id: Optional[str] = None, block: Optional[Dict] = None) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError(f"Page '{page_id}' not found")

        blocks = page["blocks"]

        if operation == "insert":
            new_block = block or self._new_block(type_="paragraph", content="")
            if not new_block.get("id"):
                new_block["id"] = str(uuid.uuid4())
            blocks.append(new_block)
        elif operation == "delete":
            if not block_id:
                raise ValueError("block_id is required for delete")
            blocks[:] = [item for item in blocks if item["id"] != block_id]
        elif operation == "move":
            if not block_id or block is None:
                raise ValueError("block_id and destination index are required for move")
            target_index = block.get("index")
            current = [item for item in blocks if item["id"] == block_id]
            if not current:
                raise KeyError(f"Block '{block_id}' not found")
            blocks[:] = [item for item in blocks if item["id"] != block_id]
            target_index = max(0, min(int(target_index), len(blocks)))
            blocks[target_index:target_index] = current
        elif operation == "update":
            if not block_id:
                raise ValueError("block_id is required for update")
            for index, item in enumerate(blocks):
                if item["id"] == block_id:
                    blocks[index].update(block or {})
                    break
            else:
                raise KeyError(f"Block '{block_id}' not found")
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        page["updated_at"] = self._current_timestamp()
        self._dirty = True
        self.save(force=True)
        return page

    def delete_page(self, page_id: str) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError(f"Page '{page_id}' not found")

        self.data["pages"] = [item for item in self.data["pages"] if item["id"] != page_id]
        ai_context = self.data["session"].get("ai_context_page_ids") or []
        self.data["session"]["ai_context_page_ids"] = [pid for pid in ai_context if pid != page_id]

        if self.data["pages"]:
            self.data["session"]["last_open_page_id"] = self.data["pages"][0]["id"]
        else:
            new_page = self._new_page(title="Untitled", blocks=[self._new_block(type_="paragraph", content="")])
            self.data["pages"] = [new_page]
            self.data["session"]["last_open_page_id"] = new_page["id"]

        self._dirty = True
        self.save(force=True)
        return {"deleted": page_id, "active_page_id": self.data["session"]["last_open_page_id"]}

    def word_count(self, page_id: Optional[str] = None) -> int:
        page = self.get_page(page_id)
        if not page:
            return 0
        return sum(len(block.get("content", "").split()) for block in page.get("blocks") or [])

    def total_page_count(self) -> int:
        return len(self.data.get("pages") or [])

    def update_focus_score(self, words_written: int = 0, idle_seconds: int = 0) -> int:
        score = int(self.data["session"].get("focus_score") or 0)
        now = self._current_timestamp()

        if idle_seconds >= 300:
            score = max(0, score - min(25, max(10, idle_seconds // 60)))
        else:
            score = min(100, score + max(1, round(words_written / 80)))

        self.data["session"]["focus_score"] = score
        self.data["session"]["last_activity_at"] = now
        self._dirty = True
        self.save(force=True)
        return score

    def get_focus_score(self) -> int:
        return int(self.data["session"].get("focus_score") or 0)

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def focus_metrics(self, page_id: Optional[str] = None) -> Dict:
        page = self.get_page(page_id)
        if not page:
            return {
                "score": 0,
                "attention_seconds": 0,
                "words": 0,
                "words_per_second": 0.0,
            }

        words = self.word_count(page["id"])
        created_at = self._parse_timestamp(page.get("created_at"))
        updated_at = self._parse_timestamp(page.get("updated_at")) or datetime.now(timezone.utc)
        if not created_at:
            created_at = updated_at

        elapsed_seconds = max(1, int((updated_at - created_at).total_seconds()))
        words_per_second = words / elapsed_seconds
        words_per_minute = words_per_second * 60

        volume_score = min(45, words / 8)
        pace_score = min(35, words_per_minute * 2)
        attention_score = min(20, elapsed_seconds / 180)
        score = max(0, min(100, round(volume_score + pace_score + attention_score)))

        self.data["session"]["focus_score"] = score
        self._dirty = True
        self.save(force=True)
        return {
            "score": score,
            "attention_seconds": elapsed_seconds,
            "words": words,
            "words_per_second": words_per_second,
        }

    def set_theme(self, theme: str) -> Dict:
        self.data["settings"]["theme"] = theme
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def set_font_size(self, font_size: int) -> Dict:
        self.data["settings"]["font_size"] = font_size
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def set_font_family(self, font_family: str) -> Dict:
        self.data["settings"]["font_family"] = font_family
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def set_autosave_interval(self, interval_sec: int) -> Dict:
        self.data["settings"]["autosave_interval_sec"] = max(10, int(interval_sec))
        self._autosave_interval = self.data["settings"]["autosave_interval_sec"]
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def set_api_key(self, api_key: str) -> Dict:
        self.data["settings"]["ai_api_key"] = api_key
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def set_ai_provider(self, provider: str) -> Dict:
        provider = provider.lower()
        if provider not in {"openai", "anthropic", "nvidia"}:
            raise ValueError("Provider must be 'openai', 'anthropic', or 'nvidia'")
        self.data["settings"]["ai_provider"] = provider
        self._dirty = True
        self.save(force=True)
        return self.data["settings"]

    def add_ai_context_page(self, page_id: str) -> List[str]:
        if not self.get_page(page_id):
            raise KeyError(f"Page '{page_id}' not found")

        context_pages = self.data["session"].get("ai_context_page_ids") or []
        if page_id not in context_pages:
            context_pages.append(page_id)
        if len(context_pages) > 3:
            context_pages = context_pages[-3:]
        self.data["session"]["ai_context_page_ids"] = context_pages
        self._dirty = True
        self.save(force=True)
        return context_pages

    def remove_ai_context_page(self, page_id: str) -> List[str]:
        context_pages = [pid for pid in (self.data["session"].get("ai_context_page_ids") or []) if pid != page_id]
        self.data["session"]["ai_context_page_ids"] = context_pages
        self._dirty = True
        self.save(force=True)
        return context_pages

    def get_ai_context_pages(self) -> List[Dict]:
        selected = []
        for page in self.data["pages"]:
            if page["id"] in (self.data["session"].get("ai_context_page_ids") or []):
                selected.append(page)
        return selected

    def _provider_headers(self, provider: str, api_key: str) -> Dict[str, str]:
        if provider in {"openai", "nvidia"}:
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        if provider == "anthropic":
            return {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }
        raise ValueError(f"Unsupported provider: {provider}")

    def _provider_endpoint(self, provider: str) -> str:
        if provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        if provider == "nvidia":
            return "https://integrate.api.nvidia.com/v1/chat/completions"
        if provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        raise ValueError(f"Unsupported provider: {provider}")

    def _provider_payload(self, provider: str, messages: List[Dict], system_prompt: Optional[str] = None) -> Dict:
        if provider in {"openai", "nvidia"}:
            payload = {
                "model": "gpt-4o-mini" if provider == "openai" else "meta/llama-3.1-70b-instruct",
                "messages": messages,
                "temperature": 0.2,
            }
            if system_prompt:
                payload["messages"] = [{"role": "system", "content": system_prompt}] + messages
            return payload

        if provider == "anthropic":
            system_parts = [system_prompt] if system_prompt else []
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_parts.append(msg["content"])
                else:
                    anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 800,
                "messages": anthropic_messages,
            }
            if system_parts:
                payload["system"] = "\n\n".join(system_parts)
            return payload

        raise ValueError(f"Unsupported provider: {provider}")

    def _extract_response(self, provider: str, response_data: Dict) -> str:
        if provider in {"openai", "nvidia"}:
            choices = response_data.get("choices") or []
            if not choices:
                raise RuntimeError(f"No response content from {provider.title()}")
            message = choices[0].get("message") or {}
            content = message.get("content") or ""
            return content.strip()

        if provider == "anthropic":
            content_blocks = response_data.get("content") or []
            if not content_blocks:
                raise RuntimeError("No response content from Anthropic")
            text_parts = []
            for block in content_blocks:
                if isinstance(block, dict):
                    text = block.get("text")
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts).strip()

        raise RuntimeError(f"Unsupported provider response parsing: {provider}")

    def request_ai(self, messages: List[Dict], system_prompt: Optional[str] = None) -> Dict:
        provider = (self.data["settings"].get("ai_provider") or "openai").lower()
        env_keys = {
            "anthropic": "ANTHROPIC_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        api_key = self.data["settings"].get("ai_api_key") or os.environ.get(env_keys.get(provider, "OPENAI_API_KEY"), "")
        if api_key.startswith("nvapi-"):
            provider = "nvidia"
        if not api_key:
            raise RuntimeError(f"Enter your {provider.title()} API key in Settings to enable AI features.")

        endpoint = self._provider_endpoint(provider)
        headers = self._provider_headers(provider, api_key)
        payload = self._provider_payload(provider, messages, system_prompt=system_prompt)

        request_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(endpoint, data=request_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=AI_REQUEST_TIMEOUT_SEC) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"AI request failed: {exc.code} {exc.reason}. {body}")
        except (TimeoutError, socket.timeout):
            raise RuntimeError("AI request timed out. The model took too long to respond; please try again.")
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, socket.timeout):
                raise RuntimeError("AI request timed out. The model took too long to respond; please try again.")
            raise RuntimeError(f"AI request failed due to network error: {exc.reason}")

        assistant_text = self._extract_response(provider, response_data)
        return {
            "provider": provider,
            "content": assistant_text,
            "raw": response_data,
        }

    def chat_history(self) -> List[Dict]:
        history = self.data["session"].get("chat_history") or []
        return list(history)

    def append_chat(self, role: str, content: str) -> List[Dict]:
        history = self.data["session"].get("chat_history") or []
        history.append({"role": role, "content": content, "timestamp": self._current_timestamp()})
        self.data["session"]["chat_history"] = history
        self._dirty = True
        self.save(force=True)
        return history

    def clear_chat_history(self) -> List[Dict]:
        self.data["session"]["chat_history"] = []
        self._dirty = True
        self.save(force=True)
        return []

    def summarize_page(self, page_id: Optional[str] = None) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError("No active page found")

        page_text = "\n".join(block.get("content", "") for block in page.get("blocks") or [])
        prompt = "Summarise the following in 3–5 sentences."
        messages = [{"role": "user", "content": f"{prompt}\n\n{page_text}"}]
        response = self.request_ai(messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "summary", "content": assistant_message}

    def fix_grammar(self, selection: str, page_id: Optional[str] = None) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError("No active page found")

        source_text = selection.strip() or "\n".join(block.get("content", "") for block in page.get("blocks") or [])
        prompt = "Fix all grammar and spelling errors. Return only the corrected text."
        messages = [{"role": "user", "content": f"{prompt}\n\n{source_text}"}]
        response = self.request_ai(messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "grammar_fix", "content": assistant_message, "source": source_text}

    def expand_text(self, selection: str) -> Dict:
        prompt = "Expand the following paragraph to approximately twice its length while preserving the original tone and meaning."
        messages = [{"role": "user", "content": f"{prompt}\n\n{selection}"}]
        response = self.request_ai(messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "expand", "content": assistant_message}

    def translate_text(self, selection: str, language: str) -> Dict:
        prompt = f"Translate the following to {language}."
        messages = [{"role": "user", "content": f"{prompt}\n\n{selection}"}]
        response = self.request_ai(messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "translate", "language": language, "content": assistant_message}

    def slash_command_options(self) -> List[Dict]:
        return [
            {"label": "Heading", "type": "heading", "template": "## Heading"},
            {"label": "Title", "type": "title", "template": "# Title"},
            {"label": "Paragraph", "type": "paragraph", "template": ""},
            {"label": "Bold", "type": "bold", "template": "****"},
            {"label": "Summarize", "type": "summarize", "template": None},
            {"label": "Code", "type": "code", "template": "```python\n\n```"},
        ]

    def run_slash_command(self, command_type: str, page_id: Optional[str] = None) -> Dict:
        commands = {option["type"]: option for option in self.slash_command_options()}
        if command_type not in commands:
            raise ValueError(f"Unsupported slash command: {command_type}")

        if command_type == "summarize":
            return self.summarize_page(page_id)

        option = commands[command_type]
        return {
            "type": command_type,
            "label": option["label"],
            "content": option.get("template") or "",
        }

    def ask_question(self, question: str, page_id: Optional[str] = None, persist_user: bool = True) -> Dict:
        page = self.get_page(page_id)
        if not page:
            raise KeyError("No active page found")

        page_context = "\n".join(block.get("content", "") for block in page.get("blocks") or [])
        extra_context_pages = [
            context_page for context_page in self.get_ai_context_pages()
            if context_page["id"] != page["id"]
        ]
        history = self.chat_history()
        context_messages = [
            {"role": "system", "content": "You are assisting with writing. Use the active page context when helpful."},
        ]
        if page_context:
            context_messages.append({"role": "system", "content": f"Active page context:\n{page_context}"})
        for context_page in extra_context_pages:
            context_text = "\n".join(block.get("content", "") for block in context_page.get("blocks") or [])
            if context_text:
                context_messages.append({
                    "role": "system",
                    "content": f"Additional context from '{context_page.get('title', 'Untitled')}':\n{context_text}",
                })

        for item in history[-10:]:
            context_messages.append({"role": item["role"], "content": item["content"]})

        context_messages.append({"role": "user", "content": question})
        if persist_user:
            self.append_chat("user", question)
        response = self.request_ai(context_messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "chat", "question": question, "content": assistant_message}

    def ask_pdf_question(self, question: str, pdf_text: str) -> Dict:
        if not pdf_text.strip():
            raise ValueError("The selected PDF has no extractable text.")

        messages = [
            {
                "role": "system",
                "content": "Use the provided PDF text to follow the user's instruction. Return only the final content.",
            },
            {
                "role": "user",
                "content": f"PDF text:\n{pdf_text}\n\nUser instruction:\n{question}",
            },
        ]
        response = self.request_ai(messages)
        assistant_message = response["content"]
        self.append_chat("assistant", assistant_message)
        return {"type": "pdf", "question": question, "content": assistant_message}

    def slash_menu_options(self) -> List[Dict]:
        return self.slash_command_options()
        return [
            {"icon": "T", "label": "Text", "description": "Plain paragraph block", "shortcut": None, "type": "paragraph"},
            {"icon": "H1", "label": "Heading 1", "description": "Large section heading", "shortcut": "Ctrl+Alt+1", "type": "h1"},
            {"icon": "H2", "label": "Heading 2", "description": "Medium section heading", "shortcut": "Ctrl+Alt+2", "type": "h2"},
            {"icon": "≡", "label": "Bullet List", "description": "Unordered bulleted list", "shortcut": None, "type": "bullet"},
            {"icon": "■", "label": "To-do List", "description": "Checkbox task list", "shortcut": None, "type": "todo"},
            {"icon": "❝", "label": "Quote", "description": "Indented quote with accent bar", "shortcut": None, "type": "quote"},
            {"icon": "—", "label": "Divider", "description": "Horizontal rule between blocks", "shortcut": None, "type": "divider"},
            {"icon": "✦", "label": "AI Prompt", "description": "Inline AI generation block", "shortcut": None, "type": "ai_prompt"},
            {"icon": "</>", "label": "Code Block", "description": "Monospace code area", "shortcut": None, "type": "code"},
        ]

    def start_autosave(self) -> None:
        if self._autosave_thread and self._autosave_thread.is_alive():
            return

        self._stop_autosave.clear()

        def runner() -> None:
            while not self._stop_autosave.wait(self._autosave_interval):
                self.save(force=True)

        self._autosave_thread = threading.Thread(target=runner, daemon=True)
        self._autosave_thread.start()

    def stop_autosave(self) -> None:
        self._stop_autosave.set()
        if self._autosave_thread:
            self._autosave_thread.join(timeout=1)


backend = WriteBackend()


__all__ = [
    "WriteBackend",
    "backend",
    "Block",
]
