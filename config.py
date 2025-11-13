
import json
from pathlib import Path

CONFIG_FILE = Path("config.json")

DEFAULT_CONFIG = {
    "favorites": [],
    "theme": "dark",
    "live_story": False
}

def load_config() -> dict:
    """Carrega a configuração do arquivo config.json."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        return merged_config
    except json.JSONDecodeError:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    """Salva a configuração no arquivo config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
