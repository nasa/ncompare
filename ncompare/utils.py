"""Helper utilities."""
from pathlib import Path
from typing import Union


def ensure_valid_path_exists(should_be_path: Union[str, Path]) -> Path:
    """Convert input to a pathlib.Path and check that the resulting filepath exists."""
    if isinstance(should_be_path, (str, Path)):
        path_obj = Path(should_be_path)
        if path_obj.exists():
            return path_obj
        raise FileNotFoundError(f"Expected file does not exist: {path_obj}")
    raise TypeError(f"Unexpected type for something that should be convertible to a Path: {type(should_be_path)}")


def ensure_valid_path_with_suffix(should_be_path: Union[str, Path],
                                  suffix: str = None) -> Path:
    """Coerce input to a pathlib.Path with given suffix."""
    wrong_type_msg = "Unexpected type for something that should be convertable to a Path: "

    if isinstance(should_be_path, str):
        path_obj = Path(should_be_path)
    elif isinstance(should_be_path, Path):
        path_obj = should_be_path
    else:
        raise TypeError(wrong_type_msg + str(type(should_be_path)))

    return path_obj.with_suffix(suffix)

def coerce_to_str(some_object: Union[str, int, tuple]) -> str:
    """Ensure the type is a string."""
    if isinstance(some_object, (str, int, tuple)):
        return str(some_object)

    raise TypeError(f"Unable to coerce value to str. Unexpected type <{type(some_object)}>.")
