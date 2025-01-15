import os
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

from modules.load_files import load_files
from modules.login import load_users, login_user, logout_user

# Importar las dos categorías
from modules.scouting_section import show_scouting_section
from modules.report_management_section import show_report_management_section

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logo_talleres_path = os.path.join(BASE_DIR, 'resources','talleres_logo.png')
sdc_logo_path = os.path.join(BASE_DIR, 'resources','sdc_logo_hor.png')

# Configuración de la página principal
im = Image.open(logo_talleres_path)
st.set_page_config(page_title='Scouting CA Talleres', page_icon=im)

# Inicialización de session_state para variables clave
def initialize_session_state():
    # Variables clave necesarias
    if 'result_df' not in st.session_state:
        st.session_state.result_df = pd.DataFrame()
    if 'important_columns' not in st.session_state:
        st.session_state.important_columns = []
    if 'selected_player_id' not in st.session_state:
        st.session_state.selected_player_id = None
    if 'selected_reference_season' not in st.session_state:
        st.session_state.selected_reference_season = None
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {'username': '', 'password': '', 'logged_in': False}
    # Aquí solo definimos las variables de datos, pero no las cargamos todavía
    if 'df_group' not in st.session_state:
        st.session_state.df_group = None
    if 'df_unique' not in st.session_state:
        st.session_state.df_unique = None
    if 'df_positions' not in st.session_state:
        st.session_state.df_positions = None

# Función para cargar archivos solo cuando son necesarios
def load_data_if_needed():
    # Si los datos no están cargados, los cargamos
    if st.session_state.df_group is None or st.session_state.df_unique is None or st.session_state.df_positions is None:
        st.session_state.df_group, st.session_state.df_unique, st.session_state.df_positions = load_files()
        st.success("Datos cargados exitosamente.")

# Ejecutar inicialización
initialize_session_state()

# Función principal de la aplicación
def main():
    # Diseño del encabezado
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image(logo_talleres_path, width=70)
    with col3:
        st.image(sdc_logo_path)

    # Cargar usuarios para autenticación
    users = load_users()

    # Verificación de estado del usuario en session_state
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'username': '',
            'password': '',
            'logged_in': False
        }

    # Manejo de sesión de usuario
    if not st.session_state.user_state['logged_in']:
        add_vertical_space(2)
        st.markdown('## Scouting - CA Talleres')
        
        username = st.text_input('Usuario')
        password = st.text_input('Contraseña', type='password')
        submit = st.button('Iniciar sesión')

        if submit:
            if login_user(users, username, password):
                # Guardar el nombre de usuario en session_state
                st.session_state.user_state['logged_in'] = True
                st.session_state.user_state['username'] = username  # Guardar el nombre del usuario
                st.session_state['username'] = username  # Copia en una variable global
                st.rerun()
            else:
                st.warning('Usuario / contraseña incorrecto')
    else:
        # Mostrar botón de cierre de sesión
        with col3:
            if st.button('Cerrar sesión'):
                logout_user()
                st.session_state.pop('username', None)  # Eliminar la variable de usuario global
                st.rerun()


        # Menú lateral para seleccionar sección de la app
        with st.sidebar:
            st.markdown("### Selecciona una sección")
            section = st.radio("", ["Scouting Similitud", "Gestión de Informes"], label_visibility="visible")

        # Lógica de cambio de sección con carga condicional de archivos
        if section == "Scouting Similitud":
            # Cargamos datos solo si no están ya en session_state
            load_data_if_needed()
            # Ahora mostramos la sección de Scouting
            show_scouting_section()
        elif section == "Gestión de Informes":
            # Cargamos datos solo si no están ya en session_state
            load_data_if_needed()
            show_report_management_section()

if __name__ == "__main__":
    main()