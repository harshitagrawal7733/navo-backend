from pathlib import Path
import yaml

def load_config():
    base_path = Path(__file__).resolve().parent  # Directory where this script is located
    path = base_path / "config.yaml"             # ✅ Correct path composition
    print("Looking for config at:", path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {path}")
    
    with open(path, "r") as file:
        config = yaml.safe_load(file)
        env = config.get("env", "local")
        return config.get(env, {})  # Return only env-specific section

config = load_config()
BASE_URL = config["server"]["base_url"]
