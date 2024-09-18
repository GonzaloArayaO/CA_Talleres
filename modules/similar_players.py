import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb

def similarPlayers(df, df_unique, playerId, reference_season, target_season='2024', importance_threshold=0.0175):
    # Filtrar el DataFrame para obtener los datos de la temporada de referencia y el jugador seleccionado
    df_reference = df[(df['seasonName'] == reference_season) & (df['playerId'] == playerId)].set_index('playerId')
    
    if df_reference.empty:
        raise ValueError("No se encontraron datos para el jugador o temporada de referencia.")
    
    # Obtener las características del jugador de referencia
    reference_player = df_reference.loc[playerId]
    
    # Obtener la posición del jugador de referencia
    player_role = df_unique[df_unique['playerId'] == playerId]['code2Role'].values[0]
    
    # Si el jugador no es portero (GK), eliminar las métricas de portero
    if player_role != 'GK':
        gk_metrics = ['gkCleanSheets', 'gkConcededGoals', 'gkShotsAgainst', 'gkExits', 
                      'gkSuccessfulExits', 'gkAerialDuels', 'gkAerialDuelsWon', 'gkSaves',
                      'goalKicksShort', 'goalKicksLong']
        df_reference = df_reference.drop(columns=gk_metrics, errors='ignore')
        df = df.drop(columns=gk_metrics, errors='ignore')

    # Continuar con el filtrado por tipos numéricos en ambos DataFrames
    df_reference = df_reference.select_dtypes(include=[np.number])
    df_target = df[df['seasonName'] == target_season].set_index('playerId').select_dtypes(include=[np.number])

    if df_target.empty:
        raise ValueError(f"No se encontraron jugadores para la temporada objetivo ({target_season}).")
    
    # Excluir las columnas no deseadas antes de la normalización
    excluded_columns = ['matches', 'matchesInStart', 'matchesSubstituted', 'matchesComingOff', 'minutesOnField', 'minutesTagged']
    df_target_filtered = df_target.drop(columns=excluded_columns, errors='ignore')
    
    # Asegurarse de que las columnas de referencia y objetivo sean las mismas
    common_columns = df_reference.columns.intersection(df_target_filtered.columns)
    df_reference = df_reference[common_columns]
    df_target_filtered = df_target_filtered[common_columns]

    # Normalización de datos
    scaler = MinMaxScaler()
    
    # Ajustar el scaler con las columnas filtradas
    df_target_normalized = pd.DataFrame(scaler.fit_transform(df_target_filtered), columns=common_columns, index=df_target_filtered.index)
    
    # Normalizar las características del jugador de referencia
    reference_player_filtered = reference_player[common_columns]
    reference_player_normalized = scaler.transform(reference_player_filtered.values.reshape(1, -1)).flatten()

    # Calcular diferencias
    difference = ((df_target_normalized - reference_player_normalized) ** 2).sum(axis=1)

    # Entrenar el modelo XGBoost para seleccionar características importantes
    model = xgb.XGBRegressor(objective='reg:squarederror', learning_rate=0.1, max_depth=3, n_estimators=100, random_state=42)
    model.fit(df_target_normalized, difference)
    
    # Obtener la importancia de las características
    importances = model.feature_importances_
    important_columns = common_columns[importances > importance_threshold]
    df_target_important = df_target_normalized[important_columns]

    # Filtrar y normalizar las características del jugador de referencia usando el mismo scaler
    reference_player_important = pd.DataFrame(reference_player_normalized.reshape(1, -1), columns=common_columns)
    reference_player_important = reference_player_important[important_columns].values
    
    # Calcular la similitud entre el jugador de referencia y los jugadores de la temporada objetivo
    distances = np.linalg.norm(df_target_important.values - reference_player_important, axis=1)
    similarities = 100 / (1 + distances)
    
    # Crear DataFrame con similitudes y añadir las características seleccionadas
    result_df = pd.DataFrame(similarities, columns=['similarity'], index=df_target_important.index)
    result_df = result_df.join(df_target_important)  # Añadir las columnas seleccionadas
    result_df = result_df.sort_values(by='similarity', ascending=False).reset_index()

    # Añadir las columnas desde df_unique
    result_df = result_df.merge(df_unique[['playerId', 'shortName', 'code2Role', 'teamName',
        'seasonName', 'nameRole', 'age']], on='playerId', how='left')
    
    # Añadir la columna 'minutesOnField' desde df
    result_df = result_df.merge(df[df['seasonName'] == target_season][['playerId', 'minutesOnField']], on='playerId', how='left')

    # Filtrar el resultado final para la temporada objetivo
    result_df = result_df[result_df['seasonName'] == target_season]

    # Reorganizar columnas para que 'shortName', 'teamOfficialName' aparezcan antes de 'similarity'
    cols = ['playerId', 'minutesOnField', 'shortName', 'code2Role', 'age', 'teamName', 'similarity']
    result_df = result_df[cols].reset_index(drop=True)

    result_df['similarity'] = result_df['similarity'].round(2)

    result_df.rename(columns={
        'shortName': 'Nombre',
        'age': 'Edad',
        'code2Role': 'Pos',
        'teamName': 'Equipo',
        'similarity': '% Similitud'
        }, inplace=True)

    return result_df.head(20), important_columns.to_list()