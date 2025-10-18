
import json
from pathlib import Path
import gettext

CONFIG_FILE = Path("config.json")
LOCALE_DIR = Path(__file__).parent / "locale"

DEFAULT_CONFIG = {
    "favorites": [],
    "theme": "dark"
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

def setup_gettext():
    gettext.bindtextdomain("messages", LOCALE_DIR)
    gettext.textdomain("messages")
    return gettext.gettext

_ = setup_gettext()
