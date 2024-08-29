import pandas as pd
from datetime import datetime

def preprocess_data(file_path):
    df = pd.read_parquet(file_path)

    df['seasonName'] = df['seasonName'].astype(str)

    #############
    # df_unique #
    #############
    df_unique = df.drop_duplicates(subset=['playerId', 'seasonName'])[['playerId', 'seasonName',
        'shortName', 'firstName', 'lastName', 'height', 'weight', 'birthDate', 'foot', 'nameBirthArea',
        'namePassportArea', 'nameRole', 'code2Role', 'teamName', 'competitionName', 'nameArea']]
    # Obtener edad del jugador
    df_unique['birthDate'] = pd.to_datetime(df_unique['birthDate'], errors='coerce')
    df_unique = df_unique.dropna(subset=['birthDate']) # En este momento 2 nulos, sin fecha de nacimiento
    df_unique['age'] = df_unique['birthDate'].apply(lambda x: datetime.now().year - x.year - ((datetime.now().month, datetime.now().day) < (x.month, x.day))).astype(int)

    ############
    # df_group #
    ############
    df_filtered = df.drop_duplicates(subset=['playerId', 'seasonName'])

    # Filtrar columnas que no terminen en _percent ni en _average
    columns_to_keep = [col for col in df.columns if not (col.endswith('_percent') or col.endswith('_average'))]
    df_filtered = df[columns_to_keep]

    # Lista con valores float a sumar
    cols_sum = ['xgShot', 'xgAssist', 'xgSave']  # float

    df_columns = df_filtered.select_dtypes(include='int64')  # Filtra las columnas int

    # Eliminar columnas para sumar listas
    cols_drop = [
        'playerId', 'matchId', 'competitionId', 'seasonId', 'roundId', 'teamId', 'gameweek',
        'competitionDivisionLevel', 'areaId', 'height', 'weight'
    ]

    df_columns = df_columns.drop(columns=cols_drop)
    list_cols = list(df_columns.columns)

    cols = list_cols + cols_sum  # Nombre columnas numericas con valores totales para sumar

    # Columnas por las cuales agrupar
    cols_group = [
        'playerId', 'shortName', 'seasonName'
    ]

    # df agrupado con suma de metricas totales
    df_group = df_filtered.groupby(cols_group)[cols].sum().reset_index()

    return df, df_unique, df_group