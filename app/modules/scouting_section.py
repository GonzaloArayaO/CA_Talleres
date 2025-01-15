import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import pandas as pd
import hashlib
import os
from datetime import datetime
import plotly.graph_objects as go
from modules.load_files import load_files
from modules.similar_players import similarPlayers
from modules.positions import get_position_mapping
from modules.bar_chart import bar_chart_player_stats
from modules.player_profile import get_player_profiles
from modules.radar_chart import show_radar_with_table
from modules.pdf_exporter import save_pdf_file, style_table, generate_preview_pdf_content
from modules.player_info_stats import generate_player_info_stats
from modules.report_management_section import log_uploaded_file

@st.cache_data
def load_cached_files():
    return load_files()

def show_scouting_section():
    # Inicializar claves en session_state si no existen
    default_values = {
        'search_executed': False,
        'df_group': pd.DataFrame(),
        'df_unique': pd.DataFrame(),
        'df_positions': pd.DataFrame(),
        'result_df': pd.DataFrame(),
        'important_columns': [],
        'selected_player_id': None,
        'selected_reference_season': None,
        'season_id': None,
        'selected_primary_positions': [],
        'selected_secondary_positions': [],
        'selected_nationalities': [],
        'selected_age_range': (0, 0),
        'min_minutes': 0,
        'selected_countries_output': [],
        'selected_competitions_output': [],
        'num_results': 20,
        'selected_country': None,
        'selected_league': None,
        'selected_team': None,
    }

    # Iterar sobre las claves y asignar valores predeterminados si no están inicializadas
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if 'search_executed' not in st.session_state:
        st.session_state.search_executed = False 
    # Cargar los datos necesarios si aún no están en session_state
    if 'df_group' not in st.session_state or 'df_unique' not in st.session_state or 'df_positions' not in st.session_state:
        st.session_state.df_group, st.session_state.df_unique, st.session_state.df_positions = load_files()

    df_group = st.session_state.df_group
    df_unique = st.session_state.df_unique
    df_positions = st.session_state.df_positions

    # Sidebar con los filtros
    with st.sidebar:
        st.markdown('## Filtros')

        # Filtro de país
        countries = sorted(df_unique['nameArea'].unique())
        selected_country = st.selectbox('Selecciona el país', countries, label_visibility="visible")
        df_countries = df_unique[df_unique['nameArea'] == selected_country]
        st.session_state.selected_country = selected_country

        # Filtro de competencia
        leagues = sorted(df_countries['competitionName'].unique())
        selected_league = st.selectbox('Selecciona la liga', leagues, label_visibility="visible")
        df_leagues = df_unique[(df_unique['competitionName'] == selected_league) & (df_unique['nameArea'] == selected_country)]
        st.session_state.selected_league = selected_league

        # Filtro de equipo
        teams = sorted(df_leagues['teamName'].unique())
        selected_team = st.selectbox('Selecciona el equipo', teams, label_visibility="visible")
        df_filtered = df_leagues[df_leagues['teamName'] == selected_team]
        st.session_state.selected_team = selected_team

        # Filtro de jugador
        short_names = sorted(df_filtered['shortName'].unique())
        selected_short_name = st.selectbox('Selecciona el nombre del jugador', short_names, label_visibility="visible")
        selected_player = df_filtered[df_filtered['shortName'] == selected_short_name].iloc[0]
        selected_player_id = selected_player['playerId']

        # Filtro de temporada disponible
        seasons_data = df_unique[(df_unique['playerId'] == selected_player_id) & (df_unique['teamName'] == selected_team)][['seasonName', 'seasonId']].drop_duplicates()

        # Crear un diccionario para mapear seasonName a seasonId
        seasons_dict = dict(zip(seasons_data['seasonName'], seasons_data['seasonId']))

        # Seleccionar temporada de referencia
        selected_reference_season = st.selectbox('Selecciona la temporada de referencia', list(seasons_dict.keys()), label_visibility="visible")
        selected_reference_season = str(selected_reference_season)

        # Obtener el seasonId correspondiente a la temporada seleccionada
        season_id = seasons_dict[selected_reference_season]

        # Obtener el diccionario de posiciones
        position_mapping = get_position_mapping()  # Asegúrate de importar o definir esta función

        # Filtro de posición primaria
        primary_positions = position_mapping.keys()
        selected_primary_positions = st.multiselect("Selecciona la posición primaria", primary_positions, label_visibility="visible")
        st.session_state.selected_primary_positions = selected_primary_positions

        # Filtro de posición secundaria basado en la posición primaria seleccionada
        if selected_primary_positions:
            # Obtener las posiciones secundarias correspondientes
            secondary_positions = sorted({pos for primary in selected_primary_positions for pos in position_mapping[primary]})
            selected_secondary_positions = st.multiselect("Selecciona las posiciones secundarias", secondary_positions, label_visibility="visible")
            st.session_state.selected_secondary_positions = selected_secondary_positions
        else:
            selected_secondary_positions = []

        # Filtro de nacionalidad y pasaporte
        nationalities = sorted(df_unique[['nameBirthArea', 'namePassportArea']].stack().unique())
        selected_nationalities = st.multiselect('Selecciona nacionalidades/pasaporte', nationalities, label_visibility="visible")
        st.session_state.selected_nationalities = selected_nationalities

        # Filtro de edad
        df_unique = df_unique[df_unique['age'] >= 0]

        min_age = int(df_unique['age'].min())
        max_age = int(df_unique['age'].max())
        selected_age_range = st.slider('Selecciona el rango de edad', min_age, max_age, (min_age, max_age), label_visibility="visible")
        st.session_state.selected_age_range = selected_age_range

        # Calcular el máximo de minutos jugados por cualquier jugador en todas las temporadas
        max_minutes = df_group['minutesOnFieldTotal'].max()
        min_minutes = st.slider(
            f'Minutos mínimos jugados (hasta un máximo de {max_minutes} minutos)',
            min_value=0,
            max_value=int(max_minutes),
            step=50,
            label_visibility="visible"
        )
        st.session_state.min_minutes = min_minutes

        # Filtro de País de competencia
        countries_output = sorted(df_unique['nameArea'].unique())
        selected_countries_output = st.multiselect('Selecciona países para filtrar', countries_output, label_visibility="visible")
        st.session_state.selected_countries_output = selected_countries_output

        # Filtro de Competencia basado en el país seleccionado
        if selected_countries_output:
            df_filtered_output = df_unique[df_unique['nameArea'].isin(selected_countries_output)]
            competitions_output = sorted(df_filtered_output['competitionName'].unique())
            selected_competitions_output = st.multiselect('Selecciona competencias para filtrar', competitions_output, label_visibility="visible")
            st.session_state.selected_competitions_output = selected_competitions_output
        else:
            selected_competitions_output = []

        # Filtro de cantidad de resultados
        num_results = st.selectbox('Cantidad de resultados:', options=[10, 20, 50, 100, 200, 500], index=1, label_visibility="visible")
        st.session_state.num_results = num_results

        # Botón para iniciar búsqueda de jugadores similares
        buscar_similares = st.button('Buscar Jugadores Similares')

    # Ejecutar búsqueda de jugadores similares al presionar el botón
    if buscar_similares:
        try:
            result_df, important_columns = similarPlayers(
                df_group=df_group, 
                df_unique=df_unique, 
                df_positions=df_positions, 
                playerId=selected_player_id, 
                reference_season=selected_reference_season,
                season_id=season_id, 
                target_seasons=['2024', '2023/2024', '2024/2025'], 
                selected_primary_positions=selected_primary_positions,
                selected_secondary_positions=selected_secondary_positions, 
                selected_nationalities=selected_nationalities, 
                selected_age_range=selected_age_range, 
                min_minutes=min_minutes,
                selected_countries_output=selected_countries_output, 
                selected_competitions_output=selected_competitions_output,
                num_results=num_results
            )

            # Guardar los resultados en session_state
            st.session_state.result_df = result_df
            st.session_state.important_columns = important_columns
            st.session_state.selected_player_id = selected_player_id
            st.session_state.selected_reference_season = selected_reference_season
            st.session_state.season_id = season_id
            st.session_state.selected_primary_positions = selected_primary_positions
            st.session_state.selected_secondary_positions = selected_secondary_positions
            st.session_state.selected_nationalities = selected_nationalities
            st.session_state.selected_age_range = selected_age_range
            st.session_state.min_minutes = min_minutes
            st.session_state.selected_countries_output = selected_countries_output
            st.session_state.selected_competitions_output = selected_competitions_output
            st.session_state.num_results = num_results
            st.session_state.selected_country = selected_country
            st.session_state.selected_league = selected_league
            st.session_state.selected_team = selected_team
            st.session_state.search_executed = True

        except ValueError as e:
            st.warning(str(e))  # Mensaje si no se encuentran resultados
        except Exception as e:
            st.error(f"Error inesperado: {e}")
            return

    if st.session_state.search_executed:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            'Tabla similitud',
            'Ficha de jugador', 
            'Gráfico de barras comparación', 
            'Perfiles de juego', 
            'Exportación a PDF'
        ])
        with tab1:
            show_tab1()
        with tab2:
            show_tab2()
        with tab3:
            show_tab3()
        with tab4:
            show_tab4()
        with tab5:
            show_tab5()

# Pestaña 1: Tabla jugadores similares
def show_tab1():
    if not st.session_state.result_df.empty:
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("### Resultados de Similitud")
            st.markdown('*- Sólo jugadores de temporada 2024.*')

            result_df_to_display = st.session_state.result_df.drop(columns=['playerId'], errors='ignore')

            styled_table_html = style_table(result_df_to_display, for_pdf=False).to_html()

            # Mostrar la tabla en Streamlit
            st.markdown(styled_table_html, unsafe_allow_html=True)

        with col_right:
            with st.expander("#### Columnas utilizadas en el análisis", expanded=False):
                important_columns_str = " - ".join(st.session_state.important_columns)

                # HTML con color de fondo celeste claro
                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; padding: 10px;">
                        <p style="color: #0c5460; font-size: 13px;">{important_columns_str}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(f"""<div style="background-color: #ffffff; padding: 15px;">
                    <p style="color: #0c5460; font-size: 14px;">{len(st.session_state.important_columns)} columnas utilizadas.</p>
                    </div>""", unsafe_allow_html=True)
    else:
        st.markdown('## Análisis de Similitud de Jugadores')
        add_vertical_space(2)
        st.markdown("""Selecciona los parámetros en Filtros y haz clic en **Buscar Jugadores Similares** 
                    para ver los resultados y gráficas correspondientes.""")

# Pestaña 2: Ficha resumen de jugador
def show_tab2():    
    if not st.session_state.result_df.empty:
        player_id = st.session_state.selected_player_id
        player_info = st.session_state.df_unique.loc[
            st.session_state.df_unique['playerId'] == player_id
        ].iloc[0].to_dict()

        stats_info = ['matchesTotal', 'matchesInStartTotal', 'minutesOnFieldTotal', 'yellowCardsTotal', 'redCardsTotal', 'assistsTotal', 'goalsTotal']
        stats = st.session_state.df_group.loc[
            st.session_state.df_group['playerId'] == player_id
        ][stats_info].iloc[0].to_dict()


        generate_player_info_stats(player_info=player_info, stats=stats)
    else:
        st.warning("No hay datos disponibles para generar la ficha del jugador.")

    
# Pestaña 3: Gráfico de barras - Comparación
def show_tab3():
    if not st.session_state.result_df.empty:
        # Selectbox para seleccionar un jugador del DataFrame de resultados
        selected_result_player = st.selectbox(
            'Selecciona un jugador para comparar',
            st.session_state.result_df.get('Nombre', pd.Series()).unique()
            )

        # Verificar si el jugador seleccionado tiene datos
        player_data_for_chart = st.session_state.result_df[
            st.session_state.result_df['Nombre'] == selected_result_player
            ]

        if not player_data_for_chart.empty:
            player_id_for_chart = player_data_for_chart['playerId'].iloc[0]
            
            fig_left = bar_chart_player_stats(
                df_group=st.session_state.df_group,
                df_unique=st.session_state.df_unique,
                player_id=st.session_state.selected_player_id,
                important_columns=st.session_state.important_columns,
                selected_reference_season=st.session_state.selected_reference_season
                )
            st.plotly_chart(fig_left)
            st.session_state.bar_chart_left = fig_left

            st.markdown(
                "<hr style='border: none; border-top: 3px solid #00184C; margin: 10px 0;'>",
                unsafe_allow_html=True
            )

            fig_right = bar_chart_player_stats(
                df_group=st.session_state.df_group,
                df_unique=st.session_state.df_unique,
                player_id=player_id_for_chart,
                important_columns=st.session_state.important_columns
                )
            st.plotly_chart(fig_right)
            st.session_state.bar_chart_right = fig_right

            # Guardar en session_state para usar en el radar chart
            st.session_state.player_id_for_chart = player_id_for_chart
        else:
            st.warning("No se encontraron datos para el jugador seleccionado.")
            st.session_state.player_id_for_chart = None  # Inicializar si no hay jugador
    else:
        st.warning("Por favor, realiza una búsqueda para ver los gráficos de comparación.")


# Pestaña 4: Radar Chart - Comparación de Perfiles de Juego
def show_tab4():
    # Obtener perfiles de juego para el selectbox
    profiles = get_player_profiles()
    
    # Inicializar `selected_profile` en `session_state` si no está definido
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = list(profiles.keys())[0]  # Perfil predeterminado

    # Selectbox para elegir el perfil de juego
    selected_profile = st.selectbox(
        'Selecciona un perfil de juego',
        list(profiles.keys()),
        index=list(profiles.keys()).index(st.session_state.selected_profile)
    )
    add_vertical_space(2)

    # Actualizar el perfil de juego seleccionado en `session_state`
    if selected_profile != st.session_state.selected_profile:
        st.session_state.selected_profile = selected_profile

    # Obtener `player_id_for_chart` de `session_state` para el gráfico comparativo
    player_id_for_chart = st.session_state.get('player_id_for_chart')
    
    if player_id_for_chart is not None:
            show_radar_with_table(
                df_group=st.session_state.df_group, 
                df_unique=st.session_state.df_unique, 
                player_id=st.session_state.selected_player_id, 
                profile_name=st.session_state.selected_profile, 
                profiles=profiles,
                session_key='fig_radar_1'
                )
            
            st.markdown(
                "<hr style='border: none; border-top: 3px solid #00184C; margin: 15px 0;'>",
                unsafe_allow_html=True
            )

            show_radar_with_table(
                df_group=st.session_state.df_group, 
                df_unique=st.session_state.df_unique, 
                player_id=player_id_for_chart,  
                profile_name=st.session_state.selected_profile, 
                profiles=profiles,
                session_key='fig_radar_2'
                )

    else:
        st.warning("No se encontraron datos para el jugador seleccionado.")




# Función para calcular hash del archivo
def calculate_file_hash(file_data):
    return hashlib.md5(file_data).hexdigest()

# Función para guardar el archivo PDF
def save_pdf_file(pdf_data, player_id):
    """
    Guarda el PDF en la carpeta correspondiente al jugador.

    Args:
        pdf_data (bytes): Contenido binario del PDF.
        player_id (str): ID del jugador.

    Returns:
        str: Ruta donde se guardó el archivo.
    """
    # Crear la carpeta del jugador si no existe
    player_folder = os.path.join("data", "reports", f"player_{player_id}")
    os.makedirs(player_folder, exist_ok=True)

    # Generar nombre del archivo con fecha y hora
    current_time = datetime.now().strftime("%Y-%m-%d")
    file_name = f"{player_id}_automatizado_{current_time}.pdf"
    file_path = os.path.join(player_folder, file_name)

    # Convertir la ruta en absoluta
    file_path_absolute = os.path.abspath(file_path)

    # Guardar el archivo PDF
    with open(file_path, "wb") as f:
        f.write(pdf_data)

    return file_path_absolute, file_name


# Pestaña 5: Exportación a PDF
def show_tab5():
    st.markdown("## Exportación de Informe a PDF")
    add_vertical_space(1)

    if st.button("Generar Informe PDF"):
        # Generar el PDF para previsualización
        pdf_base64, pdf_data = generate_preview_pdf_content()

        # Guardar los datos del PDF en session_state para usarlos luego
        st.session_state['preview_pdf_data'] = pdf_data
        st.session_state['preview_pdf_base64'] = pdf_base64

        # Mostrar previsualización del PDF
        st.markdown("#### Previsualización del Informe:")
        pdf_viewer = f"""
            <iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px"></iframe>
        """
        st.markdown(pdf_viewer, unsafe_allow_html=True)

    # Verificar si hay un PDF generado para guardar
    if 'preview_pdf_data' in st.session_state:
        if st.button("Guardar Informe PDF"):
            # Guardar el PDF en el servidor
            pdf_data = st.session_state['preview_pdf_data']
            player_id = st.session_state.selected_player_id
            file_path, file_name = save_pdf_file(pdf_data, player_id)
            
            # Generar hash del archivo
            file_hash = calculate_file_hash(pdf_data)

            # Obtener usuario autenticado
            uploaded_by = st.session_state.get('username', 'unknown_user')

            # Obtener información adicional del jugador desde df_unique
            df_unique = st.session_state.df_unique
            player_data = df_unique.loc[df_unique['playerId'] == int(player_id)].iloc[0]
            player_name = f"{player_data['firstName']} {player_data['lastName']}"
            team_name = player_data['teamName']
            name_area = player_data['nameArea']

            # Registrar en el archivo CSV con "Automatizado" como tipo de informe
            selected_report_type = "Automatizado"
            log_uploaded_file(
                player_id, file_name, file_hash, file_path, 
                uploaded_by, selected_report_type,
                player_name, team_name, name_area
            )

            st.success(f"Informe guardado correctamente:\n\n- **Ruta**: {file_path}\n- **Jugador ID**: {player_id}")

            # Limpiar session_state
            del st.session_state['preview_pdf_data']
            del st.session_state['preview_pdf_base64']