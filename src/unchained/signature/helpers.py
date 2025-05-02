from typing import Optional, Union, get_args, get_origin


def is_optional_annotation(annotation):
    """
    Determine if a type annotation represents an optional type
    (either Optional[T] or T | None).

    Args:
        annotation: The type annotation to check

    Returns:
        bool: True if the annotation is optional, False otherwise
    """
    if annotation is None:
        return False

    origin = get_origin(annotation)

    if origin is Union:
        args = get_args(annotation)
        return type(None) in args

    if origin is Optional:
        return True

    return False


def get_optional_annotation(annotation):
    """
    Extract the underlying type from an optional type annotation.
    If the annotation is Optional[T] or T | None, returns T.

    Args:
        annotation: The type annotation to check

    Returns:
        The underlying type

    Raises:
        TypeError: If the annotation is not an optional type
    """
    if not is_optional_annotation(annotation):
        raise TypeError(f"Type {annotation} is not an optional type")

    args = get_args(annotation)

    non_none_types = [arg for arg in args if arg is not type(None)]

    if len(non_none_types) == 1:
        return non_none_types[0]
    elif len(non_none_types) > 1:
        return Union[tuple(non_none_types)]
    raise ValueError(f"Type {annotation} is not an optional type or is not handled")
