"""Generación de reportes y certificados."""
from __future__ import annotations

from datetime import date
from textwrap import dedent
from typing import Dict

from .repository import certificate_payload


def build_certificate(member_id: int) -> str:
    """Genera un certificado de membresía en texto plano."""

    payload: Dict[str, object] = certificate_payload(member_id)
    member = payload["member"]
    history = payload["history"]

    last_log = history[-1]["created_at"].strftime("%Y-%m-%d") if history else "N/A"

    certificate = dedent(
        f"""
        Iglesia Pentecostal Unida de Colombia
        Sede Caunces - Santander de Quilichao

        CERTIFICADO DE MEMBRESÍA

        Se certifica que {member['first_name']} {member['last_name']}, identificado(a) con
        {member['document_type']} No. {member['document_number']}, es miembro en
        estado {member['status']} de la congregación. Su último movimiento en el
        sistema fue registrado el {last_log}.

        Expedido en fecha {date.today():%Y-%m-%d}.
        """
    ).strip()
    return certificate
