"""Helper utilities."""
from pathlib import Path
from typing import Union


def ensure_valid_path_exists(should_be_path: Union[str, Path]) -> Path:
    """Convert input to a pathlib.Path and check that the resulting filepath exists."""
    fails_to_exist_msg = "Expected file does not exist: "
    wrong_type_msg = "Unexpected type for something that should be convertable to a Path: "

    def _convert_to_path_obj(x):
        path_obj = Path(x)
        if path_obj.exists():
            return path_obj
        else:
            raise FileNotFoundError(fails_to_exist_msg + str(should_be_path))

    if isinstance(should_be_path, str):
        return _convert_to_path_obj(should_be_path)
    elif isinstance(should_be_path, Path):
        if should_be_path.exists():
            return should_be_path
        else:
            raise FileNotFoundError(fails_to_exist_msg + str(should_be_path))

    else:
        raise TypeError(wrong_type_msg + str(type(should_be_path)))

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

def coerce_to_str(x: Union[str, int, tuple]):
    """Ensure the type is a string."""
    if isinstance(x, str):
        return x
    elif isinstance(x, int):
        return str(x)
    elif isinstance(x, tuple):
        return str(x)
    else:
        raise TypeError("Unable to coerce value to str. Unexpected type <%s>.", type(x))
