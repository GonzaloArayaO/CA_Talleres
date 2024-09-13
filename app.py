import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from PIL import Image

from modules.data_preprocessing import preprocess_data
from modules.similar_players import similarPlayers
from modules.login import load_users, login_user, logout_user
from modules.bar_chart import bar_chart_player_stats


im = Image.open('resources/talleres_logo.png')

st.set_page_config(
    page_title='Scouting CA Talleres',
    page_icon=im
)

@st.cache_data
def load_data(file_path):
    df, df_unique, df_group = preprocess_data(file_path)
    return df, df_unique, df_group

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
            file_path = 'data/liga_argentina_player_stats.parquet'
            st.session_state.df, st.session_state.df_unique, st.session_state.df_group = load_data(file_path)

        df = st.session_state.df
        df_unique = st.session_state.df_unique
        df_group = st.session_state.df_group

        with st.sidebar:
            st.markdown('## Filtros')
            teams = df_unique['teamName'].unique()
            selected_team = st.selectbox('Selecciona el equipo', teams)

            df_filtered = df_unique[df_unique['teamName'] == selected_team]
            short_names = df_filtered['shortName'].unique()
            selected_short_name = st.selectbox('Selecciona el nombre del jugador', short_names)

            selected_player = df_filtered[df_filtered['shortName'] == selected_short_name].iloc[0]
            selected_player_id = selected_player['playerId']

            seasons_available = df_unique[(df_unique['playerId'] == selected_player_id) & (df_unique['teamName'] == selected_team)]['seasonName'].unique()
            selected_reference_season = st.selectbox('Selecciona la temporada de referencia', seasons_available)

            min_age = int(df_unique['age'].min())
            max_age = int(df_unique['age'].max())
            selected_age_range = st.slider('Selecciona el rango de edad', min_age, max_age, (min_age, max_age))

            # Calcular el máximo de minutos en campo para la temporada 2024
            max_minutes = df_group[df_group['seasonName'] == '2024']['minutesOnField'].max()

            # Filtro por porcentaje de minutos
            min_minutes_percentage = st.slider(f'% mínimo de minutos jugados\n\n{max_minutes} minutos máximo',
                0, 100, 0
            )

            min_minutes = (min_minutes_percentage / 100) * max_minutes

            # Mover el botón a la barra lateral
            buscar_similares = st.button('Buscar Jugadores Similares')

        if buscar_similares:
            try:
                # Buscar jugadores similares y filtrar por edad
                result_df, important_columns = similarPlayers(df_group, df_unique, selected_player_id, selected_reference_season)
                result_df = result_df[
                    (result_df['Edad'] >= selected_age_range[0]) & 
                    (result_df['Edad'] <= selected_age_range[1])
                    ]
                # Filtrar por minutos en campo
                result_df = result_df[result_df['minutesOnField'] >= min_minutes]

                # Guardar los resultados y columnas importantes en session_state
                st.session_state.result_df = result_df
                st.session_state.important_columns = important_columns
                st.session_state.selected_player_id = selected_player_id
                st.session_state.selected_reference_season = selected_reference_season
            except ValueError as e:
                st.error(e)
            except Exception as e:
                st.error(f"Error inesperado: {e}")

        # Mostrar los resultados o el mensaje si no se ha buscado aún
        if 'result_df' in st.session_state and 'important_columns' in st.session_state:
            # Primera fila: DataFrame a la izquierda y Markdown a la derecha
            col_left, col_right = st.columns([3, 1])

            with col_left:
                st.subheader('Resultados de Similitud', divider='blue')
                st.markdown('*- Sólo jugadores de temporada 2024.*')
                result_df_to_display = st.session_state.result_df.drop(columns=['playerId', 'minutesOnField'])
                st.dataframe(result_df_to_display)

            with col_right:
                add_vertical_space(5)
                important_columns_str = " - ".join(st.session_state.important_columns)
                st.write('**Columnas utilizadas en el análisis:**')
                st.write(f"*{important_columns_str}*")
                st.markdown(f":blue-background[{len(st.session_state.important_columns)} columnas utilizadas.]")

            st.subheader('', divider='blue')
            # Añadir selectbox para seleccionar un jugador del DataFrame de resultados
            selected_result_player = st.selectbox(
                'Selecciona un jugador para comparar',
                st.session_state.result_df['Nombre'].unique()
            )

            # Filtrar el DataFrame para obtener los datos del jugador seleccionado
            player_data_for_chart = st.session_state.result_df[st.session_state.result_df['Nombre'] == selected_result_player]
            if not player_data_for_chart.empty:
                player_id_for_chart = player_data_for_chart['playerId'].iloc[0]


            col_graph1, col_graph2 = st.columns(2)

            with col_graph1:
                st.plotly_chart(bar_chart_player_stats(
                    st.session_state.df_group, 
                    st.session_state.selected_player_id, 
                    st.session_state.important_columns,
                    st.session_state.selected_reference_season
                    ))
                
            with col_graph2:
                # Mostrar gráfico del jugador seleccionado
                st.plotly_chart(bar_chart_player_stats(
                st.session_state.df_group, 
                player_id_for_chart, 
                st.session_state.important_columns,
                selected_reference_season = '2024'
                ))


        else:
            # Mostrar mensaje si aún no se han buscado jugadores similares
            st.markdown('## Análisis de Similitud de Jugadores')
            add_vertical_space(2)
            st.markdown("""Selecciona los parámetros en Filtros y haz clic en **Buscar Jugadores Similares** 
                para ver los resultados.""")

if __name__ == "__main__":
    main()