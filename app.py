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

# ------------------------
# Funciones auxiliares
# ------------------------

def guardar_peso(peso):
    data = {"peso": peso}
    response = supabase.table("peso").insert(data).execute()
    return response

def leer_pesos():
    response = supabase.table("peso").select("*").order("created_at", desc=False).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df

def borrar_registros():
    supabase.table("peso").delete().neq("id", 0).execute()
    st.success("Registros borrados correctamente.")

def guardar_objetivo(peso_objetivo, fecha_objetivo):
    supabase.table("objetivo").delete().neq("id", 0).execute()  # Borra anteriores
    data = {
        "id": str(uuid.uuid4()),
        "peso_objetivo": peso_objetivo,
        "fecha_objetivo": fecha_objetivo
    }
    supabase.table("objetivo").insert(data).execute()

def leer_objetivo():
    response = supabase.table("objetivo").select("*").limit(1).execute()
    if response.data:
        return response.data[0]
    return None

# ------------------------
# Interfaz principal
# ------------------------

st.set_page_config(page_title="Carol's curve", layout="centered")
st.title("Carol's curve")

menu = st.sidebar.radio("Menú", ["📥 Registrar peso", "🗑️ Borrar registros", "🎯 Actualizar objetivo"])

# Estado de confirmación de peso
if "mostrar_confirmacion" not in st.session_state:
    st.session_state["mostrar_confirmacion"] = False
if "peso_temporal" not in st.session_state:
    st.session_state["peso_temporal"] = None

# ------------------------
# Registrar peso
# ------------------------

if menu == "📥 Registrar peso":
    st.subheader("Registrar nuevo peso")

    # Mostrar objetivo si existe
    objetivo = leer_objetivo()
    if objetivo:
        peso_obj = objetivo["peso_objetivo"]
        fecha_obj = pd.to_datetime(objetivo["fecha_objetivo"])
        dias_restantes = (fecha_obj - datetime.now(timezone.utc)).days
        peso_actual = leer_pesos()["peso"].iloc[-1] if not leer_pesos().empty else None

        st.markdown(f"""
        **🎯 Objetivo:** {peso_obj:.1f} kg  
        **📅 Fecha límite:** {fecha_obj.strftime('%d/%m/%Y')}  
        **⏳ Días restantes:** {dias_restantes}  
        **⚖️ Diferencia de peso:** {peso_actual - peso_obj:.1f} kg
        """)

        if dias_restantes < 0 and peso_actual < peso_obj:
            st.warning("🚨 No ha alcanzado el objetivo. Establezca un nuevo objetivo.")
        elif peso_actual >= peso_obj:
            st.success(f"🎉 Enhorabuena!!! Lo has alcanzado con {abs(dias_restantes)} días de antelación. Establece un nuevo objetivo.")

    # Input de peso y confirmación
    if not st.session_state["mostrar_confirmacion"]:
        nuevo_peso = st.number_input("Introduce tu peso en kg", min_value=30.0, max_value=200.0, step=0.1)
        if st.button("Guardar peso"):
            st.session_state["peso_temporal"] = nuevo_peso
            st.session_state["mostrar_confirmacion"] = True

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
                st.experimental_rerun()
        with col2:
            if st.button("❌ No, volver"):
                st.session_state["mostrar_confirmacion"] = False
                st.session_state["peso_temporal"] = None

    # Mostrar historial
    df = leer_pesos()
    if not df.empty:
        st.subheader("Historial de peso")
        st.dataframe(df[["created_at", "peso"]].tail(5), use_container_width=True)
        if len(df) >= 2:
            diff = df.iloc[-1]["peso"] - df.iloc[-2]["peso"]
            st.write(f"📉 Diferencia con la última medición: {diff:.1f} kg")

        ultimos_30 = df[df["created_at"] > datetime.now(timezone.utc) - timedelta(days=30)]
        if not ultimos_30.empty:
            media30 = ultimos_30["peso"].mean()
            st.write(f"📊 Diferencia con la media de los últimos 30 días: {df.iloc[-1]['peso'] - media30:.1f} kg")

# ------------------------
# Borrar registros
# ------------------------

elif menu == "🗑️ Borrar registros":
    st.subheader("Borrar todos los registros de peso")
    if st.button("Borrar registros"):
        borrar_registros()

# ------------------------
# Actualizar objetivo
# ------------------------

elif menu == "🎯 Actualizar objetivo":
    st.subheader("Actualizar peso objetivo")
    peso_objetivo = st.number_input("Peso objetivo (kg)", min_value=30.0, max_value=200.0, step=0.1)
    fecha_objetivo = st.date_input("Fecha para alcanzar el objetivo")
    if st.button("Guardar objetivo"):
        guardar_objetivo(peso_objetivo, fecha_objetivo)
        st.success("🎯 Objetivo actualizado correctamente.")


