import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone, date
from supabase import create_client

# Conexión a Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Registro de Peso", layout="centered")
st.title("📈 Carols curve")

# Funciones auxiliares
def guardar_peso(peso):
    try:
        supabase.table("peso").insert({"peso": peso, "created_at": datetime.now(timezone.utc).isoformat()}).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
        return False

def cargar_pesos():
    try:
        data = supabase.table("peso").select("*").order("created_at", desc=True).execute().data
        df = pd.DataFrame(data)
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"])
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame()

def borrar_todos_los_registros():
    supabase.table("peso").delete().neq("id", 0).execute()

def guardar_objetivo(peso_objetivo, fecha_objetivo):
    try:
        supabase.table("objetivo").insert({
            "peso_objetivo": peso_objetivo,
            "fecha_objetivo": fecha_objetivo.isoformat()
        }).execute()
        st.success("🎯 Objetivo guardado correctamente")
    except Exception as e:
        st.error(f"❌ Error al guardar el objetivo: {e}")

def leer_ultimo_objetivo():
    try:
        response = supabase.table("objetivo").select("*").order("created_at", desc=True).limit(1).execute()
        data = response.data
        if data:
            return data[0]
        return None
    except Exception as e:
        st.error(f"❌ Error al leer objetivo: {e}")
        return None

# Menú
opcion = st.sidebar.radio("Selecciona una opción", ("Registrar peso", "Borrar registros", "Actualizar objetivo"))

if opcion == "Registrar peso":
    st.subheader("📥 Registrar nuevo peso")
    df = cargar_pesos()

    objetivo = leer_ultimo_objetivo()
    if objetivo:
        peso_obj = objetivo["peso_objetivo"]
        fecha_obj = pd.to_datetime(objetivo["fecha_objetivo"])
        dias_restantes = (fecha_obj - datetime.now(timezone.utc)).days
        peso_actual = df["peso"].iloc[-1] if not df.empty else None

        st.markdown(f"""
        #### 🎯 Objetivo actual
        - **Peso objetivo:** {peso_obj:.1f} kg  
        - **Fecha límite:** {fecha_obj.strftime("%d/%m/%Y")}  
        - **Días restantes:** {dias_restantes} días  
        """)

        if peso_actual:
            diferencia = peso_actual - peso_obj
            st.markdown(f"- **Diferencia de peso actual:** {diferencia:+.1f} kg")

            if datetime.now(timezone.utc) > fecha_obj:
                if diferencia > 0:
                    st.warning("⚠️ No ha alcanzado el objetivo, establezca un nuevo objetivo.")
            elif diferencia <= 0:
                dias_anticipacion = abs(dias_restantes)
                st.success(f"🎉 ¡Enhorabuena! Has alcanzado el objetivo {dias_anticipacion} días antes.")

    peso_input = st.number_input("Introduce tu peso (kg)", min_value=30.0, max_value=200.0, step=0.1, key="peso")

    if st.button("Guardar peso"):
        st.session_state.confirmar = True
        st.session_state.peso_temp = peso_input

    if st.session_state.get("confirmar"):
        st.write(f"¿Es correcto el peso {st.session_state.peso_temp:.1f} kg?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar"):
                if guardar_peso(st.session_state.peso_temp):
                    st.success("Peso guardado correctamente")
                    st.session_state.confirmar = False
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar = False

elif opcion == "Borrar registros":
    st.subheader("🗑️ Borrar todos los registros")
    if st.button("Eliminar todos los pesos registrados"):
        borrar_todos_los_registros()
        st.success("Todos los registros han sido eliminados")

elif opcion == "Actualizar objetivo":
    st.subheader("🎯 Establecer nuevo objetivo")
    nuevo_peso = st.number_input("Introduce el peso objetivo (kg)", min_value=30.0, max_value=200.0, step=0.1)
    nueva_fecha = st.date_input("Fecha para alcanzar el objetivo")
    if st.button("Guardar nuevo objetivo"):
        guardar_objetivo(nuevo_peso, datetime.combine(nueva_fecha, datetime.min.time(), tzinfo=timezone.utc))

