import src.bot_backend.bot_tools.Agent_Tools as Tester

import json, time
from pathlib import Path
from datetime import datetime

def _new_run_path(dir_="logs", prefix="twitch_chat", ext=".jsonl") -> Path:
    Path(dir_).mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(dir_) / f"{prefix}_{stamp}{ext}"
    i = 1
    while path.exists():  # extreme edge case: same second or rerun
        path = Path(dir_) / f"{prefix}_{stamp}_{i}{ext}"
        i += 1
    return path
if __name__ == "__main__":
    out_path = _new_run_path()
    with open(out_path, "w", encoding="utf-8") as f:
        for line in Tester.twichchat_grabber():
            f.write(json.dumps({"ts": time.time(), "raw": line}, ensure_ascii=False) + "\n")
            f.flush()