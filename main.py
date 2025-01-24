if __name__ == "__main__":
    print("Welcome to the Pockpocket Project!")

# utils.py
import os
import sys
from pathlib import Path


def add_project_root_to_path():
    """プロジェクトルートディレクトリをsys.pathに追加"""
    # プロジェクトルートを探す（pyproject.tomlまたは.gitがある場所）
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists() or (current / ".git").exists():
            if str(current) not in sys.path:
                sys.path.insert(0, str(current))
            return
        current = current.parent