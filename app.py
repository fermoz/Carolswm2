import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pandas as pd

# ------------------------
# Conexión con Supabase
# ------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ------------------------
# Guardar nuevo peso
# ------------------------
def guardar_peso(peso):
    data = {"peso": float(peso)}  # No pongas "id", ni "created_at"
    response = supabase.table("peso").insert(data).execute()
    if response.error:
        st.error(f"❌ Error al guardar: {response.error}")


# ------------------------
# Leer datos de la tabla
# ------------------------
def leer_pesos():
    response = supabase.table("peso").select("*").order("created_at", desc=True).limit(100).execute()
    return pd.DataFrame(response.data)

# ------------------------
# Pantalla de bienvenida
# ------------------------
if "entrado" not in st.session_state:
    st.session_state.entrado = False

if not st.session_state.entrado:
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Carol's curve</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tu evolución, paso a paso.</p>", unsafe_allow_html=True)
    if st.button("Entrar"):
        st.session_state.entrado = True
    st.stop()

# ------------------------
# Interfaz principal
# ------------------------
st.title("Registro de peso")

peso = st.number_input("Introduce tu peso (kg)", min_value=20.0, max_value=200.0, step=0.1)

if st.button("Guardar peso"):
    guardar_peso(peso)
    st.success("Peso guardado en Supabase.")

# ------------------------
# Mostrar histórico
# ------------------------
df = leer_pesos()
if not df.empty:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at")
    st.subheader("Historial de peso")
    st.dataframe(df.tail(5), use_container_width=True)

    if len(df) >= 2:
        diff = df.iloc[-1]["peso"] - df.iloc[-2]["peso"]
        st.write(f"📉 Diferencia con la última medición: {diff:.1f} kg")

    ultimos_30 = df[df["created_at"] > datetime.now() - timedelta(days=30)]
    if not ultimos_30.empty:
        media30 = ultimos_30["peso"].mean()
        delta = df.iloc[-1]["peso"] - media30
        st.write(f"📊 Diferencia con la media de los últimos 30 días: {delta:.1f} kg")

