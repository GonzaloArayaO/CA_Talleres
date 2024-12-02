import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def bar_chart_player_stats(df_group, df_unique, player_id, important_columns, selected_reference_season=None, x_max=None):
    # Si no se pasan temporadas, tomar todos los registros del jugador.
    if selected_reference_season is None:
        player_data = df_group[df_group['playerId'] == player_id][important_columns]
        minutes_played = df_group[df_group['playerId'] == player_id]['minutesOnFieldTotal'].sum()
    else:
        player_data = df_group[(df_group['playerId'] == player_id) & (df_group['seasonName'] == selected_reference_season)][important_columns]
        minutes_played = df_group[
            (df_group['playerId'] == player_id) & 
            (df_group['seasonName'] == selected_reference_season)
            ]['minutesOnFieldTotal'].sum()

    if player_data.empty:
        raise ValueError(f"No se encontraron métricas para el jugador en las temporadas seleccionadas.")

    # Obtener los nombres de las columnas y sus respectivos valores
    columns = player_data.columns
    columns = [f"{col} " for col in player_data.columns]
    values = player_data.iloc[0].values  # Obtener la primera fila (que corresponde al jugador seleccionado)
    
    # Parametro no usado para añadir informacion del jugador
    player_data = df_unique[df_unique['playerId'] == player_id].iloc[0]

    player_name = df_group[df_group['playerId'] == player_id]['shortName'].iloc[0]
    season = df_group[df_group['playerId'] == player_id]['seasonName'].iloc[0]

    # Calcular la altura del gráfico en función del número de barras
    num_metrics = len(columns)
    height_per_bar = 30
    height = max(400, num_metrics * height_per_bar)

    if x_max is None:
        x_max = max(values) * 1.1

    # Crear el gráfico de barras
    fig = go.Figure()

    # Añadir una barra por cada métrica
    fig.add_trace(go.Bar(
        x=values,  
        y=columns,  
        orientation='h',  
        text=values.round(2),
        textposition='outside',
        insidetextanchor='end',
        textfont=dict(size=12, color='gray'),
        width=0.8,
        marker=dict(
            color='rgba(0, 24, 76, 1)',
            line=dict(color='rgba(255, 255, 255, 1)', width=1)
        )
    ))

    # Configurar los ejes
    fig.update_xaxes(
        title_text='Valores totales',
        title_font=dict(size=13, color='gray'),
        showgrid=True,
        gridcolor='rgba(181, 181, 181, 0.8)',  # Color de la cuadrícula
        griddash="dash",
        zerolinecolor='rgba(200, 200, 200, 0.5)',  # Línea del eje X
        tickfont=dict(size=13, color='gray'),
        layer="below traces"
    )
    fig.update_yaxes(
        showgrid=False,
        tickfont=dict(size=13, color='gray'),
        automargin=True,  # Ajustar automáticamente el espacio para el texto
        title_text=None
        )

    # Configurar el layout del gráfico
    fig.update_layout(
        title={
            'text': (
                f'{player_name}<br>'
                f'<span style="font-size:13px; color:gray;">Métricas totales temporada: {season}</span><br>'
                f'<span style="font-size:13px; color:gray;">Minutos jugados: {minutes_played}</span>'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=16, color='black')  # Formato del título principal
        },
        plot_bgcolor='rgba(245, 245, 245, 1)',  # Fondo del área del gráfico
        paper_bgcolor='white',  # Fondo total del gráfico
        showlegend=False,
        margin=dict(l=160, r=10, t=110, b=40),
        xaxis=dict(range=[0, x_max + (0.05 * x_max)]),
        height=height
    )

    # Establecer el límite máximo del eje X si se proporciona
    if x_max is not None:
        fig.update_xaxes(range=[0, x_max])

    return fig