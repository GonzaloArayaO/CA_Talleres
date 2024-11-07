import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def calculate_percentiles(df_group, metrics, season_id):
    """Calcula los percentiles para las métricas dentro de la misma liga."""
    filtered_df = df_group[df_group['seasonId'] == season_id]
    percentiles_df = filtered_df[metrics].rank(pct=True) * 100
    percentiles_df['playerId'] = filtered_df['playerId'].values
    return percentiles_df

def radar_chart(df_group, df_unique, player_id, profile_name, profiles):
    metrics = profiles[profile_name]
    player_info = df_unique[df_unique['playerId'] == player_id].iloc[0]
    season_id = player_info['seasonId']

    # Calcular percentiles
    percentiles_df = calculate_percentiles(df_group, metrics, season_id)
    player_metrics = percentiles_df[percentiles_df['playerId'] == player_id][metrics].iloc[0]
    player_data = df_group[df_group['playerId'] == player_id][metrics].iloc[0]
    playerName = player_info['shortName']

    # Crear figura del radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player_metrics.values,
        theta=metrics,
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.4)',
        line=dict(color='blue', width=1),
        text=[f'{v:.2f}' for v in player_metrics.values],
        textposition='bottom center',
        mode='lines+markers+text',
        textfont=dict(size=12, color='black'),
        marker=dict(size=6, symbol='circle', color='blue'),
        hoverinfo='text',
        hovertext=[f'<b>{metric}</b>: {value:.2f}' for metric, value in zip(metrics, player_metrics.values)]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                linecolor='black',
                gridcolor='rgba(0, 0, 0, 0.15)',
                gridwidth=0.1,
                griddash='dash',
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                showline=True,
                linewidth=1,
                linecolor='gray',
                griddash='dash',
                tickfont=dict(size=12, color='black')
            )
        ),
        title=dict(
            text=f'{playerName}',
            font=dict(size=20),
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top'
        ),
        margin=dict(t=75)
    )

    return fig, player_data

def show_radar_with_table(df_group, df_unique, player_id, profile_name, profiles):
    # Desempaquetar correctamente la tupla
    fig, player_data = radar_chart(df_group, df_unique, player_id, profile_name, profiles)

    # Crear layout con dos columnas
    col1, col2 = st.columns([3, 1])

    # Mostrar radar chart en la primera columna
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    # Mostrar tabla con valores absolutos en la segunda columna
    with col2:
        data = {'Métrica': player_data.index, 'Valor': player_data.values}
        df_table = pd.DataFrame(data)
        df_table['Valor'] = df_table['Valor'].apply(lambda x: f'{x:.2f}')
        styled_table = (
        df_table.style
            .set_table_styles(
                [  # Estilos para el encabezado sin borde exterior
                    {'selector': 'thead th', 'props': [('font-size', '13px'), ('border', 'none'), ('padding', '2px 5px')]},
                    # Celdas con tamaño ajustado al contenido y sin bordes
                    {'selector': 'th, td', 'props': [('font-size', '12px'), ('border', 'none'), ('padding', '2px 5px')]}
                ]
            )
            .hide(axis="index")  # Ocultar el índice
            )
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)