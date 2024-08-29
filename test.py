import streamlit as st

from modules.data_preprocessing import preprocess_data
from modules.similar_players import similarPlayers
from modules.login import load_users, login_user, logout_user

from PIL import Image

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

    col1, col2, col3 = st.columns([20, 60, 20])
    with col1:
        st.image('https://cdn5.wyscout.com/photos/team/public/1100_120x120.png', width=60)

    st.title('Scouting CA Talleres')

    with col3:
        st.image('resources/sdc_logo.png', width=125)

    users = load_users()

    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'username': '',
            'password': '',
            'logged_in': False
        }

    if not st.session_state.user_state['logged_in']:
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

        # Cargar y preprocesar los datos usando el cache
        # with st.spinner('Cargando datos...'):
        file_path = 'data/liga_argentina_player_stats.parquet'
        df, df_unique, df_group = load_data(file_path)

        st.header('Análisis de Similitud de Jugadores')

        with st.sidebar:
            st.header('Filtros')
            teams = df_unique['teamName'].unique()
            selected_team = st.selectbox('Selecciona el equipo', teams)

            df_filtered = df_unique[df_unique['teamName'] == selected_team]
            short_names = df_filtered['shortName'].unique()
            selected_short_name = st.selectbox('Selecciona el nombre del jugador', short_names)

            selected_player = df_filtered[df_filtered['shortName'] == selected_short_name].iloc[0]
            selected_player_id = selected_player['playerId']

            seasons_available = df_unique[(df_unique['playerId'] == selected_player_id) & (df_unique['teamName'] == selected_team)]['seasonName'].unique()
            st.write(f"Temporadas disponibles para {selected_short_name}: {seasons_available}")

            selected_reference_season = st.selectbox('Selecciona la temporada de referencia', seasons_available)

            min_age = int(df_unique['age'].min())
            max_age = int(df_unique['age'].max())
            selected_age_range = st.slider('Selecciona el rango de edad', min_age, max_age, (min_age, max_age))

            if st.button('Buscar Jugadores Similares'):
                try:
                    result_df, important_columns = similarPlayers(df_group, df_unique, selected_player_id, selected_reference_season)
                    result_df = result_df[(result_df['Edad'] >= selected_age_range[0]) & (result_df['Edad'] <= selected_age_range[1])]
                    st.session_state.result_df = result_df
                    st.session_state.important_columns = important_columns
                except ValueError as e:
                    st.error(e)
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

        if 'result_df' in st.session_state:
            important_columns_str = " - ".join(st.session_state.important_columns)
            st.write('**Columnas utilizadas:**')
            st.write(f"Se utilizaron {len(st.session_state.important_columns)} columnas\n\n {important_columns_str}")
            st.dataframe(st.session_state.result_df)
        else:
            st.write("""Selecciona los parametros en Filtros y haz clic en 'Buscar Jugadores Similares' 
            para ver los resultados.""")

if __name__ == "__main__":
    main()