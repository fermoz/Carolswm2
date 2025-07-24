# Requiere: streamlit, supabase, pandas, python-dotenv
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import os

# --------------------
# Configuración
# --------------------
st.set_page_config(page_title="Carol's Curve")

# Cargar claves desde secrets.toml o entorno
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --------------------
# Guardar peso actual
# --------------------
def guardar_peso(peso):
    data = {"peso": peso}
    response = supabase.table("peso").insert(data).execute()
    if hasattr(response, "error") and response.error:
        st.error(f"❌ Error al guardar: {response.error}")

# ------------------------
# Leer historial de pesos
# ------------------------
def leer_pesos():
    response = supabase.table("peso").select("*").order("created_at", desc=False).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize("UTC")
    return df

# ------------------------
# Guardar objetivo
# ------------------------
def guardar_objetivo(peso_objetivo, fecha_objetivo):
    supabase.table("objetivo").insert({
        "peso_objetivo": peso_objetivo,
        "fecha_objetivo": fecha_objetivo.isoformat()
    }).execute()

# ------------------------
# Leer último objetivo
# ------------------------
def leer_ultimo_objetivo():
    response = supabase.table("objetivo").select("*").order("created_at", desc=True).limit(1).execute()
    data = response.data
    return data[0] if data else None

# --------------------
# Interfaz Streamlit
# --------------------
st.title("💪 Carol's Curve")
menu = st.sidebar.radio("Menú", ("Registrar peso", "Actualizar objetivo", "Borrar registros"))

# ------------------------
# Registro de peso
# ------------------------
# Inicializar estado si no existe
if "mostrar_confirmacion" not in st.session_state:
    st.session_state["mostrar_confirmacion"] = False
if "peso_temporal" not in st.session_state:
    st.session_state["peso_temporal"] = None

# ------------------------
# Registro de peso
# ------------------------

elif menu == "📥 Registrar peso":
    st.subheader("Registrar nuevo peso")

    # Solo mostramos el input si no estamos confirmando
    if not st.session_state["mostrar_confirmacion"]:
        nuevo_peso = st.number_input("Introduce tu peso en kg", min_value=30.0, max_value=200.0, step=0.1)
        if st.button("Guardar peso"):
            st.session_state["peso_temporal"] = nuevo_peso
            st.session_state["mostrar_confirmacion"] = True

    # Confirmación del peso
    if st.session_state["mostrar_confirmacion"]:
        peso_confirmar = st.session_state["peso_temporal"]
        st.info(f"¿Es correcto el peso {peso_confirmar:.1f} kg?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, es correcto"):
                guardar_peso(peso_confirmar)
                st.success("Peso guardado correctamente.")
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None
                st.experimental_rerun()  # Refresca la app para que aparezca el historial actualizado
        with col2:
            if st.button("❌ No, volver"):
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None


# ====================
# Actualizar objetivo
# ====================
elif menu == "Actualizar objetivo":
    st.subheader("🎯 Establecer nuevo objetivo")
    nuevo_peso = st.number_input("Peso objetivo (kg)", min_value=30.0, max_value=200.0, step=0.1)
    nueva_fecha = st.date_input("Fecha para alcanzar el objetivo")
    if st.button("Guardar nuevo objetivo"):
        guardar_objetivo(nuevo_peso, datetime.combine(nueva_fecha, datetime.min.time(), tzinfo=timezone.utc))
        st.success("✅ Objetivo guardado correctamente")

# ====================
# Borrar registros
# ====================
elif menu == "Borrar registros":
    st.warning("Función no implementada todavía. ¿Quieres que la añada?")
    if st.button("Guardar nuevo objetivo"):
        guardar_objetivo(nuevo_peso, datetime.combine(nueva_fecha, datetime.min.time(), tzinfo=timezone.utc))

