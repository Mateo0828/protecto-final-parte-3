"""Punto de entrada de la aplicación de consola."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from app import repository
from app import reports
from app.validators import (
    ValidationError,
    parse_date,
    require_in_options,
    require_non_empty,
)

GENDER_OPTIONS = ("MASCULINO", "FEMENINO")
STATUS_OPTIONS = ("ACTIVO", "INACTIVO", "TRASLADADO")
CIVIL_STATUS_OPTIONS = ("SOLTERO", "CASADO", "VIUDO", "UNIÓN LIBRE")


def init_db(_: argparse.Namespace) -> None:
    repository.bootstrap_schema()
    print("Esquema creado correctamente.")


def seed(_: argparse.Namespace) -> None:
    repository.seed_catalogs()
    print("Catálogos cargados.")


def show_cities(_: argparse.Namespace) -> None:
    cities = repository.list_cities()
    print(json.dumps(cities, indent=2, ensure_ascii=False))


def show_pastors(_: argparse.Namespace) -> None:
    pastors = repository.list_pastors()
    print(json.dumps(pastors, indent=2, ensure_ascii=False))


def create_member(args: argparse.Namespace) -> None:
    try:
        gender = require_in_options(args.gender, GENDER_OPTIONS, "género")
        status = require_in_options(args.status, STATUS_OPTIONS, "estado")
        civil_status = (
            require_in_options(args.civil_status, CIVIL_STATUS_OPTIONS, "estado civil")
            if args.civil_status
            else None
        )
        first_name = require_non_empty(args.first_name, "nombre")
        last_name = require_non_empty(args.last_name, "apellido")
        document_number = require_non_empty(args.document_number, "número de documento")

        payload: Dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "status": status,
            "document_number": document_number,
            "document_type_id": args.document_type_id,
            "city_id": args.city_id,
            "pastor_id": args.pastor_id,
        }

        if args.birth_date:
            payload["birth_date"] = parse_date(args.birth_date, "fecha de nacimiento")
        if args.baptized_date:
            payload["baptized_date"] = parse_date(args.baptized_date, "fecha de bautismo")
        if civil_status:
            payload["civil_status"] = civil_status
        if args.address:
            payload["address"] = args.address
        if args.phone:
            payload["phone"] = args.phone
        if args.email:
            payload["email"] = args.email

        member_id = repository.create_member(payload)
        print(f"Miembro creado con ID {member_id}")
    except ValidationError as error:
        print(f"Error de validación: {error}")
        sys.exit(2)


def update_member(args: argparse.Namespace) -> None:
    updates: Dict[str, Any] = {}
    if args.gender:
        updates["gender"] = require_in_options(args.gender, GENDER_OPTIONS, "género")
    if args.status:
        updates["status"] = require_in_options(args.status, STATUS_OPTIONS, "estado")
    if args.civil_status:
        updates["civil_status"] = require_in_options(
            args.civil_status, CIVIL_STATUS_OPTIONS, "estado civil"
        )
    if args.address:
        updates["address"] = args.address
    if args.phone:
        updates["phone"] = args.phone
    if args.email:
        updates["email"] = args.email
    if args.pastor_id:
        updates["pastor_id"] = args.pastor_id
    if args.city_id:
        updates["city_id"] = args.city_id

    if args.baptized_date:
        updates["baptized_date"] = parse_date(args.baptized_date, "fecha de bautismo")
    if args.birth_date:
        updates["birth_date"] = parse_date(args.birth_date, "fecha de nacimiento")

    repository.update_member(args.member_id, updates)
    print("Miembro actualizado correctamente.")


def list_members(_: argparse.Namespace) -> None:
    members = repository.list_members()
    print(json.dumps(members, indent=2, ensure_ascii=False))


def show_summary(_: argparse.Namespace) -> None:
    summary = repository.demographic_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def generate_certificate(args: argparse.Namespace) -> None:
    certificate = reports.build_certificate(args.member_id)
    print(certificate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sistema de gestión de membresías para la IPUC Caunces",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Crear las tablas necesarias").set_defaults(
        func=init_db
    )
    subparsers.add_parser("seed", help="Cargar catálogos iniciales").set_defaults(
        func=seed
    )
    subparsers.add_parser("list-cities", help="Mostrar las ciudades registradas").set_defaults(
        func=show_cities
    )
    subparsers.add_parser("list-pastors", help="Mostrar los pastores registrados").set_defaults(
        func=show_pastors
    )

    create_parser = subparsers.add_parser("add-member", help="Crear un nuevo miembro")
    create_parser.set_defaults(func=create_member)
    create_parser.add_argument("--first-name", required=True)
    create_parser.add_argument("--last-name", required=True)
    create_parser.add_argument("--gender", required=True)
    create_parser.add_argument("--status", default="ACTIVO")
    create_parser.add_argument("--document-type-id", type=int, required=True)
    create_parser.add_argument("--document-number", required=True)
    create_parser.add_argument("--city-id", type=int, required=True)
    create_parser.add_argument("--pastor-id", type=int, required=True)
    create_parser.add_argument("--civil-status")
    create_parser.add_argument("--birth-date")
    create_parser.add_argument("--baptized-date")
    create_parser.add_argument("--address")
    create_parser.add_argument("--phone")
    create_parser.add_argument("--email")

    update_parser = subparsers.add_parser("update-member", help="Actualizar datos de un miembro")
    update_parser.set_defaults(func=update_member)
    update_parser.add_argument("member_id", type=int)
    update_parser.add_argument("--gender")
    update_parser.add_argument("--status")
    update_parser.add_argument("--civil-status")
    update_parser.add_argument("--birth-date")
    update_parser.add_argument("--baptized-date")
    update_parser.add_argument("--address")
    update_parser.add_argument("--phone")
    update_parser.add_argument("--email")
    update_parser.add_argument("--pastor-id", type=int)
    update_parser.add_argument("--city-id", type=int)

    subparsers.add_parser("list-members", help="Listar miembros").set_defaults(
        func=list_members
    )
    subparsers.add_parser(
        "summary", help="Mostrar resumen demográfico"
    ).set_defaults(func=show_summary)

    certificate_parser = subparsers.add_parser(
        "certificate", help="Generar certificado de membresía"
    )
    certificate_parser.set_defaults(func=generate_certificate)
    certificate_parser.add_argument("member_id", type=int)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
