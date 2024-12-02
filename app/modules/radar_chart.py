import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from modules.pdf_exporter import style_table

def calculate_percentiles(df_group, metrics, season_id):
    """Calcula los percentiles para las métricas dentro de la misma liga."""
    filtered_df = df_group[df_group['seasonId'] == season_id]
    percentiles_df = filtered_df[metrics].rank(pct=True) * 100
    percentiles_df['playerId'] = filtered_df['playerId'].values
    return percentiles_df

def calculate_prom_league(df_group, metrics, season_id):
    metrics_league = df_group[df_group['seasonId'] == season_id]
    prom_league = metrics_league.groupby('seasonId').mean(numeric_only=True).reset_index().round(3) # Promedios metricas de liga
    prom_league = prom_league[metrics]
    return prom_league


def radar_chart(df_group, df_unique, player_id, profile_name, profiles):
    metrics = profiles[profile_name]
    player_info = df_unique[df_unique['playerId'] == player_id].iloc[0]
    season_id = player_info['seasonId']

    # Calcular percentiles
    percentiles_df = calculate_percentiles(df_group, metrics, season_id)
    player_metrics = percentiles_df[percentiles_df['playerId'] == player_id][metrics].iloc[0]
    player_data = df_group[df_group['playerId'] == player_id][metrics].iloc[0]
    playerName = player_info['shortName']

    # Definir colores según perfil
    color_map = {
        'Portero bueno con los pies': 'rgba(255, 170, 0, 0.4)',
        'Portero con muchas paradas': 'rgba(255, 170, 0, 0.4)',
        'Lateral defensivo': 'rgba(93, 109, 126, 0.4)',
        'Lateral ofensivo': 'rgba(93, 109, 126, 0.4)',
        'Central ganador de duelos': 'rgba(93, 109, 126, 0.4)',
        'Central rápido': 'rgba(93, 109, 126, 0.4)',
        'Central técnico': 'rgba(93, 109, 126, 0.4)',
        'Mediocentro defensivo': 'rgba(50, 205, 50, 0.4)',
        'Mediocentro creador': 'rgba(50, 205, 50, 0.4)',
        'Mediocentro box to box': 'rgba(50, 205, 50, 0.4)',
        'Extremo regateador': 'rgba(227, 0, 34, 0.4)',
        'Extremo centrador': 'rgba(227, 0, 34, 0.4)',
        'Extremo goleador': 'rgba(227, 0, 34, 0.4)',
        'Delantero cabeceador': 'rgba(227, 0, 34, 0.4)',
        'Delantero killer': 'rgba(227, 0, 34, 0.4)',
        'Delantero asociador': 'rgba(227, 0, 34, 0.4)',
    }

    # Obtener color correspondiente al perfil
    fill_color = color_map.get(profile_name, 'rgba(200, 200, 200, 0.4)')

    # Crear figura del radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player_metrics.values,
        theta=metrics,
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=fill_color.replace('0.4', '1'), width=1.5),
        text=[f'{v:.2f}' for v in player_metrics.values],
        textposition='bottom center',
        mode='lines+markers+text',
        textfont=dict(size=12, color='black'),
        marker=dict(size=8, symbol='circle', color=fill_color.replace('0.4', '1')),
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
                tickfont=dict(size=12, color='black'),
                rotation=45
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

def show_radar_with_table(df_group, df_unique, player_id, profile_name, profiles, session_key):
    fig, player_data = radar_chart(df_group, df_unique, player_id, profile_name, profiles)

    player_info = df_unique[df_unique['playerId'] == player_id].iloc[0]
    season_id = player_info['seasonId']

    # Guardar la figura en session_state usando el session_key para identificarla
    if fig is not None:
        st.session_state[session_key] = fig

    data = {'Métrica': player_data.index, 'Valor': player_data.values}
    df_table = pd.DataFrame(data)
    df_table['Valor'] = df_table['Valor'].apply(lambda x: f'{x:.2f}')

    # Calcular los promedios de liga
    metrics = player_data.index.tolist()  # Obtener las métricas del radar
    prom_league = calculate_prom_league(df_group, metrics, season_id)
    prom_league = prom_league.iloc[0].values  # Extraer valores de la fila correspondiente
    df_table['Prom liga'] = prom_league
    df_table['Prom liga'] = df_table['Prom liga'].apply(lambda x: f'{x:.2f}')


    styled_table_html = style_table(df_table,  for_info=True).to_html(index=False)


    # Mostrar radar chart y tabla
    col1, col2 = st.columns([3, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown(styled_table_html, unsafe_allow_html=True)
