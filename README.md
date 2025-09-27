# Full MVP (serial/int) — Backend FastAPI + Frontend Streamlit

## Estructura
- `db.sql` — esquema alineado al diagrama (serial/int) + seed
- `queries.sql` — consultas para exposición
- `backend/main.py` — API simple (FastAPI + psycopg2)
- `frontend/app.py` — UI simple (Streamlit) consumiendo la API
- `.env.example` — variables de entorno
- `requirements.txt`

## 1) PostgreSQL 17 y pgAdmin
1. Crea la BD y usuario (o usa existentes).
2. En **pgAdmin**, conecta a tu BD y ejecuta **db.sql** para crear tablas/vistas y cargar datos de ejemplo.

## 2) Preparar entorno Python (VSCode)
```bash
cd congregacion_full_mvp_serial
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # ajusta credenciales y API_BASE si cambias el puerto
```

## 3) Levantar backend
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Probar en navegador: `http://127.0.0.1:8000/health`

## 4) Levantar frontend
En otra terminal (con el mismo venv activo):
```bash
streamlit run frontend/app.py
```
La app llamará al API en `API_BASE` (por defecto `http://127.0.0.1:8000`).

## 5) Qué mostrar en la exposición
- **pgAdmin** ejecutando algunas consultas de `queries.sql`.
- **Frontend**: buscar por ciudad, crear y editar miembro, ver estadística por congregación.
- **Backend**: endpoints `/miembros/*`, `/estadistica`, todo parametrizado y contra PostgreSQL real.

¡Listo!
