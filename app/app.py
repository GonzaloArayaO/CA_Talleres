import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import pandas as pd
from PIL import Image

from modules.load_files import load_files
from modules.similar_players import similarPlayers
from modules.login import load_users, login_user, logout_user
from modules.bar_chart import bar_chart_player_stats

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

            # Filtro por posiciones (multiselect) usando df_positions
            available_positions = sorted(df_positions['position'].unique())  # Tomar todas las posiciones únicas de df_positions
            selected_positions = st.multiselect('Selecciona las posiciones', available_positions)

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

            # Filtro de cantidad de resultados
            num_results = st.selectbox('Cantidad de resultados:', options=[10, 20, 50, 100, 200, 500], index=1)

            # Mover el botón a la barra lateral
            buscar_similares = st.button('Buscar Jugadores Similares')

        if buscar_similares:
            try:
                result_df, important_columns = similarPlayers(
                    df_group, df_unique, df_positions, selected_player_id, selected_reference_season, 
                    target_seasons=['2024', '2023/2024', '2024/2025'], 
                    selected_positions=selected_positions, 
                    selected_nationalities=selected_nationalities, 
                    selected_age_range=selected_age_range, 
                    min_minutes=min_minutes, 
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

        # Verificación antes de acceder a datos en result_df
        if 'result_df' in st.session_state and not st.session_state.result_df.empty:
            # Primera fila: DataFrame a la izquierda y Markdown a la derecha
            col_left, col_right = st.columns([3, 1])

            with col_left:
                st.subheader('Resultados de Similitud', divider='blue')
                st.markdown('*- Sólo jugadores de temporada 2024.*')
                result_df_to_display = st.session_state.result_df.drop(columns=['playerId'])
                st.dataframe(result_df_to_display)

            with col_right:
                add_vertical_space(5)
                important_columns_str = " - ".join(st.session_state.important_columns)
                st.write('**Columnas utilizadas en el análisis:**')
                st.write(f"*{important_columns_str}*")
                st.markdown(f":blue-background[{len(st.session_state.important_columns)} columnas utilizadas.]")

        if not st.session_state.result_df.empty:
            # Selectbox para seleccionar un jugador del DataFrame de resultados
            selected_result_player = st.selectbox(
                'Selecciona un jugador para comparar',
                st.session_state.result_df['Nombre'].unique()
            )

            player_data_for_chart = st.session_state.result_df[
                st.session_state.result_df['Nombre'] == selected_result_player
            ]

            if not player_data_for_chart.empty:
                player_id_for_chart = player_data_for_chart['playerId'].iloc[0]
            else:
                st.warning("No se encontraron datos para el jugador seleccionado.")
                return

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


        else:
            st.markdown('## Análisis de Similitud de Jugadores')
            add_vertical_space(2)
            st.markdown("""Selecciona los parámetros en Filtros y haz clic en **Buscar Jugadores Similares** 
                        para ver los resultados.""")


if __name__ == "__main__":
    main()