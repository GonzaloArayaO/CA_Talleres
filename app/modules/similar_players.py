import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
from modules.positions import get_position_mapping

position_mapping = get_position_mapping()

def similarPlayers(
    df_group, 
    df_unique, 
    df_positions, 
    playerId, 
    reference_season,
    season_id,
    target_seasons, 
    selected_primary_positions=None,
    selected_secondary_positions=None,
    selected_nationalities=None, 
    selected_age_range=(0, 100), min_minutes=0,
    selected_countries_output=None, 
    selected_competitions_output=None,
    num_results=20, 
    importance_threshold=0.01
):
    # 1. Obtener las métricas del jugador de referencia
    df_reference = df_group[
        (df_group['seasonName'] == reference_season) & 
        (df_group['playerId'] == playerId) &
        (df_group['seasonId'] == season_id)
    ].set_index('playerId')

    if df_reference.empty:
        raise ValueError("No se encontraron datos para el jugador o temporada de referencia.")

    # 2. Filtrar jugadores por nacionalidad/pasaporte
    if selected_nationalities:
        df_unique_filtered = df_unique[
            df_unique['nameBirthArea'].isin(selected_nationalities) | 
            df_unique['namePassportArea'].isin(selected_nationalities)
            ]
        df_group = df_group[df_group['playerId'].isin(df_unique_filtered['playerId'])]

    # 3. Aplicar filtros de edad y minutos al resto de los jugadores
    df_combined = pd.merge(
        df_group[['playerId', 'seasonName', 'minutesOnFieldTotal']], 
        df_unique[['playerId', 'age']], 
        on='playerId', how='inner'
    )
    df_filtered = df_combined[
        (df_combined['age'] >= selected_age_range[0]) &
        (df_combined['age'] <= selected_age_range[1]) &
        (df_combined['minutesOnFieldTotal'] >= min_minutes)
    ]

    if df_filtered.empty:
        raise ValueError("No se encontraron jugadores que coincidan con los filtros seleccionados.")

    # 4. Asegurar que el jugador de referencia esté incluido para la comparación
    filtered_player_ids = df_filtered['playerId'].tolist()
    if playerId not in filtered_player_ids:
        filtered_player_ids.append(playerId)  # Asegurar que el jugador de referencia esté incluido

    df_group = df_group[df_group['playerId'].isin(filtered_player_ids)]

    # 5. Aplicar los filtros de posición
    if 'Goalkeeper' in selected_secondary_positions or 'GK' in selected_primary_positions:
        # Filtrar exclusivamente por porteros
        df_positions_filtered = df_positions[df_positions['position'] == 'Goalkeeper']
        df_group = df_group[df_group['playerId'].isin(df_positions_filtered['playerId'])]

    elif selected_secondary_positions:
        # Filtrar por las posiciones secundarias si están seleccionadas
        df_positions_filtered = df_positions[df_positions['position'].isin(selected_secondary_positions)]
        df_group = df_group[df_group['playerId'].isin(df_positions_filtered['playerId'])]

    elif selected_primary_positions:
        # Si no hay posiciones secundarias, filtra por las primarias
        primary_positions_filtered = []
        for primary in selected_primary_positions:
            primary_positions_filtered.extend(position_mapping[primary])  # Obtiene las posiciones secundarias relacionadas

        # Filtrar jugadores en df_unique que coincidan con las posiciones primarias seleccionadas
        df_unique_filtered = df_unique[df_unique['code2Role'].isin(selected_primary_positions)]
        
        # Obtener los playerIds de los jugadores con la posición primaria seleccionada
        primary_player_ids = df_unique_filtered['playerId'].unique()
        
        # Filtrar df_group utilizando estos playerIds
        df_group = df_group[df_group['playerId'].isin(primary_player_ids)]

    # 6. Filtro adicional por países de competencia
    if selected_countries_output:
        df_unique_filtered = df_unique[df_unique['nameArea'].isin(selected_countries_output)]
        df_group = df_group[df_group['playerId'].isin(df_unique_filtered['playerId'])]

    # 7. Filtro adicional por nombre de competencias
    if selected_competitions_output:
        df_unique_filtered = df_unique[df_unique['competitionName'].isin(selected_competitions_output)]
        df_group = df_group[df_group['playerId'].isin(df_unique_filtered['playerId'])]

    # 6. Eliminar métricas de portero si el jugador no es portero
    player_role = df_unique[df_unique['playerId'] == playerId]['code2Role'].values[0]
    if player_role != 'GK':
        gk_metrics = ['gkCleanSheetsTotal', 'gkConcededGoalsTotal', 'gkShotsAgainstTotal', 
                      'gkExitsTotal', 'gkSuccessfulExitsTotal', 'gkAerialDuelsTotal', 
                      'gkAerialDuelsWonTotal', 'gkSavesTotal', 'goalKicksShortTotal', 'goalKicksLongTotal',
                      'gkAerialDuelsPer90', 'gkAerialDuelsWonPer90', 'gkConcededGoalsPer90',
                      'gkExitsPer90', 'gkSavesPer90', 'gkShotsAgainstPer90',
                      'gkSuccessfulExitsPer90', 'gkAerialDuelsWonPercent', 'gkSavesPercent',
                      'gkSuccessfulExitsPercent']
        df_reference = df_reference.drop(columns=gk_metrics, errors='ignore')
        df_group = df_group.drop(columns=gk_metrics, errors='ignore')

    # 7. Filtrar las temporadas objetivo
    df_target = df_group[
        df_group['seasonName'].isin(target_seasons)
    ].set_index('playerId').select_dtypes(include=[np.number]) \
     .replace([np.inf, -np.inf], np.nan).fillna(0)

    if df_target.empty:
        raise ValueError(f"No se encontraron jugadores para las temporadas objetivo: {target_seasons}.")

    # 8. Continuar con el procesamiento de similitud
    excluded_columns = ['matchesTotal', 'matchesInStartTotal', 'matchesSubstitutedTotal', 'matchesComingOffTotal', 'minutesOnFieldTotal', 'minutesTaggedTotal']
    df_target_filtered = df_target.drop(columns=excluded_columns, errors='ignore')

    common_columns = df_reference.columns.intersection(df_target_filtered.columns)
    df_reference = df_reference[common_columns]
    df_target_filtered = df_target_filtered[common_columns]

    scaler = MinMaxScaler()
    df_target_normalized = pd.DataFrame(scaler.fit_transform(df_target_filtered), columns=common_columns, index=df_target_filtered.index)

    reference_player_normalized = scaler.transform(df_reference.values.reshape(1, -1)).flatten()

    difference = ((df_target_normalized - reference_player_normalized) ** 2).sum(axis=1)

    model = xgb.XGBRegressor(objective='reg:squarederror', learning_rate=0.1, max_depth=3, n_estimators=100, random_state=42)
    model.fit(df_target_normalized, difference)

    importances = model.feature_importances_
    important_columns = common_columns[importances > importance_threshold]
    df_target_important = df_target_normalized[important_columns]

    reference_player_important = pd.DataFrame(reference_player_normalized.reshape(1, -1), columns=common_columns)
    reference_player_important = reference_player_important[important_columns].values

    distances = np.linalg.norm(df_target_important.values - reference_player_important, axis=1)
    similarities = 100 / (1 + distances)

    result_df = pd.DataFrame(similarities, columns=['similarity'], index=df_target_important.index)
    result_df = result_df.join(df_target_important).sort_values(by='similarity', ascending=False).reset_index()

    result_df = result_df.merge(df_unique[[ 
        'playerId', 'shortName', 'code2Role', 'teamName', 'seasonName', 'age', 'foot', 
        'competitionName', 'nameArea', 'nameBirthArea', 'namePassportArea' 
    ]], on='playerId', how='inner')

    result_df = result_df[result_df['seasonName'].isin(target_seasons)]

    cols = ['playerId', 'similarity', 'shortName', 'code2Role', 'age', 'foot', 
        'nameArea', 'teamName', 'competitionName', 'nameBirthArea', 'namePassportArea']
    result_df = result_df[cols].reset_index(drop=True)

    result_df.rename(columns={
        'similarity': '% Similitud',
        'shortName': 'Nombre',
        'code2Role': 'Posición',
        'age': 'Edad',
        'foot': 'Pie',
        'nameArea': 'Pais competencia',
        'teamName': 'Equipo',
        'competitionName': 'Nombre competencia',
        'nameBirthArea': 'Pais nacimiento',
        'namePassportArea': 'Pais pasaporte'
    }, inplace=True)

    result_df = result_df.drop_duplicates(subset='playerId')
    result_df['% Similitud'] = result_df['% Similitud'].apply(lambda x: f'{x:.2f}')

    return result_df.head(num_results), important_columns.to_list()