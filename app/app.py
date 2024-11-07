import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import pandas as pd
from PIL import Image

from modules.load_files import load_files
from modules.similar_players import similarPlayers
from modules.login import load_users, login_user, logout_user
from modules.bar_chart import bar_chart_player_stats
from modules.player_profile import get_player_profiles
from modules.radar_chart import show_radar_with_table
from modules.positions import get_position_mapping

# Configuracion pagina
im = Image.open('resources/talleres_logo.png')
st.set_page_config(
    page_title='Scouting CA Talleres',
    page_icon=im
)

# Inicialización de variables en session_state
if 'result_df' not in st.session_state:
    st.session_state.result_df = pd.DataFrame()
if 'important_columns' not in st.session_state:
    st.session_state.important_columns = []
if 'selected_player_id' not in st.session_state:
    st.session_state.selected_player_id = None
if 'selected_reference_season' not in st.session_state:
    st.session_state.selected_reference_season = None
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'username': '',
        'password': '',
        'logged_in': False
    }

def main():

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image('resources/talleres_logo.png', width=70)

    with col3:
        st.image('resources/sdc_logo_hor.png')

    users = load_users()

    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'username': '',
            'password': '',
            'logged_in': False
        }

    if not st.session_state.user_state['logged_in']:

        add_vertical_space(2)
        st.markdown('## Scouting - CA Talleres')

        username = st.text_input('Usuario')
        password = st.text_input('Contraseña', type='password')
        submit = st.button('Iniciar sesión')

        if submit:
            if login_user(users, username, password):
                st.rerun()
            else:
                st.warning('Usuario / contraseña incorrecto')
    else:

        with col3:
            if st.button('Cerrar sesión'):
                logout_user()
                st.rerun()

        if 'df' not in st.session_state:
            st.session_state.df_group, st.session_state.df_unique, st.session_state.df_positions = load_files()

            df_group = st.session_state.df_group
            df_unique = st.session_state.df_unique
            df_positions = st.session_state.df_positions

        with st.sidebar:
            st.markdown('## Filtros')

            # Filtro de pais
            countries = sorted(df_unique['nameArea'].unique())
            selected_country = st.selectbox('Selecciona el pais', countries)
            df_countries = df_unique[df_unique['nameArea'] == selected_country]

            # Filtro de competencia
            leagues = sorted(df_countries['competitionName'].unique())
            selected_league = st.selectbox('Selecciona la liga', leagues)
            df_leagues = df_unique[(df_unique['competitionName'] == selected_league) & (df_unique['nameArea'] == selected_country)]

            # Filtro de equipo
            teams = sorted(df_leagues['teamName'].unique())
            selected_team = st.selectbox('Selecciona el equipo', teams)
            df_filtered = df_unique[df_unique['teamName'] == selected_team]

            # Filtro de jugador
            short_names = sorted(df_filtered['shortName'].unique())
            selected_short_name = st.selectbox('Selecciona el nombre del jugador', short_names)
            selected_player = df_filtered[df_filtered['shortName'] == selected_short_name].iloc[0]
            selected_player_id = selected_player['playerId']

            # Filtro de temporada disponible
            seasons_available = df_unique[(df_unique['playerId'] == selected_player_id) & (df_unique['teamName'] == selected_team)]['seasonName'].unique()
            selected_reference_season = st.selectbox('Selecciona la temporada de referencia', seasons_available)

            # Obtener el diccionario de posiciones
            position_mapping = get_position_mapping()

            # Filtro de posición primaria
            primary_positions = position_mapping.keys()
            selected_primary_positions = st.multiselect("Selecciona la posición primaria", primary_positions)

            # Filtro de posición secundaria basado en la posición primaria seleccionada
            if selected_primary_positions:
                # Obtén las posiciones secundarias correspondientes
                secondary_positions = []
                for primary in selected_primary_positions:
                    secondary_positions.extend(position_mapping[primary])
                secondary_positions = sorted(set(secondary_positions))  # Eliminar duplicados y ordenar

                # Filtro de posición secundaria
                selected_secondary_positions = st.multiselect("Selecciona las posiciones secundarias", secondary_positions)
            else:
                selected_secondary_positions = []


            # Filtro por posiciones (multiselect) usando df_positions
            # available_positions = sorted(df_positions['position'].unique())  # Tomar todas las posiciones únicas de df_positions
            # selected_positions = st.multiselect('Selecciona las posiciones', available_positions)

            # Filtro de nacionalidad y pasaporte
            nationalities = sorted(df_unique[['nameBirthArea', 'namePassportArea']].stack().unique())
            selected_nationalities = st.multiselect('Selecciona nacionalidades/pasaporte', nationalities)

            # Filtro de edad
            min_age = int(df_unique['age'].min())
            max_age = int(df_unique['age'].max())
            selected_age_range = st.slider('Selecciona el rango de edad', min_age, max_age, (min_age, max_age))

            # Calcular el máximo de minutos jugados por cualquier jugador en todas las temporadas
            max_minutes = df_group['minutesOnFieldTotal'].max()

            # Crear un slider para filtrar por un mínimo de minutos jugados, moviéndose en pasos de 50
            min_minutes = st.slider(
                f'Minutos mínimos jugados (hasta un máximo de {max_minutes} minutos)',
                min_value=0,
                max_value=int(max_minutes),  # Convertir a entero porque el slider no soporta flotantes
                step=50,
            )

            # Filtro de País de competencia
            countries_output = sorted(df_unique['nameArea'].unique())
            selected_countries_output = st.multiselect('Selecciona países para filtrar', countries_output)

            # Filtro de Competencia basado en el país seleccionado
            if selected_countries_output:
                df_filtered_output = df_unique[df_unique['nameArea'].isin(selected_countries_output)]
                competitions_output = sorted(df_filtered_output['competitionName'].unique())
                selected_competitions_output = st.multiselect('Selecciona competencias para filtrar', competitions_output)
            else:
                selected_competitions_output = []

            # Filtro de cantidad de resultados
            num_results = st.selectbox('Cantidad de resultados:', options=[10, 20, 50, 100, 200, 500], index=1)

            # Mover el botón a la barra lateral
            buscar_similares = st.button('Buscar Jugadores Similares')

        if buscar_similares:
            try:
                result_df, important_columns = similarPlayers(
                    df_group=df_group, 
                    df_unique=df_unique, 
                    df_positions=df_positions, 
                    playerId=selected_player_id, 
                    reference_season=selected_reference_season, 
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

                # Guardar resultados en session_state
                st.session_state.result_df = result_df
                st.session_state.important_columns = important_columns
                st.session_state.selected_player_id = selected_player_id
                st.session_state.selected_reference_season = selected_reference_season

            except ValueError as e:
                st.warning(str(e))  # Mostrar un mensaje amigable si no se encuentran resultados
            except Exception as e:
                st.error(f"Error inesperado: {e}")

        # Crear pestañas para mostrar los resultados
        tab1, tab2, tab3 = st.tabs(['Tabla similitud', 'Gráfico de barras comparación', 'Perfiles de juego'])

        # Pestaña 1: Tabla
        with tab1:
            # Verificación antes de acceder a datos en result_df
            if not st.session_state.result_df.empty:
                # Primera fila: DataFrame a la izquierda y Markdown a la derecha
                col_left, col_right = st.columns([3, 2])

                with col_left:
                    st.subheader('Resultados de Similitud', divider='blue')
                    st.markdown('*- Sólo jugadores de temporada 2024.*')
                    result_df_to_display = st.session_state.result_df.drop(columns=['playerId'], errors='ignore')
                    result_df_to_display['% Similitud'] = result_df_to_display['% Similitud'].apply(lambda x: f'{x:.2f}')
                    # Aplicar estilo personalizado al DataFrame
                    styled_table = (
                        result_df_to_display.style
                        .set_table_styles(
                            [  # Estilos para el encabezado sin borde exterior
                                {'selector': 'thead th', 'props': [('padding', '2px')]},
                                # Celdas con tamaño ajustado al contenido y sin bordes
                                {'selector': 'th, td', 'props': [('font-size', '13px'), ('border', 'none'), ('padding', '2px 5px')]}
                            ]
                        )
                    )

                    # Renderizar tabla en HTML en Streamlit
                    st.markdown(styled_table.to_html(), unsafe_allow_html=True) 

                with col_right:
                    with st.expander("#### Columnas utilizadas en el análisis", expanded=True):
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


        # Pestaña 2: Gráfico de Barras
        with tab2:
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

                    col_graph1, col_graph2 = st.columns(2)

                    # Primer gráfico: todas las temporadas relevantes
                    with col_graph1:
                        st.plotly_chart(bar_chart_player_stats(
                            st.session_state.df_group,
                            st.session_state.selected_player_id,
                            st.session_state.important_columns,
                            st.session_state.selected_reference_season
                        ))

                    # Segundo gráfico: solo el jugador seleccionado
                    with col_graph2:
                        st.plotly_chart(bar_chart_player_stats(
                            st.session_state.df_group,
                            player_id_for_chart,
                            st.session_state.important_columns
                        ))

                    # Guardar en session_state para usar en el radar chart
                    st.session_state.player_id_for_chart = player_id_for_chart
                else:
                    st.warning("No se encontraron datos para el jugador seleccionado.")
                    st.session_state.player_id_for_chart = None  # Inicializar si no hay jugador

        # Pestaña 3: Radar Chart
        with tab3:
            profiles = get_player_profiles()
            selected_profile = st.selectbox('Selecciona un perfil de juego', list(profiles.keys()))

            # Verificar si player_id_for_chart está disponible
            player_id_for_chart = st.session_state.get('player_id_for_chart')

            if player_id_for_chart is not None:
                # Mostrar radar chart para el jugador seleccionado
                show_radar_with_table(
                    df_group=df_group, 
                    df_unique=df_unique, 
                    player_id=st.session_state.selected_player_id, 
                    profile_name=selected_profile, 
                    profiles=profiles
                )

                # Mostrar radar chart para el jugador base
                show_radar_with_table(
                    df_group=df_group, 
                    df_unique=df_unique, 
                    player_id=player_id_for_chart,  
                    profile_name=selected_profile, 
                    profiles=profiles
                )

if __name__ == "__main__":
    main()