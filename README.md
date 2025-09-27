# Sistema de Gestión de Membresías – IPUC Caunces

Este repositorio contiene el MVP del sistema de registro y gestión de información para la congregación **Iglesia Pentecostal Unida de Colombia – Sede Caunces**. El objetivo es centralizar los datos de los miembros, permitir su actualización y generar reportes básicos apoyados en PostgreSQL 17.

## Requisitos

- Python 3.11+
- PostgreSQL 17
- Acceso a una base de datos con privilegios de creación de tablas

Instala las dependencias de la aplicación:

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Configura las variables de entorno de conexión. Puedes copiar el archivo `.env.example` y ajustarlo según tu equipo:

```bash
cp .env.example .env
export $(grep -v '^#' .env | xargs)  # Linux/Mac
```

Valores esperados:

- `PENTA_DB_HOST`
- `PENTA_DB_PORT`
- `PENTA_DB_NAME`
- `PENTA_DB_USER`
- `PENTA_DB_PASSWORD`

## Inicialización de la base de datos

1. Ejecuta el comando para crear las tablas:

   ```bash
   python main.py init-db
   ```

2. Carga los catálogos mínimos (tipos de documento, ubicación y pastor inicial):

   ```bash
   python main.py seed
   ```

## Operaciones principales

- **Listar catálogos**

  ```bash
  python main.py list-cities
  python main.py list-pastors
  ```

- **Crear un miembro**

  ```bash
  python main.py add-member \
      --first-name "María" \
      --last-name "Gómez" \
      --gender "Femenino" \
      --document-type-id 1 \
      --document-number "123456789" \
      --city-id 1 \
      --pastor-id 1 \
      --birth-date 1995-06-20 \
      --baptized-date 2010-08-15 \
      --address "Cra 10 # 4-50" \
      --phone "+57 300 111 2233" \
      --email "maria.gomez@example.com"
  ```

- **Actualizar un miembro**

  ```bash
  python main.py update-member 1 --status "Inactivo" --phone "+57 312 000 1122"
  ```

- **Listar miembros registrados**

  ```bash
  python main.py list-members
  ```

- **Resumen demográfico**

  ```bash
  python main.py summary
  ```

- **Generar certificado de membresía**

  ```bash
  python main.py certificate 1
  ```

## Estructura del proyecto

```
.
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── repository.py
│   ├── reports.py
│   └── validators.py
├── main.py
├── requirements.txt
├── README.md
└── .env.example
```

## Notas para la exposición

- Demuestra la inicialización de la BD (`init-db` + `seed`).
- Registra un miembro y actualízalo mostrando el efecto en `list-members`.
- Ejecuta el comando `summary` para evidenciar los reportes solicitados.
- Muestra el certificado generado en consola (`certificate`).

## Licencia

Proyecto académico para la asignatura de Bases de Datos. Uso interno del equipo de trabajo.
