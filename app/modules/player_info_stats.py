import streamlit as st
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space

from modules.pdf_exporter import style_table

def generate_player_info_stats(player_info, stats):
    """
    Genera un diseño estático del perfil del jugador en Streamlit.
    """
    # Obtener solo la fecha de nacimiento (sin hora)
    birth_date = str(player_info['birthDate'])[:10]

    # Mostrar información del jugador
    st.markdown(f"""
    <div style="text-align: left; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <!-- Foto del jugador -->
            <div style="display: flex; align-items: center;">
                <img src="{player_info['imageDataURL']}" alt="Foto del jugador" style="width: 100px; height: 100px; border-radius: 50%; margin-right: 20px; border: 1px solid #ccc;">
                <div>
                    <h1 style="margin: 0; padding: 0; font-size: 30px; text-align: center;">{player_info['firstName']} {player_info['lastName']}</h1>
                </div>
            </div>
            <!-- Foto del equipo -->
            <div>
                <img src="{player_info['teamImageDataURL']}" alt="Logo del equipo" style="width: 80px; height: 80px;">
            </div>
        </div>
        <!-- Información adicional en 2 columnas -->
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <div style="flex: 1; margin-right: 10px;">
                <p style="margin: 0px; font-size: 14px;"><strong>Equipo:</strong> {player_info['teamName']}</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Competencia:</strong> {player_info['competitionName']} - {player_info['nameArea']}</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Posición:</strong> {player_info['nameRole']} - {player_info['code2Role']}</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Nacionalidad:</strong> {player_info['nameBirthArea']} ({player_info['namePassportArea']})</p>
            </div>
            <div style="flex: 1; margin-left: 10px;">
                <p style="margin: 0px; font-size: 14px;"><strong>Edad:</strong> {player_info['age']} años ({birth_date})</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Peso:</strong> {player_info['weight']} kg</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Altura:</strong> {player_info['height']} cm</p>
                <p style="margin: 0px; font-size: 14px;"><strong>Pie dominante:</strong> {player_info['foot']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    add_vertical_space()

    # Convertir el diccionario stats en un DataFrame
    stats_df = pd.DataFrame(stats, index=[0])
    stats_df.rename(columns={
        'matchesTotal': 'Partidos jugados',
        'matchesInStartTotal': 'Titular',
        'minutesOnFieldTotal': 'Minutos',
        'yellowCardsTotal': 'Tarjetas amarillas',
        'redCardsTotal': 'Tarjetas rojas',
        'assistsTotal': 'Asistencias',
        'goalsTotal': 'Goles'
        }, inplace=True)

    styled_table_html = style_table(stats_df, for_pdf=False, for_info=True).to_html()

    # Mostrar la tabla en Streamlit
    st.markdown(styled_table_html, unsafe_allow_html=True)