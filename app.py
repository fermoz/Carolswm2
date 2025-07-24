import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta, timezone
import json

# Configurar conexión desde secrets
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("📊 Registro de Peso Corporal")

# Función: Guardar nuevo peso
def guardar_peso(peso):
    fecha = datetime.now(timezone.utc).isoformat()
    data = {"peso": peso, "fecha": fecha}
    supabase.table("registro_peso").insert(data).execute()

# Función: Leer registros
def leer_registros():
    response = supabase.table("registro_peso").select("*").order("fecha", desc=True).execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["fecha", "peso"])

# Función: Borrar todos los registros
def borrar_registros():
    supabase.table("registro_peso").delete().neq("peso", -1).execute()

# Función: Guardar objetivo
def guardar_objetivo(peso_objetivo, fecha_objetivo):
    data = {
        "peso_objetivo": peso_objetivo,
        "fecha_objetivo": fecha_objetivo.isoformat()
    }
    supabase.table("objetivo").delete().neq("peso_objetivo", -1).execute()
    supabase.table("objetivo").insert(data).execute()

# Función: Leer objetivo
def leer_objetivo():
    response = supabase.table("objetivo").select("*").limit(1).execute()
    if response.data:
        obj = response.data[0]
        obj["fecha_objetivo"] = pd.to_datetime(obj["fecha_objetivo"])
        return obj
    return None

# Cargar datos
df = leer_registros()
objetivo = leer_objetivo()

# ====================
# Menú lateral
# ====================
menu = st.sidebar.radio("Menú", ["Registrar peso", "Actualizar objetivo", "Borrar registros"])

# ====================
# Registrar peso
# ====================
if menu == "Registrar peso":
    st.subheader("📝 Registrar nuevo peso")

    if "mostrar_confirmacion" not in st.session_state:
        st.session_state["mostrar_confirmacion"] = False
        st.session_state["peso_temporal"] = None

    if not st.session_state["mostrar_confirmacion"]:
        peso = st.number_input("Introduce tu peso (kg)", min_value=30.0, max_value=300.0, step=0.1, format="%.1f")
        if st.button("💾 Guardar peso"):
            st.session_state["peso_temporal"] = peso
            st.session_state["mostrar_confirmacion"] = True
    else:
        peso_temp = st.session_state["peso_temporal"]
        st.success(f"¿Es correcto el peso {peso_temp:.1f} kg?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, guardar"):
                guardar_peso(peso_temp)
                st.success("Peso guardado correctamente.")
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None
                st.rerun()
        with col2:
            if st.button("❌ No, volver"):
                st.session_state["mostrar_confirmacion"] = False

    # Mostrar registros previos
    if not df.empty:
        st.subheader("📈 Historial")
        st.dataframe(df[["fecha", "peso"]])

    # Mostrar objetivo
    if objetivo:
        peso_obj = objetivo["peso_objetivo"]
        fecha_obj = objetivo["fecha_objetivo"]
        dias_restantes = (fecha_obj - datetime.now()).days
        peso_actual = df["peso"].iloc[0] if not df.empty else None

        if peso_actual is not None:
            diferencia = peso_actual - peso_obj
            st.markdown(f"""
                **🎯 Objetivo:** {peso_obj:.1f} kg  
                **📅 Fecha límite:** {fecha_obj.strftime('%d/%m/%Y')}  
                **⏳ Días restantes:** {dias_restantes}  
                **⚖️ Diferencia de peso:** {diferencia:+.1f} kg
            """)
            if dias_restantes < 0 and peso_actual < peso_obj:
                st.warning("⏰ No ha alcanzado el objetivo. Establezca un nuevo objetivo.")
            elif peso_actual <= peso_obj and dias_restantes >= 0:
                dias_adelanto = abs(dias_restantes)
                st.success(f"🎉 ¡Enhorabuena! Lo has logrado con {dias_adelanto} días de antelación. Establece un nuevo objetivo.")

# ====================
# Actualizar objetivo
# ====================
elif menu == "Actualizar objetivo":
    st.subheader("🎯 Nuevo objetivo")
    peso_objetivo = st.number_input("Peso objetivo (kg)", min_value=30.0, max_value=300.0, step=0.1, format="%.1f")
    fecha_objetivo = st.date_input("Fecha para alcanzar el objetivo")
    if st.button("Guardar objetivo"):
        guardar_objetivo(peso_objetivo, fecha_objetivo)
        st.success("🎯 Objetivo actualizado correctamente.")
        st.rerun()

# ====================
# Borrar registros
# ====================
elif menu == "Borrar registros":
    st.subheader("⚠️ Borrar todo el historial")
    if st.button("🗑️ Confirmar borrado"):
        borrar_registros()
        st.success("Todos los registros han sido eliminados.")
        st.rerun()


