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

# ====================
# Registrar peso
# ====================
if menu == "Registrar peso":
    df = leer_pesos()
    objetivo = leer_ultimo_objetivo()

    if objetivo:
        peso_obj = objetivo["peso_objetivo"]
        fecha_obj = pd.to_datetime(objetivo["fecha_objetivo"])
        if fecha_obj.tzinfo is None:
           fecha_obj = fecha_obj.tz_localize("UTC")

        dias_restantes = (fecha_obj - datetime.now(timezone.utc)).days
        peso_actual = df["peso"].iloc[-1] if not df.empty else None

        st.markdown(f"""
        #### 🎯 Objetivo actual
        - **Peso objetivo:** {peso_obj:.1f} kg  
        - **Fecha límite:** {fecha_obj.strftime("%d/%m/%Y")}  
        - **Días restantes:** {dias_restantes} días
        """)

        if peso_actual is not None:
            diferencia = peso_actual - peso_obj
            st.markdown(f"- **Diferencia de peso actual:** {diferencia:+.1f} kg")
            if datetime.now(timezone.utc) > fecha_obj:
                if diferencia > 0:
                    st.warning("⚠️ No ha alcanzado el objetivo, establezca un nuevo objetivo.")
            elif diferencia <= 0:
                st.success(f"🎉 ¡Enhorabuena! Has alcanzado el objetivo {abs(dias_restantes)} días antes.")

    peso = st.number_input("Introduce tu peso actual (kg)", min_value=30.0, max_value=200.0, step=0.1, format="%.1f")
    if st.button("Guardar peso"):
        confirmar = st.radio(f"¿Es correcto el peso {peso:.1f} kg?", ("Sí", "No"))
        if confirmar == "Sí":
            guardar_peso(peso)
        else:
            st.info("Vuelve a introducir tu peso si te has equivocado")

    # Mostrar histórico
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
            st.write(f"📊 Media últimos 30 días: {media30:.1f} kg")

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

