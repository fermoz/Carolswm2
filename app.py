import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta, timezone
import pandas as pd

# ------------------------
# Conexión con Supabase
# ------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ------------------------
# Funciones
# ------------------------

def guardar_peso(peso):
    try:
        data = {"peso": float(peso)}
        supabase.table("peso").insert(data).execute()
        st.success("✅ Peso guardado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

def leer_pesos():
    response = supabase.table("peso").select("*").order("created_at", desc=True).limit(100).execute()
    df = pd.DataFrame(response.data)
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df

def borrar_todo():
    try:
        supabase.table("peso").delete().neq("id", 0).execute()
        st.success("🗑️ Todos los registros han sido eliminados.")
    except Exception as e:
        st.error(f"❌ Error al borrar: {e}")

# ------------------------
# Interfaz de navegación
# ------------------------

st.set_page_config(page_title="Carol's Curve", page_icon="📈")
st.title("📈 Carol's Curve")

menu = st.sidebar.radio("Menú", ["1. Registrar peso", "2. Borrar registros"])

# ------------------------
# Registrar peso
# ------------------------

if menu == "1. Registrar peso":
    st.subheader("Registrar nuevo peso")
    peso = st.number_input("Introduce tu peso (kg)", min_value=20.0, max_value=200.0, step=0.1)

    if st.button("Guardar peso"):
        guardar_peso(peso)

    # Mostrar historial
    df = leer_pesos()
    if not df.empty:
        df = df.sort_values("created_at")
        st.subheader("Historial de peso")
        st.dataframe(df[["created_at", "peso"]].tail(5), use_container_width=True)

        if len(df) >= 2:
            diff = df.iloc[-1]["peso"] - df.iloc[-2]["peso"]
            st.write(f"📉 Diferencia con la última medición: {diff:.1f} kg")

        ultimos_30 = df[df["created_at"] > datetime.now(timezone.utc) - timedelta(days=30)]
        if not ultimos_30.empty:
            media30 = ultimos_30["peso"].mean()
            delta = df.iloc[-1]["peso"] - media30
            st.write(f"📊 Diferencia con la media de los últimos 30 días: {delta:.1f} kg")

# ------------------------
# Borrar registros
# ------------------------

elif menu == "2. Borrar registros":
    st.subheader("⚠️ Borrar todos los registros")
    if st.button("Borrar todo"):
        st.warning("Esta acción es irreversible.")
        borrar_todo()




