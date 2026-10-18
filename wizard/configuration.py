"""Provider and saved-configuration rules shared by wizard views, without Qt."""
from copy import deepcopy
import json
from pathlib import Path

PROVIDER_LABELS = {
    "rwkv": "Dual RWKV (Local)",
    "ollama": "Ollama (Local)",
    "codex_cli": "Codex CLI (ChatGPT subscription)",
    "claude_cli": "Claude Code CLI",
    "gemini": "Gemini (Google)",
    "anthropic": "Claude (Anthropic)",
    "llama_cpp": "llama.cpp (Local GGUF)",
}
SECRET_FIELDS = {
    "gemini_api_key": "GEMINI_API_KEY", "anthropic_api_key": "ANTHROPIC_API_KEY",
    "openai_api_key": "OPENAI_API_KEY", "alibaba_api_key": "ALIBABA_API_KEY",
    "telegram_token": "HELIX_TELEGRAM_TOKEN", "discord_token": "HELIX_DISCORD_TOKEN",
    "slack_bot_token": "HELIX_SLACK_BOT_TOKEN", "slack_app_token": "HELIX_SLACK_APP_TOKEN",
    "whatsapp_token": "HELIX_WHATSAPP_TOKEN", "webhook_inbound_secret": "HELIX_WEBHOOK_INBOUND_SECRET",
}


def canonical_provider(provider):
    return {"bicameral_rwkv": "rwkv", "codex": "codex_cli"}.get(provider, provider)


def supported_providers(composition):
    if composition == "mindscape":
        return ("rwkv", "ollama")
    if composition == "helix":
        return tuple(PROVIDER_LABELS)
    raise ValueError("Choose Mindscape or Helix composition")


def select_provider(config, provider, model):
    """Validate before changing configuration; keep all local selectors aligned."""
    result = deepcopy(config)
    provider = canonical_provider(provider)
    composition = result.get("composition", "helix")
    if provider not in supported_providers(composition):
        raise ValueError(f"{provider} is not supported by {composition}; choose a listed runtime provider")
    model = str(model or "").strip()
    if provider == "rwkv" and not model:
        from core.model_paths import default_rwkv_model
        model = result.get("mindscape", {}).get("rwkv_model") or default_rwkv_model()
    if provider in {"ollama", "llama_cpp"} and not model:
        raise ValueError("Choose a local model before continuing")
    result.update(llm_provider=provider, llm_model=model)
    if provider in {"rwkv", "ollama", "llama_cpp"}:
        result.update(local_provider=provider, local_model=model)
    if composition == "mindscape":
        result.update(task_cognition_mode="off", cli_agent_mode=False)
        if provider == "rwkv":
            result.setdefault("mindscape", {})["rwkv_model"] = model
    if provider == "ollama":
        result["ollama_model"] = model
    return result


def load_wizard_config(path, defaults, credentials=None):
    """Copy defaults and preserve legacy composition and private channel values."""
    path = Path(path)
    saved = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(saved, dict):
        raise ValueError("Saved wizard configuration must be a JSON object")
    saved_native = saved.get("mindscape", {})
    if not isinstance(saved_native, dict):
        raise ValueError("Saved mindscape configuration must be a JSON object")
    result = deepcopy(defaults)
    result.update(saved)
    result["mindscape"] = {**deepcopy(defaults.get("mindscape", {})), **saved_native}
    credentials = credentials or {}
    if path.exists() and "composition" not in saved:
        result["composition"] = "helix"
        result["llm_provider"] = saved.get("llm_provider") or saved.get("local_provider") or credentials.get("HELIX_PROVIDER") or "gemini"
        result["llm_model"] = saved.get("llm_model") or saved.get("local_model") or credentials.get("HELIX_MODEL", "")
        result["task_cognition_mode"] = saved.get("task_cognition_mode", "observe")
    for field, variable in SECRET_FIELDS.items():
        if credentials.get(variable):
            result[field] = credentials[variable]
    return result


def bootstrap_command(config, root, executable):
    """Provision the selected composition without rerunning interactive mode selection."""
    root = Path(root)
    command = [executable, str(root / "setup.py"), "--non-interactive", "--composition-only"]
    values = {
        "composition": config.get("composition", "helix"),
        "agent-name": config.get("agent_name", "Helix"), "creator-name": config.get("creator_name") or "User",
        "profile": config.get("bootstrap_profile", "standard"), "personality": config.get("personality", "curious"),
        "archetype": config.get("agent_archetype", "balanced"),
        "primary-channel": config.get("primary_channel", "dashboard"), "data-dir": config.get("data_dir", "data"),
        "provider": canonical_provider(config.get("llm_provider", "rwkv")),
        "model": config.get("llm_model", ""), "local-context-window": config.get("local_context_window", 8192),
    }
    if values["composition"] == "mindscape":
        for field, option in (("package_path", "mightymem-path"), ("rwkv_model", "rwkv-model"),
                              ("home", "agent-home"), ("workspace", "workspace")):
            if config.get("mindscape", {}).get(field):
                values[option] = config["mindscape"][field]
    command.extend(f"--{key}={value}" for key, value in values.items())
    return command
