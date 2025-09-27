"""Validaciones sencillas para entradas de usuario."""
from __future__ import annotations

import datetime as _dt
from typing import Iterable


class ValidationError(ValueError):
    """Error para entradas inválidas."""


def require_non_empty(value: str, field: str) -> str:
    if not value.strip():
        raise ValidationError(f"El campo '{field}' no puede estar vacío")
    return value.strip()


def require_in_options(value: str, options: Iterable[str], field: str) -> str:
    normalized = value.strip().upper()
    valid = {option.upper() for option in options}
    if normalized not in valid:
        raise ValidationError(
            f"El campo '{field}' debe ser uno de: {', '.join(sorted(valid))}"
        )
    return normalized


def parse_date(value: str, field: str) -> _dt.date:
    try:
        return _dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(
            f"El campo '{field}' debe tener el formato AAAA-MM-DD"
        ) from exc
