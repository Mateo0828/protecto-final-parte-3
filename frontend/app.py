\
import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Membresías MVP", layout="wide")
st.title("Gestión de Membresías - MVP (Frontend sencillo)")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Salud del API", "Miembros (detalle)", "Filtrar por ciudad", "Crear/Editar miembro", "Estadística"
])

with tab1:
    if st.button("Probar conexión"):
        try:
            r = requests.get(f"{API_BASE}/health", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(e)

with tab2:
    if st.button("Cargar listado completo"):
        r = requests.get(f"{API_BASE}/miembros/detalle")
        st.dataframe(r.json())

with tab3:
    ciudad = st.text_input("Ciudad contiene:", "Mosquera")
    if st.button("Buscar por ciudad"):
        r = requests.get(f"{API_BASE}/miembros/ciudad/{ciudad}")
        st.dataframe(r.json())

with tab4:
    st.subheader("Crear miembro")
    with st.form("crear"):
        nombres = st.text_input("Nombres", "")
        apellidos = st.text_input("Apellidos", "")
        id_congregacion = st.number_input("ID congregación", min_value=1, step=1)
        fecha_nacimiento = st.text_input("Fecha nacimiento (YYYY-MM-DD)", "")
        direccion = st.text_input("Dirección", "")
        telefono = st.text_input("Teléfono", "")
        correo = st.text_input("Correo", "")
        fecha_bautismo = st.text_input("Fecha bautismo (YYYY-MM-DD)", "")
        id_pastor = st.text_input("ID pastor (opcional)", "")
        id_barrio = st.text_input("ID barrio (opcional)", "")
        estado_civil = st.text_input("Estado civil", "")
        ok = st.form_submit_button("Crear")
        if ok:
            payload = {
                "nombres": nombres,
                "apellidos": apellidos,
                "id_congregacion": int(id_congregacion),
                "fecha_nacimiento": fecha_nacimiento or None,
                "direccion": direccion or None,
                "telefono": telefono or None,
                "correo": correo or None,
                "fecha_bautismo": fecha_bautismo or None,
                "id_pastor": int(id_pastor) if id_pastor else None,
                "id_barrio": int(id_barrio) if id_barrio else None,
                "estado_civil": estado_civil or None,
            }
            r = requests.post(f"{API_BASE}/miembros", json=payload)
            st.json(r.json())

    st.subheader("Editar contacto")
    with st.form("editar"):
        id_miembro = st.number_input("ID miembro", min_value=1, step=1)
        telefono = st.text_input("Nuevo teléfono", "")
        correo = st.text_input("Nuevo correo", "")
        direccion = st.text_input("Nueva dirección", "")
        ok2 = st.form_submit_button("Actualizar")
        if ok2:
            payload = {
                "telefono": telefono or None,
                "correo": correo or None,
                "direccion": direccion or None,
            }
            r = requests.patch(f"{API_BASE}/miembros/{int(id_miembro)}", json=payload)
            if r.status_code == 200:
                st.success("Actualizado")
                st.json(r.json())
            else:
                st.error(r.text)

with tab5:
    if st.button("Ver estadística por congregación"):
        r = requests.get(f"{API_BASE}/estadistica")
        st.dataframe(r.json())
