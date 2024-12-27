import pdfkit
import base64
import streamlit as st
import io
import os
import pandas as pd
import requests
from PIL import Image
from datetime import datetime
import plotly.io as pio
from modules.player_profile import get_player_profiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def style_table(dataframe, for_pdf=False, for_info=False):
    """
    Aplica estilo a un DataFrame. Ajusta el estilo para PDF o Streamlit.
    
    Args:
        dataframe (pd.DataFrame): DataFrame a estilizar.
        for_pdf (bool): Si es True, aplica estilos para PDF, si es False aplica estilos para Streamlit.
        
    Returns:
        styled_table (pd.Styler): El DataFrame estilizado.
    """
    table_styles = [
        {'selector': 'thead th', 'props': [('padding', '5px'), 
                                           ('background-color', '#00184C'), 
                                           ('color', 'white'),
                                           ('border', '2px solid #00184C'), 
                                           ('font-weight', 'bold'),
                                           ('font-size', '13px' if for_pdf else '12px'),
                                           ('white-space', 'nowrap')]},
        {'selector': 'tbody td', 'props': [('padding', '6px' if for_pdf else '5px'), 
                                           ('font-size', '12px' if for_pdf else '11px'),
                                           ('text-align', 'center'),
                                           ('border', '1px solid #ddd')]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f7f7f7')]},
        {'selector': '.row_heading', 'props': [('font-weight', 'normal'),
                                            ('font-size', '12px' if for_pdf else '11px'),
                                            ('text-align', 'center'),
                                            ('padding', '6px' if for_pdf else '5px'),
                                            ('background-color', '#00184C'),
                                            ('color', 'white'), 
                                            ('font-weight', 'bold')]}
    ]
    
    # Aplicar estilos al DataFrame
    styled_table = dataframe.style.set_table_styles(table_styles)

    # Ocultar el índice si for_info es True
    if for_info:
        styled_table = styled_table.hide(axis='index')

    if for_info:
        styled_table = styled_table.set_table_attributes(
           'style="margin-left: auto; margin-right: auto; border-collapse: collapse; max-width: 95%;"'
        )


    return styled_table


def get_common_html_styles():
    """
    Retorna los estilos comunes que serán usados en el PDF.
    """
    return """
        body {
            font-family: 'Arial', sans-serif;
            color: #333;
            line-height: 1.5;
            padding: 25px;
        }
        h1 {
            color: #000000;
            border-bottom: 2px solid #00184C;
            padding-bottom: 5px;
            font-size: 25px;
            text-align: left;
        }
        p {
            font-size: 14px;
            color: #555;
            margin-top: 5px;
            margin-bottom: 20px;
        }
        table {
            max-width: 100%;
            border-collapse: collapse;
            marginp: auto;
            font-size: 12px;
        }
        .table-container {
            margin-bottom: 30px;
        }
        .important-columns {
            font-size: 11px;
        }
    """


def generate_tab1_content():
    """
    Genera el contenido específico para la pestaña 1.
    """
    if st.session_state.result_df.empty:
        return "<p>No hay datos para mostrar.</p>"

    # Generar tabla y contenido adicional
    result_df_to_display = st.session_state.result_df.drop(columns=['playerId'], errors='ignore')
    styled_table_html = style_table(result_df_to_display, for_pdf=True).to_html()
    important_columns_str = " - ".join(st.session_state.important_columns)

    # Retornar solo el contenido
    return f"""
        <header>
            <h1>Resultados de Similitud de Jugadores</h1>
            <p>- Jugadores con estadísticas de la temporada actual.</p>
        </header>
        <section class="table-container">
            {styled_table_html}
        </section>
        <section class="important-columns">
            <h2>Columnas utilizadas en el análisis:</h2>
            <p>{important_columns_str}</p>
        </section>
    """



def url_to_base64_image(url):
    """
    Convierte una URL de imagen a formato base64.

    Args:
        url (str): URL de la imagen.

    Returns:
        str: Imagen en formato base64, o un string vacío si falla.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")  # Cambia a JPG si es necesario
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir la imagen a Base64: {e}")
        return ""  # Devuelve un string vacío si ocurre un error

import base64


def image_to_base64(image_path):
    """
    Convierte una imagen a formato Base64.

    Args:
        image_path (str): Ruta de la imagen.

    Returns:
        str: Imagen en formato Base64.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir la imagen a Base64: {e}")
        return None



def generate_tab2_content():
    """
    Genera el contenido específico para la pestaña 2 (Ficha del jugador).
    """
    # Verificar que haya datos
    if st.session_state.df_group.empty or st.session_state.df_unique.empty:
        return "<p>No hay datos disponibles para generar la ficha del jugador.</p>"

    # Obtener información del jugador y estadísticas
    player_id = st.session_state.selected_player_id
    player_info = st.session_state.df_unique.loc[
        st.session_state.df_unique['playerId'] == player_id
    ].iloc[0].to_dict()
    player_info['imageDataBase64'] = url_to_base64_image(player_info['imageDataURL'])
    player_info['teamImageDataBase64'] = url_to_base64_image(player_info['teamImageDataURL'])

    stats_info = ['matchesTotal', 'matchesInStartTotal', 'minutesOnFieldTotal', 
                  'yellowCardsTotal', 'redCardsTotal', 'assistsTotal', 'goalsTotal']
    stats = st.session_state.df_group.loc[
        st.session_state.df_group['playerId'] == player_id
    ][stats_info].iloc[0].to_dict()

    # Formatear fecha de nacimiento
    birth_date = str(player_info['birthDate'])[:10]

    # Generar tabla de métricas
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

    styled_table_html = style_table(stats_df, for_pdf=True, for_info=True).to_html()

    # Convertir la imagen a Base64
    logo_base64 = image_to_base64(os.path.join(BASE_DIR, '..','resources','sdc_logo_hor.png'))

    # Crear una sección de filtros utilizados
    filters_used = f"""
        <div style="margin-top: 30px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; text-align: left;">
            <h3 style="margin-top: 0; font-size: 14px; color: #333;">Filtros utilizados para buscar jugadores similares a {player_info['shortName']}:</h3>
            <ul style="font-size: 13px; color: #333;">

                <li><strong>Posiciones primarias seleccionadas:</strong> {', '.join(st.session_state.get('selected_primary_positions', [])) or 'No seleccionado'}</li>
                <li><strong>Posiciones secundarias seleccionadas:</strong> {', '.join(st.session_state.get('selected_secondary_positions', [])) or 'No seleccionado'}</li>
                <li><strong>Nacionalidades o Pasaporte seleccionadas:</strong> {', '.join(st.session_state.get('selected_nationalities', [])) or 'No seleccionado'}</li>
                <li><strong>Rango de edad:</strong> {f"{st.session_state.get('selected_age_range', (0, 0))[0]} - {st.session_state.get('selected_age_range', (0, 0))[1]}"}</li>
                <li><strong>Mínimo de minutos jugados:</strong> {st.session_state.get('min_minutes', 0)}</li>
                <li><strong>Países de competencia a buscar:</strong> {', '.join(st.session_state.get('selected_countries_output', [])) or 'No seleccionado'}</li>
                <li><strong>Competencias a buscar:</strong> {', '.join(st.session_state.get('selected_competitions_output', [])) or 'No seleccionado'}</li>
                <li><strong>Cantidad de resultados mostrados:</strong> {st.session_state.get('num_results', 'No seleccionado')}</li>
            </ul>
        </div>
    """

    # Generar contenido HTML
    return f"""
    <div style="text-align: left; padding: 15px; margin-bottom: 30px; page-break-after: always;">

        <!-- Logo institucional en la esquina superior izquierda -->
        <img src="data:image/png;base64,{logo_base64}" alt="Logo institucional" 
            style="position: absolute; top: 10px; right: 15px; width: 100px; height: auto;">

        <header style="text-align: left; margin-bottom: 100px; margin-top: 50px;">
            <h1 style="margin-bottom: 10px; font-size: 30px; color: #00184C;">Informe scouting automatizado</h1>
            <p style="text-align: right; margin-bottom: 10px; margin-top: 10px; font-size: 12px; color: #777;">Generado automáticamente. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="width: 20%; text-align: center;">
                    <img src="data:image/png;base64,{player_info['imageDataBase64']}" alt="Foto del jugador" 
                        style="width: 100px; height: 100px; border-radius: 50%; border: 1px solid #ccc;">
                </td>
                <td style="width: 60%; text-align: center;">
                    <p style="margin: 0; font-size: 30px; font-weight: bold; color: #333;">{player_info['firstName']} {player_info['lastName']}</p>
                </td>
                <td style="width: 20%; text-align: center;">
                    <img src="data:image/png;base64,{player_info['teamImageDataBase64']}" alt="Logo del equipo" 
                        style="width: 80px; height: 80px; border-radius: 10px;">
                </td>
            </tr>
        </table>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr>
                <!-- Columna izquierda -->
                <td style="width: 50%; padding: 10px; vertical-align: top;">
                    <p style="margin: 0px; font-size: 14px;"><strong>Equipo:</strong> {player_info['teamName']}</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Competencia:</strong> {player_info['competitionName']} - {player_info['nameArea']}</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Posición:</strong> {player_info['nameRole']} - {player_info['code2Role']}</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Nacionalidad:</strong> {player_info['nameBirthArea']} ({player_info['namePassportArea']})</p>
                </td>
                <!-- Columna derecha -->
                <td style="width: 50%; padding: 10px; vertical-align: top;">
                    <p style="margin: 0px; font-size: 14px;"><strong>Edad:</strong> {player_info['age']} años ({birth_date})</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Peso:</strong> {player_info['weight']} kg</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Altura:</strong> {player_info['height']} cm</p>
                    <p style="margin: 0px; font-size: 14px;"><strong>Pie dominante:</strong> {player_info['foot']}</p>
                </td>
            </tr>
        </table>
        <div style="margin-top: 20px; text-align: center;">
            <div style="display: inline-block;">
                {styled_table_html}
            </div>
            <!-- Sección de filtros utilizados -->
            {filters_used}
        </div>
    </div>
    """



def export_chart_as_png(fig, filename="chart.png", width=600, height=800, scale=5):
    """
    Guarda un gráfico de Plotly como archivo PNG.
    
    Args:
        fig (plotly.graph_objs.Figure): El gráfico a guardar.
        filename (str): Nombre del archivo.
        width (int): Ancho del archivo exportado.
        height (int): Altura del archivo exportado.
        scale (int): Escala del archivo exportado.
    
    Returns:
        str: Ruta completa del archivo guardado.
    """
    try:
        fig.write_image(filename, width=width, height=height, scale=scale)
        return filename
    except Exception as e:
        print(f"Error al guardar el gráfico: {e}")
        return None



def generate_tab3_content():
    """
    Genera el contenido específico para la pestaña 3.
    """
    # Verificar si los gráficos están disponibles
    bar_chart_left = st.session_state.get("bar_chart_left", None)
    bar_chart_right = st.session_state.get("bar_chart_right", None)

    if not bar_chart_left or not bar_chart_right:
        return "<p>No hay gráficos disponibles para mostrar.</p>"

    # Convertir gráficos en imágenes base64
    left_file = export_chart_as_png(bar_chart_left, filename="chart_left.png")
    right_file = export_chart_as_png(bar_chart_right, filename="chart_right.png")

    left_image_base64 = image_to_base64(left_file)
    right_image_base64 = image_to_base64(right_file)

    # Retornar contenido
    html_content = f"""
        <header>
            <h1>Gráficos de barra comparación de jugadores</h1>
            <p>- Comparación entre el jugador buscado y el jugador seleccionado, utilizando el total de métricas escogidas por algoritmo.</p>
        </header>
        <section class="chart-container">
            <table style="width: 100%; text-align: center; border-collapse: collapse;">
                <tr>
                    <td style="width: 50%; padding: 0px;">
                        <img src="data:image/png;base64,{left_image_base64}" alt="Gráfico de barras izquierda" style="width: 100%; height: auto;">
                    </td>
                    <td style="width: 50%; padding: 0px;">
                        <img src="data:image/png;base64,{right_image_base64}" alt="Gráfico de barras derecha" style="width: 100%; height: auto;">
                    </td>
                </tr>
            </table>
        </section>
    """
    os.remove(left_file)
    os.remove(right_file)

    return html_content


def prepare_chart_for_export(fig):
    """
    Ajusta un radar chart para exportarlo con márgenes personalizados.

    Args:
        fig (go.Figure): Gráfico de radar original.

    Returns:
        go.Figure: Gráfico ajustado para exportación.
    """
    fig_export = fig  # Clonar el gráfico si es necesario
    fig_export.update_layout(
        margin=dict(
            t=75,  # Mayor margen superior
            b=50,  # Mayor margen inferior
            l=100,  # Mayor margen izquierdo
            r=100   # Mayor margen derecho
        ),
        width=450,  # Ajusta el tamaño total para la exportación
        height=450
    )
    return fig_export

def export_radar_chart_as_png(fig, filename="radar_chart.png"):
    """
    Exporta un radar chart de Plotly a un archivo PNG.

    Args:
        fig (go.Figure): Gráfico de radar.
        filename (str): Nombre del archivo a exportar.

    Returns:
        str: Ruta del archivo PNG generado.
    """
    try:
        fig_for_export = prepare_chart_for_export(fig)

        pio.write_image(fig_for_export, filename, format='png', width=500, height=500)
        return filename
    except Exception as e:
        print(f"Error al exportar el radar chart a PNG: {e}")
        return None
    
def generate_radar_chart_html(fig, df_table):
    """
    Genera el contenido HTML del radar chart y la tabla.

    Args:
        fig (go.Figure): Gráfico de radar.
        df_table (pd.DataFrame): DataFrame con los datos de la tabla.
        title (str): Título para el bloque HTML.

    Returns:
        str: Contenido HTML que combina el radar chart y la tabla.
    """
    # Exportar gráfico como imagen
    radar_file = export_radar_chart_as_png(fig)
    radar_image_base64 = image_to_base64(radar_file) if radar_file else ""

    # Generar tabla HTML estilizada
    styled_table_html = style_table(df_table, for_info=True).to_html(index=False)

    # Combinar contenido en HTML
    html_content = f"""
        <section class="chart-container">
            <img src="data:image/png;base64,{radar_image_base64}" alt="Radar Chart" style="width: 100%; height: auto;">
        </section>
        <section class="table-container">
            {styled_table_html}
        </section>
    """
    # Eliminar archivo temporal
    if radar_file:
        os.remove(radar_file)

    return html_content

def calculate_prom_league(df_group, metrics, season_id):
    metrics_league = df_group[df_group['seasonId'] == season_id]
    prom_league = metrics_league.groupby('seasonId').mean(numeric_only=True).reset_index().round(3) # Promedios metricas de liga
    prom_league = prom_league[metrics]
    return prom_league

def export_radar_chart_and_table_to_html(player_id, profile_name, profiles, session_key="fig_radar_1"):
    """
    Exporta el radar chart y la tabla para un jugador en formato HTML.

    Args:
        player_id (int): ID del jugador.
        profile_name (str): Nombre del perfil de métricas.
        profiles (dict): Diccionario con perfiles y métricas asociadas.
        session_key (str): Clave de sesión para recuperar el gráfico.

    Returns:
        str: Contenido HTML del radar chart y la tabla.
    """
    # Verificar si la figura existe en session_state
    fig = st.session_state.get(session_key, None)
    if not fig:
        return "<p>No se encontró el gráfico de radar en la sesión.</p>"

    # Recuperar los datos del jugador
    df_group = st.session_state.df_group
    df_unique = st.session_state.df_unique
    metrics = profiles[profile_name]

    # Generar tabla de métricas
    player_info = df_unique[df_unique['playerId'] == player_id].iloc[0]
    player_data = df_group[df_group['playerId'] == player_id][metrics].iloc[0]
    df_table = pd.DataFrame({
        "Métrica": player_data.index,
        "Valor": player_data.values
    })
    df_table['Valor'] = df_table['Valor'].apply(lambda x: f'{x:.2f}')

    season_id = player_info['seasonId']
    prom_league = calculate_prom_league(df_group, metrics, season_id)
    prom_league = prom_league.iloc[0].values  # Extraer valores de la fila correspondiente
    df_table['Prom liga'] = prom_league
    df_table['Prom liga'] = df_table['Prom liga'].apply(lambda x: f'{x:.2f}')

    # Generar HTML del radar chart y la tabla
    return generate_radar_chart_html(fig, df_table)


def generate_tab4_content():
    """
    Genera el contenido para la pestaña 4 (Radar Charts) en el informe PDF.
    """

    profile_name = st.session_state.selected_profile

    # Verificar si el radar chart y tabla están disponibles en session_state
    radar1_html = export_radar_chart_and_table_to_html(
        player_id=st.session_state.selected_player_id,
        profile_name=st.session_state.selected_profile,
        profiles=get_player_profiles(),
        session_key="fig_radar_1"
    )

    radar2_html = export_radar_chart_and_table_to_html(
        player_id=st.session_state.get("player_id_for_chart"),
        profile_name=st.session_state.selected_profile,
        profiles=get_player_profiles(),
        session_key="fig_radar_2"
    )

    # Verificar que el contenido sea válido
    if not radar1_html or not radar2_html:
        return "<p>No hay gráficos ni tablas disponibles para mostrar.</p>"

    # Crear contenido HTML final
    html_content = f"""
        <header>
            <h1>Radar Chart de Perfiles de Juego</h1>
            <p>Comparación de perfiles de juego basada en métricas seleccionadas.</p>
            <p style="text-align: center; font-size: 18px;">Perfil de juego seleccionado: <b>{profile_name}</b></p>
        </header>
        <section class="chart-container">
            <table style="width: 100%; text-align: center; border-collapse: collapse;">
                <tr>
                    <td style="width: 50%; padding: 10px;">
                        {radar1_html}
                    </td>
                    <td style="width: 50%; padding: 10px;">
                        {radar2_html}
                    </td>
                </tr>
            </table>
        </section>
    """
    return html_content



def generate_full_html():
    """
    Genera el HTML unificado para todas las pestañas.
    """
    tab2_content = generate_tab2_content()
    tab1_content = generate_tab1_content()
    tab3_content = generate_tab3_content()
    tab4_content = generate_tab4_content()

    # Combinar el contenido con los estilos comunes
    full_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {get_common_html_styles()}
        </style>
    </head>
    <body>
        <section>
            {tab2_content}
        </section>
        <section>
            {tab1_content}
        </section>
        <section style="page-break-before: always;">
            {tab3_content}
        </section>
        <section style="page-break-before: always;">
            {tab4_content}
        </section>
    </body>
    </html>
    """
    return full_html


### Guardado de reporte automatizado

def generate_preview_pdf_content():
    """
    Genera el contenido del PDF para previsualización.

    Returns:
        Tuple: PDF codificado en base64 y el contenido binario del PDF.
    """
    html_content = generate_full_html()
    # Convertir HTML a PDF en memoria (sin guardarlo en disco)
    options = {
        'encoding': "UTF-8",
        'enable-local-file-access': '',
        'quiet': ''
    }
    pdf_data = pdfkit.from_string(html_content, False, options=options)  # False genera en memoria
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    return pdf_base64, pdf_data


def save_pdf_file(pdf_data, player_id):
    """
    Guarda el PDF en un directorio organizado por el ID del jugador.

    Args:
        pdf_data (bytes): Contenido binario del PDF.
        player_id (str): ID único del jugador.

    Returns:
        str: Ruta completa del archivo PDF generado.
    """
    # Crear el directorio del jugador si no existe
    player_dir = os.path.join(BASE_DIR,'..', 'data','reports',f"player_{player_id}")
    os.makedirs(player_dir, exist_ok=True)

    # Crear el nombre del archivo basado en la fecha actual
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_filename = os.path.join(player_dir, f"{player_id}_automatizado_{current_date}.pdf")

    # Escribir el PDF en el archivo
    with open(output_filename, "wb") as pdf_file:
        pdf_file.write(pdf_data)

    return output_filename