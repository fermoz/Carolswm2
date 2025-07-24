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
# Función para guardar peso
# ------------------------
def guardar_peso(peso):
    try:
        data = {"peso": float(peso)}
        supabase.table("peso").insert(data).execute()
        st.success("✅ Peso guardado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# ------------------------
# Función para leer los datos
# ------------------------
def leer_pesos():
    response = supabase.table("peso").select("*").order("created_at", desc=True).limit(100).execute()
    df = pd.DataFrame(response.data)

    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)

    return df

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
# Registro de nuevo peso
# ------------------------
st.title("Registro de peso")

peso = st.number_input("Introduce tu peso (kg)", min_value=20.0, max_value=200.0, step=0.1)

if st.button("Guardar peso"):
    guardar_peso(peso)

# ------------------------
# Mostrar histórico
# ------------------------
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




