import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import os

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
st.title("Gestión de Maquinaria - Versión Web")

# Menú lateral
opcion = st.sidebar.selectbox(
    "Elige una opción",
    [
        "Agregar nueva maquinaria",
        "Actualizar estado de maquinaria",
        "Programar mantenimiento",
        "Registrar intervención (historial)",
        "Ver estado actual de toda la maquinaria",
        "Ver pendientes de mantenimiento",
        "Ver hoja de vida (historial) de una maquinaria"
    ]
)

if opcion == "Agregar nueva maquinaria":
    with st.form(key='agregar_maquinaria'):
        nombre = st.text_input("Nombre/ID de la maquinaria")
        descripcion = st.text_input("Descripción")
        estado = st.selectbox("Estado inicial", ["operativa", "no operativa"])
        submit = st.form_submit_button("Agregar")
        if submit:
            cursor.execute("INSERT INTO maquinaria (nombre, descripcion, estado) VALUES (%s, %s, %s)", (nombre, descripcion, estado))
            conn.commit()
            st.success("Maquinaria agregada.")

elif opcion == "Actualizar estado de maquinaria":
    df = load_maquinaria()
    st.dataframe(df)
    with st.form(key='actualizar_estado'):
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        nuevo_estado = st.selectbox("Nuevo estado", ["operativa", "no operativa"])
        submit = st.form_submit_button("Actualizar")
        if submit:
            cursor.execute("UPDATE maquinaria SET estado = %s WHERE id = %s", (nuevo_estado, id_maquinaria))
            conn.commit()
            st.success("Estado actualizado.")

elif opcion == "Programar mantenimiento":
    df = load_maquinaria()
    st.dataframe(df)
    with st.form(key='programar_mantenimiento'):
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        tipo = st.text_input("Tipo de mantenimiento")
        fecha = st.date_input("Fecha programada")
        submit = st.form_submit_button("Programar")
        if submit:
            cursor.execute("INSERT INTO mantenimiento (maquinaria_id, tipo, fecha_programada) VALUES (%s, %s, %s)", (id_maquinaria, tipo, fecha))
            conn.commit()
            st.success("Mantenimiento programado.")

elif opcion == "Registrar intervención (historial)":
    df = load_maquinaria()
    st.dataframe(df)
    with st.form(key='registrar_intervencion'):
        id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
        descripcion = st.text_input("Descripción de la intervención")
        costo = st.number_input("Costo", min_value=0.0)
        estado_resultante = st.selectbox("Estado resultante", ["operativa", "no operativa"])
        fecha = datetime.now().date()
        submit = st.form_submit_button("Registrar")
        if submit:
            cursor.execute("INSERT INTO intervenciones (maquinaria_id, fecha, descripcion, costo, estado_resultante) VALUES (%s, %s, %s, %s, %s)", 
                           (id_maquinaria, fecha, descripcion, costo, estado_resultante))
            conn.commit()
            st.success("Intervención registrada.")

elif opcion == "Ver estado actual de toda la maquinaria":
    df = load_maquinaria()
    st.dataframe(df)

elif opcion == "Ver pendientes de mantenimiento":
    df = pd.read_sql_query("SELECT m.nombre, mt.tipo, mt.fecha_programada FROM mantenimiento mt JOIN maquinaria m ON mt.maquinaria_id = m.id WHERE mt.completado = FALSE", conn)
    st.write("Pendientes de mantenimiento:")
    st.dataframe(df)

elif opcion == "Ver hoja de vida (historial) de una maquinaria":
    df_maq = load_maquinaria()
    st.dataframe(df_maq)
    id_maquinaria = st.number_input("ID de la maquinaria", min_value=1)
    df = pd.read_sql_query("SELECT * FROM intervenciones WHERE maquinaria_id = %s", conn, params=(id_maquinaria,))
    st.write("Hoja de vida (intervenciones):")
    st.dataframe(df)
    if not df.empty:
        total_costo = df['costo'].sum()
        st.write(f"Total costos: {total_costo}")

# Cerrar conexión
conn.close()