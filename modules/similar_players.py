import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb

def similarPlayers(df, df_unique, playerId, reference_season, target_season='2024', importance_threshold=0.01):
    # Filtrar el DataFrame para obtener los datos de la temporada de referencia y el jugador seleccionado
    df_reference = df[(df['seasonName'] == reference_season) & (df['playerId'] == playerId)].set_index('playerId').select_dtypes(include=[np.number])
    
    if df_reference.empty:
        raise ValueError("No se encontraron datos para el jugador o temporada de referencia.")
    
    # Obtener las características del jugador de referencia
    reference_player = df_reference.loc[playerId]
    
    # Filtrar el DataFrame para la temporada de búsqueda
    df_target = df[df['seasonName'] == target_season].set_index('playerId').select_dtypes(include=[np.number])
    
    if df_target.empty:
        raise ValueError("No se encontraron datos para la temporada objetivo.")
    
    # Excluir las columnas no deseadas antes de la normalización
    excluded_columns = ['matches', 'matchesInStart', 'matchesSubstituted', 'matchesComingOff', 'minutesOnField', 'minutesTagged']
    df_target_filtered = df_target.drop(columns=excluded_columns, errors='ignore')
    
    # Normalización de datos
    scaler = MinMaxScaler()
    df_target_normalized = pd.DataFrame(scaler.fit_transform(df_target_filtered), columns=df_target_filtered.columns, index=df_target_filtered.index)
    
    # Crear una columna sintética de diferencia con el jugador de referencia
    reference_player_filtered = reference_player.drop(labels=excluded_columns, errors='ignore')
    reference_player_normalized = scaler.transform(reference_player_filtered.values.reshape(1, -1)).flatten()
    difference = ((df_target_normalized - reference_player_normalized) ** 2).sum(axis=1)

    # Entrenar el modelo XGBoost para seleccionar características importantes
    model = xgb.XGBRegressor(objective='reg:squarederror', learning_rate=0.1, max_depth=3, n_estimators=100, random_state=42)
    model.fit(df_target_normalized, difference)
    
    # Obtener la importancia de las características
    importances = model.feature_importances_
    important_columns = df_target_normalized.columns[importances > importance_threshold]
    df_target_important = df_target_normalized[important_columns]

    # Filtrar y normalizar las características del jugador de referencia usando el mismo scaler
    reference_player_important = pd.DataFrame(reference_player_normalized.reshape(1, -1), columns=df_target_filtered.columns)
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

    # Filtrar el resultado final para la temporada objetivo
    result_df = result_df[result_df['seasonName'] == target_season]

    # Reorganizar columnas para que 'shortName', 'teamOfficialName', 'seasonName' aparezcan antes de 'similarity'
    cols = ['shortName', 'code2Role', 'age', 'teamName', 'seasonName', 'similarity']
    result_df = result_df[cols].reset_index(drop=True)

    result_df.rename(columns={
        'shortName': 'Nombre',
        'age': 'Edad',
        'code2Role': 'Pos',
        'teamName': 'Equipo',
        'seasonName': 'Temporada',
        'similarity': '% Similitud'
        }, inplace=True)

    return result_df.head(20), important_columns.to_list()