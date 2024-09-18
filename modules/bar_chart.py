import plotly.graph_objects as go
import pandas as pd

def bar_chart_player_stats(df, player_id, important_columns, selected_reference_season, x_max=None):
    # Filtrar el DataFrame por el jugador y las columnas importantes
    player_data = df[(df['playerId'] == player_id) & (df['seasonName'] == selected_reference_season)][important_columns]

    # Obtener los nombres de las columnas y sus respectivos valores
    columns = player_data.columns
    values = player_data.iloc[0].values  # Obtener la primera fila (que corresponde al jugador seleccionado)
    
    player_name = df[df['playerId'] == player_id]['shortName'].iloc[0]

    minutes_played = df[(df['playerId'] == player_id) & (df['seasonName'] == selected_reference_season)]['minutesOnField'].iloc[0]

    # Calcular la altura del gráfico en función del número de barras
    num_metrics = len(columns)
    height_per_bar = 40
    height = max(400, num_metrics * height_per_bar)

    # Crear el gráfico de barras
    fig = go.Figure()

    # Añadir una barra por cada métrica
    fig.add_trace(go.Bar(
        x=values,  
        y=columns,  
        orientation='h',  
        text=values.round(2),
        textangle=0,
        textfont=dict(size=12)
    ))

    fig.update_xaxes(title_text='Valores totales', title_font_size=13)

    # Configurar el layout del gráfico
    fig.update_layout(
        title={
            'text': (
                f'{player_name}<br>'
                f'<span style="font-size:13px; color:gray;">Métricas totales temporada: {selected_reference_season}</span><br>'
                f'<span style="font-size:13px; color:gray;">Minutos jugados: {minutes_played}</span>'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=16, color='black')  # Formato del título principal
        },
        showlegend=False,
        margin=dict(l=0, r=0, t=115, b=0),
        height=height
    )

    # Establecer el límite máximo del eje X si se proporciona
    if x_max is not None:
        fig.update_xaxes(range=[0, x_max])

    return fig