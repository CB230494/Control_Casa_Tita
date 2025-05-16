import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# === CONEXIÓN CON GOOGLE SHEETS DESDE SECRETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# === HOJA ÚNICA ===
ws = client.open("Control_Casa_Tita").sheet1

# === VARIABLES ===
MONTO_INICIAL = 11605319
TRABAJADORES_BASE = [
    ["Gilberth Rojas Bogantes", "109320677"],
    ["Roy Francisco Alvarez Moya", "20330183"],
    ["William Antonio Zeledon Chaves", "205520554"],
    ["Juan Alexis Chacon Saborio", "206200794"],
    ["Maycol Mauricio Mata Zeledon", "207060735"]
]

# === CARGA DE DATOS ===
data = ws.get_all_records()
df = pd.DataFrame(data)

# === SEPARAR POR TIPO ===
df_asistencia = df[df["Tipo"] == "Asistencia"]
df_gastos = df[df["Tipo"] == "Gasto"]

st.title("Control Casa Tita")

st.sidebar.header("Menú")
modo = st.sidebar.radio("Selecciona", ["Registrar Asistencia", "Registrar Gasto", "Dashboard"])

# === REGISTRAR ASISTENCIA ===
if modo == "Registrar Asistencia":
    st.subheader("Registro de Asistencia")

    fecha = st.date_input("Fecha", value=date.today())

    # Mostrar casillas para marcar asistencia
    st.markdown("### Marcar asistencia")
    asistencia_registro = []
    for nombre, cedula in TRABAJADORES_BASE:
        asistio = st.checkbox(nombre, value=False)
        asistencia_registro.append([nombre, cedula, "Sí" if asistio else "No"])

    # Opción para agregar un trabajador nuevo
    st.markdown("---")
    st.markdown("### Agregar trabajador eventual")
    nuevo_nombre = st.text_input("Nombre del nuevo trabajador")
    nueva_cedula = st.text_input("Cédula del nuevo trabajador")
    nuevo_asistio = st.checkbox("¿Asistió?", value=False)

    if nuevo_nombre and nueva_cedula:
        asistencia_registro.append([nuevo_nombre, nueva_cedula, "Sí" if nuevo_asistio else "No"])

    # Botón para guardar todo
    if st.button("Guardar asistencia"):
        for nombre, cedula, asistio in asistencia_registro:
            fila = ["Asistencia", str(fecha), nombre, cedula, asistio, "", "", ""]
            ws.append_row(fila)
        st.success("Asistencia guardada correctamente.")

# === REGISTRAR GASTO ===
elif modo == "Registrar Gasto":
    st.subheader("Registro de Gasto")
    fecha = st.date_input("Fecha del gasto", value=date.today())
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto (₡)", min_value=0)
    categoria = st.selectbox("Categoría", ["Trabajadores", "Ferretería", "Arquitecta", "Otros"])

    if st.button("Guardar gasto"):
        fila = ["Gasto", str(fecha), "", "", "", descripcion, monto, categoria]
        ws.append_row(fila)
        st.success("Gasto registrado correctamente.")

# === DASHBOARD ===
elif modo == "Dashboard":
    st.subheader("Resumen del Proyecto")

    total_gastado = df_gastos["Monto"].astype(float).sum() if not df_gastos.empty else 0
    saldo = MONTO_INICIAL - total_gastado

    col1, col2, col3 = st.columns(3)
    col1.metric("Monto Inicial", f"₡{MONTO_INICIAL:,.0f}")
    col2.metric("Gastado", f"₡{total_gastado:,.0f}")
    col3.metric("Saldo Disponible", f"₡{saldo:,.0f}")

    st.markdown("### Asistencia")
    st.dataframe(df_asistencia)

    st.markdown("### Gastos")
    st.dataframe(df_gastos)

    if not df_gastos.empty:
        grafico = df_gastos.groupby("Categoría")["Monto"].sum().reset_index()
        st.bar_chart(grafico.set_index("Categoría"))