import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import psycopg2
import pandas as pd
from datetime import datetime
import os

# Estilo CSS personalizado usando st.markdown
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f5;
        padding: 20px;
        border-radius: 10px;
    }
    .icon-button {
        display: inline-block;
        margin: 10px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
    .icon-button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Conectar a la base de datos de Supabase (Connection Pooler)
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres.ddduccrecwuedpdprnah:pK4ViLhZhplWcjdp@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute('''
CREATE TABLE IF NOT EXISTS maquinaria (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS mantenimiento (
    id SERIAL PRIMARY KEY,
    maquinaria_id INTEGER,
    tipo TEXT NOT NULL,
    fecha_programada DATE,
    completado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (maquinaria_id) REFERENCES maquinaria(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS intervenciones (
    id SERIAL PRIMARY KEY,
    maquinaria_id INTEGER,
    fecha DATE NOT NULL,
    descripcion TEXT NOT NULL,
    costo REAL,
    estado_resultante TEXT,
    FOREIGN KEY (maquinaria_id) REFERENCES maquinaria(id)
)
''')

conn.commit()

# Función para cargar datos
def load_maquinaria():
    return pd.read_sql_query("SELECT * FROM maquinaria", conn)

# Interfaz web con Streamlit
st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("Gestión de Maquinaria - Versión Web")
st.markdown('</div>', unsafe_allow_html=True)

# Botones con iconos en la pantalla principal
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("➕ Agregar Maquinaria"):
        switch_page("agregar_maquinaria")
    if st.button("🔧 Actualizar Estado"):
        switch_page("actualizar_estado")
with col2:
    if st.button("🛠️ Programar Mantenimiento"):
        switch_page("programar_mantenimiento")
    if st.button("📝 Registrar Intervención"):
        switch_page("registrar_intervencion")
with col3:
    if st.button("📋 Ver Estado"):
        switch_page("ver_estado")
    if st.button("⏰ Ver Pendientes"):
        switch_page("ver_pendientes")
    if st.button("📊 Ver Hoja de Vida"):
        switch_page("ver_hoja_vida")

# Páginas dinámicas usando switch_page
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "agregar_maquinaria":
    with st.form(key='agregar_maquinaria'):
        st.subheader("Agregar Nueva Maquinaria")
        nombre = st.text_input("Nombre/ID de la maquinaria")
        descripcion = st.text_input("Descripción")
        estado = st.selectbox("Estado inicial", ["operativa", "no operativa"])
        submit = st.form_submit_button("Agregar")
        if submit:
            cursor.execute("INSERT INTO maquinaria (nombre, descripcion, estado) VALUES (%s, %s, %s)", (nombre, descripcion, estado))
            conn.commit()
            st.success("Maquinaria agregada.")
            st.session_state.page = "home"

elif st.session_state.page == "actualizar_estado":
    with st.form(key='actualizar_estado'):
        st.subheader("Actualizar Estado de Maquinaria")
        df = load_maquinaria()
        st.dataframe(df, use_container_width=True)
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        nuevo_estado = st.selectbox("Nuevo estado", ["operativa", "no operativa"])
        submit = st.form_submit_button("Actualizar")
        if submit:
            cursor.execute("UPDATE maquinaria SET estado = %s WHERE id = %s", (nuevo_estado, id_maquinaria))
            conn.commit()
            st.success("Estado actualizado.")
            st.session_state.page = "home"

elif st.session_state.page == "programar_mantenimiento":
    with st.form(key='programar_mantenimiento'):
        st.subheader("Programar Mantenimiento")
        df = load_maquinaria()
        st.dataframe(df, use_container_width=True)
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        tipo = st.text_input("Tipo de mantenimiento")
        fecha = st.date_input("Fecha programada")
        submit = st.form_submit_button("Programar")
        if submit:
            cursor.execute("INSERT INTO mantenimiento (maquinaria_id, tipo, fecha_programada) VALUES (%s, %s, %s)", (id_maquinaria, tipo, fecha))
            conn.commit()
            st.success("Mantenimiento programado.")
            st.session_state.page = "home"

elif st.session_state.page == "registrar_intervencion":
    with st.form(key='registrar_intervencion'):
        st.subheader("Registrar Intervención")
        df = load_maquinaria()
        st.dataframe(df, use_container_width=True)
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        descripcion = st.text_input("Descripción de la intervención")
        costo = st.number_input("Costo", min_value=0.0)
        estado_resultante = st.selectbox("Estado resultante", ["operativa", "no operativa"])
        submit = st.form_submit_button("Registrar")
        if submit:
            cursor.execute("INSERT INTO intervenciones (maquinaria_id, fecha, descripcion, costo, estado_resultante) VALUES (%s, %s, %s, %s, %s)", 
                           (id_maquinaria, datetime.now().date(), descripcion, costo, estado_resultante))
            conn.commit()
            st.success("Intervención registrada.")
            st.session_state.page = "home"

elif st.session_state.page == "ver_estado":
    st.subheader("Estado Actual de Maquinaria")
    df = load_maquinaria()
    st.dataframe(df, use_container_width=True)

elif st.session_state.page == "ver_pendientes":
    st.subheader("Pendientes de Mantenimiento")
    df = pd.read_sql_query("SELECT m.nombre, mt.tipo, mt.fecha_programada FROM mantenimiento mt JOIN maquinaria m ON mt.maquinaria_id = m.id WHERE mt.completado = FALSE", conn)
    st.dataframe(df, use_container_width=True)

elif st.session_state.page == "ver_hoja_vida":
    st.subheader("Hoja de Vida de Maquinaria")
    df_maq = load_maquinaria()
    st.dataframe(df_maq, use_container_width=True)
    id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
    df = pd.read_sql_query("SELECT * FROM intervenciones WHERE maquinaria_id = %s", conn, params=(id_maquinaria,))
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        total_costo = df['costo'].sum()
        st.write(f"**Total costos:** ${total_costo:.2f}")

# Cerrar conexión
conn.close()