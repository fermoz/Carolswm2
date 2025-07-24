import streamlit as st
import pandas as pd
from datetime import datetime
import os


st.write("Archivo guardado en:", os.path.abspath(DATA_FILE))

# ---------- Configuración ----------
DATA_FILE = "peso.csv"

# ---------- Cargar datos ----------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["fecha_hora"])
    else:
        return pd.DataFrame(columns=["fecha_hora", "peso"])

# ---------- Guardar nuevo registro ----------
def guardar_dato(peso):
    df = cargar_datos()
    nueva_fila = pd.DataFrame({
        "fecha_hora": [datetime.now()],
        "peso": [peso]
    })
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return df

# ---------- Pantalla de bienvenida ----------
if "entrado" not in st.session_state:
    st.session_state.entrado = False

if not st.session_state.entrado:
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Carol's curve</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tu evolución, paso a paso.</p>", unsafe_allow_html=True)
    if st.button("Entrar"):
        st.session_state.entrado = True
    st.stop()

# ---------- Interfaz principal ----------
st.title("Registro de peso")

peso = st.number_input("Introduce tu peso (kg)", min_value=20.0, max_value=200.0, step=0.1)

if st.button("Guardar peso"):
    df = guardar_dato(peso)
    st.success("Peso guardado correctamente.")
else:
    df = cargar_datos()

# ---------- Mostrar últimos datos ----------
if not df.empty:
    st.subheader("Historial de peso")
    st.dataframe(df.tail(5))

    # Diferencia con la última medición
    if len(df) >= 2:
        diff_ult = df.iloc[-1]["peso"] - df.iloc[-2]["peso"]
        st.write(f"📉 Diferencia con la última medición: {diff_ult:.1f} kg")

    # Media últimos 30 días
    ultimos_30 = df[df["fecha_hora"] > (datetime.now() - pd.Timedelta(days=30))]
    if not ultimos_30.empty:
        media_30 = ultimos_30["peso"].mean()
        diff_media = df.iloc[-1]["peso"] - media_30
        st.write(f"📊 Diferencia con la media de los últimos 30 días: {diff_media:.1f} kg")
