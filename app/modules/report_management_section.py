from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit as st
from datetime import datetime
import os
import pandas as pd
import base64
import hashlib
import csv

# Base directory for reports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, '..', 'data', 'reports')

def show_report_management_section():
    st.subheader("Gestión de Informes")

    # Tabs for different funcionalidades
    tab_buscador, tab2, tab3 = st.tabs(["Buscador de jugadores disponibles", "Subir informes", "Directorio"])

    # Tab 1: Buscador de jugadores disponibles
    with tab_buscador:
        show_tab_buscador()

    # Tab 2: Subir informes
    with tab2:
        show_upload_report()

    # Tab 3: Directorio
    with tab3:
        st.subheader("Visualizador de directorio")
        st.info('Desarrollando...')




# Función para codificar PDF a base64
def encode_pdf_to_base64(filepath):
    with open(filepath, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")

# Pestaña: Buscador de jugadores disponibles
def show_tab_buscador():
    # Crear sesión de estado para navegación
    if 'navigation_stack' not in st.session_state:
        st.session_state['navigation_stack'] = []  # Guarda navegación en "directorios"

    # Base de navegación
    current_level = st.session_state['navigation_stack'][-1] if st.session_state['navigation_stack'] else None

    # Primer nivel: Mostrar jugadores
    if current_level is None:
        players_with_folders = []
        for folder in os.listdir(REPORTS_DIR):
            folder_path = os.path.join(REPORTS_DIR, folder)
            if os.path.isdir(folder_path):
                player_id = folder.split('_')[-1]
                player_data = st.session_state.df_unique.loc[
                    st.session_state.df_unique['playerId'] == int(player_id)
                ]
                if not player_data.empty:
                    player_info = player_data.iloc[0]
                    players_with_folders.append({
                        "ID": player_id,
                        "Nombre": f"{player_info['firstName']} {player_info['lastName']}",
                        "Nacionalidad": player_info['nameBirthArea'],
                        "Equipo": player_info['teamName']
                    })

        if players_with_folders:
            st.markdown("#### Jugadores con informes disponibles")
            df_players = pd.DataFrame(players_with_folders)

            # Configurar AgGrid
            gb = GridOptionsBuilder.from_dataframe(df_players)
            gb.configure_selection('single', use_checkbox=True)
            grid_options = gb.build()

            # Mostrar AgGrid
            grid_response = AgGrid(
                df_players,
                gridOptions=grid_options,
                height=300,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                theme='streamlit'
            )

            # Navegación al segundo nivel
            selected_rows = grid_response['selected_rows']
            if selected_rows is not None and len(selected_rows) > 0:
                player_id = selected_rows["ID"][0]
                player_name = selected_rows["Nombre"][0]
                st.session_state['navigation_stack'].append(player_id)
                st.session_state['selected_player_name'] = player_name
                st.rerun()
        else:
            st.info("No se encontraron jugadores con informes disponibles.")

    # Segundo nivel: Mostrar informes del jugador seleccionado
    else:
        player_id = current_level
        player_name = st.session_state.get('selected_player_name', f"ID {player_id}") 
        player_dir = os.path.join(REPORTS_DIR, f"player_{player_id}")
        if os.path.exists(player_dir):
            reports = os.listdir(player_dir)
            if reports:
                processed_reports = []
                for report in reports:
                    parts = report.split('_')
                    report_type = parts[1]
                    report_date = parts[2].replace('.pdf', '')
                    report_path = os.path.join(player_dir, report)
                    
                    # Agregar datos procesados
                    processed_reports.append({
                        "Fecha": datetime.strptime(report_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
                        "Tipo de Informe": report_type.capitalize(),
                        "Nombre Original": report,
                        "Ruta": report_path
                    })

                # Mostrar tabla con AgGrid
                reports_df = pd.DataFrame(processed_reports)

                # Botón "Atrás" en la esquina superior izquierda
                col1, col2 = st.columns([0.80, 0.20])
                with col2:
                    if st.button("**←  Atrás**", key="back_button"):
                        st.session_state['navigation_stack'].pop()
                        st.rerun()

                st.markdown(f"#### Informes de {player_name}")

                # Configurar AgGrid para incluir la columna 'Ruta' oculta
                gb_reports = GridOptionsBuilder.from_dataframe(reports_df)
                gb_reports.configure_column("Ruta", hide=True)  # Ocultar la columna 'Ruta'
                gb_reports.configure_selection('single', use_checkbox=True)
                grid_options_reports = gb_reports.build()


                # Mostrar la tabla interactiva
                grid_response_reports = AgGrid(
                    reports_df,
                    gridOptions=grid_options_reports,
                    height=300,
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    theme='streamlit'
                )


                # Mostrar PDF previsualizado
                selected_report = grid_response_reports['selected_rows']
                if selected_report is not None and not selected_report.empty:
                    report_path = selected_report.iloc[0]["Ruta"]
                    pdf_base64 = encode_pdf_to_base64(report_path)
                    report_name = selected_report.iloc[0]["Nombre Original"] # Nombre original archivo pdf

                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.markdown("**Previsualización:**")
                    with col2:
                        # Botón de descarga
                        href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{report_name}">**⬇ Descargar Informe**</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    pdf_viewer = f"""
                        <iframe src="data:application/pdf;base64,{pdf_base64}" 
                                width="100%" height="600px"></iframe>
                    """
                    st.markdown(pdf_viewer, unsafe_allow_html=True)


            else:
                st.info("No se encontraron informes disponibles para este jugador.")





def calculate_file_hash(file_bytes):
    """
    Genera un hash MD5 único a partir del contenido del archivo.
    Args:
        file_bytes: Contenido del archivo en bytes.
    Returns:
        str: Hash MD5 del archivo.
    """
    md5_hash = hashlib.md5()  # Inicializar el objeto de hash
    md5_hash.update(file_bytes)  # Calcular hash del contenido
    return md5_hash.hexdigest()  # Devolver el hash en formato hexadecimal



# Ruta del archivo CSV
LOG_FILE_PATH = os.path.join("data", "uploaded_files_log.csv")

def log_uploaded_file(player_id, file_name, file_hash, file_path, uploaded_by, log_file=LOG_FILE_PATH):
    """
    Registra los detalles del archivo subido en un archivo CSV.

    Args:
        player_id (str): ID del jugador.
        file_name (str): Nombre del archivo subido.
        file_hash (str): Hash del archivo.
        file_path (str): Ruta del archivo guardado.
        uploaded_by (str): Usuario que subió el archivo.
        log_file (str): Ruta del archivo CSV donde se guarda el registro.
    """
    file_exists = os.path.isfile(log_file)  # Verificar si el archivo de log existe

    # Crear la carpeta "data/reports" si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Agregar fecha y hora actual
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", newline="", encoding="utf-8") as csvfile:
        # Campos del CSV
        fieldnames = ["player_id", "file_name", "file_hash", "file_path", "uploaded_by", "upload_datetime"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escribir el encabezado si el archivo es nuevo
        if not file_exists:
            writer.writeheader()

        # Escribir los detalles del archivo en una nueva fila
        writer.writerow({
            "player_id": player_id,
            "file_name": file_name,
            "file_hash": file_hash,
            "file_path": file_path,
            "uploaded_by": uploaded_by,
            "upload_datetime": current_datetime
        })

# Pestaña: Subir informes
def show_upload_report():
    st.markdown("### Subir Informes de Jugadores")
    df_unique = st.session_state.df_unique  # Asegura que df_unique esté en session_state

    # Selección del método de búsqueda
    search_method = st.radio("Método de búsqueda:", ["Por Liga", "Por Nacionalidad"], horizontal=True)

    if search_method == "Por Liga":
        st.markdown("**Busqueda por liga**")
        # Filtro por País de Liga
        countries = sorted(df_unique['nameArea'].unique())
        selected_country = st.selectbox("Selecciona el país", countries, key="country_league")
        st.session_state.selected_country_upload = selected_country

        # Filtro por Liga
        df_countries = df_unique[df_unique['nameArea'] == selected_country]
        leagues = sorted(df_countries['competitionName'].unique())
        selected_league = st.selectbox("Selecciona la liga", leagues, key="league_name")
        st.session_state.selected_league_upload = selected_league

        # Filtro por Equipo
        df_leagues = df_countries[(df_countries['competitionName'] == selected_league) & (df_countries['nameArea'] == selected_country)]
        teams = sorted(df_leagues['teamName'].unique())
        selected_team = st.selectbox("Selecciona el equipo", teams, key="team_name")
        st.session_state.selected_team_upload = selected_team

        filtered_df = df_unique[df_unique['teamName'] == selected_team]

        # Filtro final de Jugador
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.markdown("**Selecciona el jugador:**")
            short_names = sorted(filtered_df['shortName'].unique())
            selected_short_name = st.selectbox("Jugador", short_names, key="player_name")
            selected_player = filtered_df[filtered_df['shortName'] == selected_short_name].iloc[0]
            player_name = selected_player['shortName']
            selected_player_id = selected_player['playerId']
        with col2:
            add_vertical_space(4)
            st.success(f"ID: {selected_player_id}")

    elif search_method == "Por Nacionalidad":
        st.markdown("**Búsqueda por Nacionalidad o Pasaporte**")

        # Filtro obligatorio: Nacionalidad o Pasaporte
        nationalities = sorted(df_unique['nameBirthArea'].dropna().unique())

        # Definir índice predeterminado en base a "Argentina"
        default_index = nationalities.index("Argentina") if "Argentina" in nationalities else 0

        # Mostrar selectbox con valor por defecto
        selected_nationality = st.selectbox(
            "Selecciona la nacionalidad / pasaporte",
            nationalities,
            index=default_index,  # Índice predeterminado
            key="nationality"
        )
        st.session_state.selected_nationality_upload = selected_nationality


        # Filtrar el DataFrame por nacionalidad o pasaporte
        df_nationality = df_unique[
            (df_unique['nameBirthArea'] == selected_nationality) | 
            (df_unique['namePassportArea'] == selected_nationality)
        ]

        # Filtros opcionales
        col1, col2, col3 = st.columns(3)

        with col1:
            countries = sorted(df_nationality['nameArea'].dropna().unique())
            selected_country = st.selectbox("Filtrar por país de liga (opcional)", 
                                        ["Todos"] + countries, key="country_nationality")
            # Filtrar DataFrame por país si se selecciona uno
            if selected_country != "Todos":
                df_nationality = df_nationality[df_nationality['nameArea'] == selected_country]

        with col2:
            leagues = sorted(df_nationality['competitionName'].dropna().unique())
            selected_league = st.selectbox("Filtrar por liga (opcional)", 
                                        ["Todas"] + leagues, key="league_nationality")
            # Filtrar DataFrame por liga si se selecciona una
            if selected_league != "Todas":
                df_nationality = df_nationality[df_nationality['competitionName'] == selected_league]

        with col3:
            teams = sorted(df_nationality['teamName'].dropna().unique())
            selected_team = st.selectbox("Filtrar por equipo (opcional)", 
                                        ["Todos"] + teams, key="team_nationality")
            # Filtrar DataFrame por equipo si se selecciona uno
            if selected_team != "Todos":
                df_nationality = df_nationality[df_nationality['teamName'] == selected_team]

        # Aplicar filtros opcionales si se seleccionan
        filtered_df = df_nationality.copy()

        # Filtro final de Jugador
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.markdown("**Selecciona el jugador:**")
            short_names = sorted(filtered_df['shortName'].unique())
            selected_short_name = st.selectbox("Jugador", short_names, key="player_name")
            selected_player = filtered_df[filtered_df['shortName'] == selected_short_name].iloc[0]
            player_name = selected_player['shortName']
            selected_player_id = selected_player['playerId']
        with col2:
            add_vertical_space(4)
            st.success(f"ID: {selected_player_id}")
        

    # Tipo de informe y fecha
    report_types = ["Rapido","Avanzado","Comparativo","Completo"]
    selected_report_type = st.selectbox("Selecciona el tipo de informe", report_types)
    report_date = st.date_input("Fecha del informe", datetime.today())

    # Estado en session_state para resetear el uploader
    if 'reset_uploader' not in st.session_state:
        st.session_state['reset_uploader'] = False

    # Estado en session_state para resetear el uploader
    if 'uploader_key' not in st.session_state:
        st.session_state['uploader_key'] = 0  # Inicializa el contador de claves

    # Subida del archivo con clave dinámica
    uploaded_file = st.file_uploader(
        "Sube el informe en formato PDF", 
        type=["pdf"], 
        key=f"uploader_{st.session_state['uploader_key']}"  # Clave dinámica
    )

    # Confirmación del archivo
    if uploaded_file is not None:
        # Botones de confirmación
        col1, col2, col3, col4, col5 = st.columns([0.2, 0.3, 0.1, 0.4, 0.1])
        with col2:
            if st.button("✅ Confirmar", key="confirm_upload"):
                st.session_state['file_ready_to_save'] = True
        with col4:
            if st.button("❌ Cancelar", key="cancel_upload"):
                st.session_state['file_ready_to_save'] = False
                st.session_state['uploader_key'] += 1  # Incrementa el contador para resetear el uploader
                st.warning("Subida de archivo cancelada.")
                st.rerun()  # Recarga la aplicación para aplicar el cambio


    # Guardar archivo
    if st.session_state.get('file_ready_to_save', False):
        report_name = f"{selected_player_id}_{selected_report_type.lower()}_{report_date}.pdf"
        player_folder = os.path.join(REPORTS_DIR, f"player_{selected_player_id}")
        save_path = os.path.join(player_folder, report_name)

        os.makedirs(player_folder, exist_ok=True)  # Crear carpeta si no existe

        # Generar el hash del archivo
        file_hash = calculate_file_hash(uploaded_file.getvalue())

        # Verificar si el archivo ya existe
        if os.path.exists(save_path):
            st.warning(f"El archivo '{report_name}' ya existe.")

            if st.button("⚠️ Sobrescribir archivo"):
                # Guardar archivo si el usuario confirma
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                    # Registrar el archivo
                    uploaded_by = st.session_state.get('username', 'unknown_user')
                    log_uploaded_file(selected_player_id, report_name, file_hash, save_path, uploaded_by)
                    st.success(f'''
                               - Jugador: {player_name}\n\n
                               El archivo {report_name} fue sobrescrito correctamente
                               ''')
                    st.info(f"Ruta del archivo: {save_path}")
                    st.session_state['file_ready_to_save'] = False
                    uploaded_file = None
        else:
            # Guardar archivo si no existe
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Registrar el archivo
            uploaded_by = st.session_state.get('username', 'unknown_user')
            log_uploaded_file(selected_player_id, report_name, file_hash, save_path, uploaded_by)

            st.success(f"-  Jugador: {player_name}\n\nInforme guardado correctamente: {report_name}")
            st.info(f"Ruta del archivo: {save_path}")
            st.session_state['file_ready_to_save'] = False
            uploaded_file = None