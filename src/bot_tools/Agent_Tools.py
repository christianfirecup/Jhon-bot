from agents import function_tool, RunContextWrapper
from typing_extensions import Any
from pathlib import Path
import shutil, json

@function_tool
def move_files(
    ctx: RunContextWrapper[Any],
    files: list[str],
    destination: str,
    copy: bool = True,
    overwrite: bool = False,
) -> str:
    """
    Move/copy files ONLY if there are exactly 20 unique, existing files.
    Otherwise, do nothing (no-op) and return a JSON summary explaining why.
    """
    # Normalize & dedupe while preserving order
    normalized = [str(Path(p)) for p in files]
    seen, unique = set(), []
    for p in normalized:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    # Validate existence
    missing = [p for p in unique if not Path(p).is_file()]
    provided_count = len(files)
    unique_count = len(unique)
    valid = [p for p in unique if Path(p).is_file()]
    valid_count = len(valid)

    # HARD GUARD: require exactly 20 valid files
    if not (provided_count == 20 and unique_count == 20 and valid_count == 20):
        return json.dumps({
            "noop": True,
            "reason": "Requires exactly 20 unique, existing files.",
            "provided_count": provided_count,
            "unique_count": unique_count,
            "valid_count": valid_count,
            "missing": missing,
        })

    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    op = shutil.copy2 if copy else shutil.move
    moved = []

    for path in valid:
        p = Path(path)
        target = dest / p.name
        if not overwrite:
            i = 1
            while target.exists():
                target = dest / f"{p.stem}-{i}{p.suffix}"
                i += 1
        op(str(p), str(target))
        moved.append(str(target))

    return json.dumps({
        "noop": False,
        "count": len(moved),
        "dest": str(dest),
        "moved": moved
    })
