import os

SOURCE_EXT = ".iol"
TOKEN_EXT = ".tkn"


class FileIOError(Exception):
    pass


def is_source_file(path: str) -> bool:
    return path.lower().endswith(SOURCE_EXT)


def load_source(path: str) -> str:
    if not is_source_file(path):
        raise FileIOError(f"Not a {SOURCE_EXT} file: {path}")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            return f.read()
    except OSError as e:
        raise FileIOError(f"Could not open {path}: {e}") from e


def save_source(path: str, source: str) -> str:
    if not is_source_file(path):
        path += SOURCE_EXT
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(source)
    except OSError as e:
        raise FileIOError(f"Could not save {path}: {e}") from e
    return path


def token_path_for(source_path: str) -> str:
    base, _ = os.path.splitext(source_path)
    return base + TOKEN_EXT


def save_tokens(path: str, content: str) -> str:
    if not path.lower().endswith(TOKEN_EXT):
        path += TOKEN_EXT
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        raise FileIOError(f"Could not save {path}: {e}") from e
    return path


def load_tokens(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise FileIOError(f"Could not open {path}: {e}") from e
