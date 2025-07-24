import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import uuid

# ------------------------
# Conexión con Supabase
# ------------------------

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Registro de Peso", layout="centered")

# ======= Funciones Supabase =======

def guardar_peso(peso):
    supabase.table("peso").insert({
        "fecha": datetime.now(timezone.utc).isoformat(),
        "peso": peso
    }).execute()

def leer_pesos():
    response = supabase.table("peso").select("*").order("fecha", desc=True).execute()
    return pd.DataFrame(response.data)

def guardar_objetivo(peso_objetivo, fecha_objetivo):
    data = {
        "peso_objetivo": peso_objetivo,
        "fecha_objetivo": datetime.combine(fecha_objetivo, time()).isoformat()
    }
    supabase.table("objetivo").insert(data).execute()

def leer_objetivo():
    response = supabase.table("objetivo").select("*").order("id", desc=True).limit(1).execute()
    if response.data:
        return response.data[0]
    return None

# ======= App Streamlit =======

st.title("🧍 Registro de peso")

menu = st.sidebar.selectbox("Menú", ["Registrar peso", "Actualizar objetivo", "Borrar registros"])

# ======= Registrar peso =======
if menu == "Registrar peso":
    if "mostrar_confirmacion" not in st.session_state:
        st.session_state["mostrar_confirmacion"] = False
        st.session_state["peso_temporal"] = None

    df = leer_pesos()
    objetivo = leer_objetivo()

    if objetivo:
        peso_obj = objetivo["peso_objetivo"]
        fecha_obj = pd.to_datetime(objetivo["fecha_objetivo"])
        dias_restantes = (fecha_obj - datetime.now(timezone.utc)).days
        peso_actual = df["peso"].iloc[0] if not df.empty else None

        if peso_actual is not None:
            st.markdown(f"""
            **🎯 Objetivo:** {peso_obj:.1f} kg  
            **📅 Fecha límite:** {fecha_obj.strftime('%d/%m/%Y')}  
            **⏳ Días restantes:** {dias_restantes}  
            **⚖️ Diferencia de peso:** {peso_actual - peso_obj:.1f} kg
            """)

            if dias_restantes < 0 and peso_actual < peso_obj:
                st.error("⛔ No ha alcanzado el objetivo, establezca uno nuevo.")
            elif peso_actual >= peso_obj and dias_restantes >= 0:
                st.success(f"🎉 ¡Enhorabuena! Alcanzaste tu objetivo {abs(dias_restantes)} días antes. Establece uno nuevo.")

    if not st.session_state["mostrar_confirmacion"]:
        nuevo_peso = st.number_input("Introduce tu peso (kg)", min_value=30.0, max_value=200.0, step=0.1)
        if st.button("Guardar peso"):
            st.session_state["peso_temporal"] = nuevo_peso
            st.session_state["mostrar_confirmacion"] = True
    else:
        st.info(f"¿Es correcto el peso {st.session_state['peso_temporal']:.1f} kg?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, confirmar"):
                guardar_peso(st.session_state["peso_temporal"])
                st.success("Peso guardado correctamente.")
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None
                st.rerun()
        with col2:
            if st.button("❌ No, volver"):
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None

    st.subheader("📊 Histórico de peso")
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
        st.line_chart(df.set_index("fecha")["peso"])
        st.dataframe(df[["fecha", "peso"]])

# ======= Actualizar objetivo =======
elif menu == "Actualizar objetivo":
    st.subheader("🎯 Nuevo objetivo")
    peso_objetivo = st.number_input("Peso objetivo (kg)", min_value=30.0, max_value=200.0, step=0.1)
    fecha_objetivo = st.date_input("Fecha para alcanzar el objetivo")
    if st.button("Guardar objetivo"):
        guardar_objetivo(peso_objetivo, fecha_objetivo)
        st.success("🎯 Objetivo actualizado correctamente.")
        st.rerun()

# ======= Borrar registros =======
elif menu == "Borrar registros":
    st.subheader("🗑️ Borrar todos los registros")
    if st.button("Eliminar todo"):
        supabase.table("peso").delete().neq("id", 0).execute()
        supabase.table("objetivo").delete().neq("id", 0).execute()
        st.success("Registros eliminados correctamente.")
        st.rerun()


