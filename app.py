import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import os

# Estilo CSS personalizado para responsive y profesional
st.markdown(
    """
    <style>
    /* Fondo principal y responsive */
    .main {
        background-color: #F5F5F5; /* Gris claro como base neutra */
        padding: 20px;
        border-radius: 10px;
        font-family: 'Arial', sans-serif;
        color: #333333; /* Texto principal oscuro */
    }
    @media (max-width: 768px) {
        .main {
            padding: 10px;
        }
    }

    /* Botones con estilo amarillo */
    .stButton > button {
        background-color: #FFD700; /* Amarillo dorado */
        color: #333333; /* Texto oscuro para contraste */
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
        border: none;
    }
    .stButton > button:hover {
        background-color: #FFE066; /* Amarillo suave en hover */
    }
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin-bottom: 10px;
        }
    }

    /* Títulos y texto */
    h1 {
        color: #004D80; /* Azul oscuro para headers */
        text-align: center;
        font-weight: bold;
    }
    .stSubheader {
        color: #004D80;
    }

    /* Tablas responsive */
    .stDataFrame {
        border: 1px solid #808080; /* Gris medio */
        border-radius: 5px;
        padding: 10px;
        background-color: #FFFFFF; /* Blanco para cards */
        overflow-x: auto; /* Scroll horizontal en móvil */
    }
    @media (max-width: 768px) {
        .stDataFrame {
            font-size: 14px;
        }
    }

    /* Modo oscuro opcional */
    .dark-mode {
        background-color: #001F3F; /* Azul muy oscuro */
        color: #FFFFFF; /* Texto claro */
    }
    .dark-mode .stButton > button {
        background-color: #FFD700;
        color: #001F3F;
    }
    .dark-mode .stButton > button:hover {
        background-color: #FFE066;
    }
    .dark-mode h1, .dark-mode .stSubheader {
        color: #00A0C0; /* Teal claro */
    }
    .dark-mode .stDataFrame {
        background-color: #00264D;
        border-color: #00A0C0;
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
    tipo TEXT NOT NULL,
    capacidad TEXT NOT NULL,
    unidad_medida TEXT NOT NULL
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
    cursor.execute("SELECT nombre, tipo, capacidad, medida, estado FROM maquinaria")
    return pd.DataFrame(cursor.fetchall(), columns=["Nombre", "Tipo", "Capacidad", "medida", "Estado"])

# Interfaz web con Streamlit
st.markdown('<div class="main">', unsafe_allow_html=True)
st.image("assets/logo_empresa.png", width=200, caption="Logo de la Empresa")
st.title("Mantenimiento VG")  # Cambio de título a "Mantenimiento VG"

# Interruptor para modo oscuro
dark_mode = st.checkbox("Activar modo oscuro", value=False)
if dark_mode:
    st.markdown('<style>.main { background-color: #001F3F; color: #FFFFFF; }</style>', unsafe_allow_html=True)
    st.markdown('<style>.dark-mode { display: block; }</style>', unsafe_allow_html=True)
else:
    st.markdown('<style>.dark-mode { display: none; }</style>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Estado de la página
if "page" not in st.session_state:
    st.session_state.page = "home"

# Botones con iconos
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("➕ Agregar Maquinaria", key="btn_add", help="Agregar una nueva máquina"):
        st.session_state.page = "agregar_maquinaria"
    if st.button("🔧 Actualizar Estado", key="btn_update", help="Actualizar estado de una máquina"):
        st.session_state.page = "actualizar_estado"
with col2:
    if st.button("🛠️ Programar Mantenimiento", key="btn_schedule", help="Programar mantenimiento"):
        st.session_state.page = "programar_mantenimiento"
    if st.button("📝 Registrar Intervención", key="btn_record", help="Registrar intervención"):
        st.session_state.page = "registrar_intervencion"
with col3:
    if st.button("📋 Ver Estado", key="btn_view_state", help="Ver estado de máquinas"):
        st.session_state.page = "ver_estado"
    if st.button("⏰ Ver Pendientes", key="btn_pendings", help="Ver mantenimientos pendientes"):
        st.session_state.page = "ver_pendientes"
    if st.button("📊 Ver Hoja de Vida", key="btn_history", help="Ver hoja de vida de máquinas"):
        st.session_state.page = "ver_hoja_vida"

# Páginas dinámicas
if st.session_state.page == "agregar_maquinaria":
    with st.form(key='agregar_maquinaria'):
        st.subheader("Agregar Nueva Maquinaria")
        nombre = st.text_input("Nombre", help="Nombre alfanumérico de la máquina")
        tipo = st.selectbox("Tipo", ["Lav", "Sec", "Cen", "SG", "Man"], help="Tipo de maquinaria")
        capacidad = st.text_input("Capacidad", help="Valor numérico de capacidad")
        unidad_medida = st.selectbox("medida", ["LBS", "HP"], help="Unidad de capacidad")
        submit = st.form_submit_button("Agregar")
        if submit:
            cursor.execute("""
                INSERT INTO maquinaria (nombre, tipo, capacidad, medida)
                VALUES (%s, %s, %s, %s)
            """, (nombre, tipo, capacidad, medida))
            conn.commit()
            st.success("Maquinaria agregada.")
            st.session_state.page = "home"
elif st.session_state.page == "actualizar_estado":
    st.subheader("Estado Actual de Maquinaria")
    # Cargar datos sin mostrar ID
    cursor.execute("SELECT nombre, tipo, capacidad, unidad_medida, estado FROM maquinaria")
    df = pd.DataFrame(cursor.fetchall(), columns=["Nombre", "Tipo", "Capacidad", "Unidad de medida", "Estado"])
    st.dataframe(df, use_container_width=True, hide_index=True)  # Oculta el índice
    if not df.empty:
        # Selector basado en nombres para una experiencia más amigable
        nombres = df["Nombre"].tolist()
        idx_maquinaria = st.selectbox("Selecciona una máquina", range(len(nombres)), format_func=lambda x: nombres[x])
        if idx_maquinaria is not None:
            maquina = df.iloc[idx_maquinaria].to_list()
            nombre, tipo, capacidad, unidad_medida, estado = maquina
            st.write(f"**Nombre:** {nombre}")
            st.write(f"**Tipo:** {tipo}")
            st.write(f"**Capacidad:** {capacidad}")
            st.write(f"**medida:** {medida}")
            st.write(f"**Estado:** {estado}")
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
    if not df.empty:
        id_maquinaria = st.number_input("ID de la máquina a eliminar", min_value=df['id'].min(), max_value=df['id'].max(), step=1)
        # Verificar si hay intervenciones asociadas
        cursor.execute("SELECT COUNT(*) FROM intervenciones WHERE maquinaria_id = %s", (id_maquinaria,))
        intervenciones_count = cursor.fetchone()[0]
        if st.button("Eliminar Máquina", key="btn_eliminar"):
            if st.session_state.get("confirm_eliminar", False):
                if intervenciones_count > 0:
                    if st.session_state.get("confirm_intervenciones", False):
                        # Eliminar intervenciones asociadas primero
                        cursor.execute("DELETE FROM intervenciones WHERE maquinaria_id = %s", (id_maquinaria,))
                        cursor.execute("DELETE FROM maquinaria WHERE id = %s", (id_maquinaria,))
                        conn.commit()
                        st.success(f"Máquina con ID {id_maquinaria} y sus intervenciones eliminadas.")
                        st.session_state.confirm_intervenciones = False
                        st.session_state.confirm_eliminar = False
                        st.rerun()  # Recarga la página
                    else:
                        st.warning(f"La máquina tiene {intervenciones_count} intervenciones. Haz clic de nuevo para eliminarla junto con sus intervenciones.")
                        st.session_state.confirm_intervenciones = True
                else:
                    # Sin intervenciones, eliminar directamente
                    cursor.execute("DELETE FROM maquinaria WHERE id = %s", (id_maquinaria,))
                    conn.commit()
                    st.success(f"Máquina con ID {id_maquinaria} eliminada.")
                    st.session_state.confirm_eliminar = False
                    st.rerun()  # Recarga la página
            else:
                st.warning("¿Estás seguro? Haz clic de nuevo para confirmar.")
                st.session_state.confirm_eliminar = True
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
        st.bar_chart({"Costos": [total_costo]})

# Cerrar conexión
conn.close()