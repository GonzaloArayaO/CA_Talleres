def get_player_profiles():
    return {
    'Portero bueno con los pies': 
    [
        'receivedPassPer90', 'passesPer90', 'successfulPassesPercent',
        'forwardPassesPer90', 'successfulForwardPassesPercent',
        'lateralPassesPer90', 'successfulLateralPassesPercent',
        'longPassesPer90','progressivePassesPer90',
        'successfulLongPassesPercent', 'gkConcededGoalsPer90',
        'gkShotsAgainstPer90', 'xgSavePer90', 'gkSavesPer90',
        'gkSuccessfulExitsPer90', 'fieldAerialDuelsPer90', 'gkSavesPercent',
        'gkCleanSheetsTotal'
    ],
        
    'Portero con muchas paradas': 
    [
        'gkConcededGoalsPer90', 'gkShotsAgainstPer90', 'xgSavePer90',
        'gkSavesTotal', 'gkSuccessfulExitsPer90', 'fieldAerialDuelsPer90',
        'gkSavesPercent', 'gkCleanSheetsTotal'
    ],

    'Lateral defensivo': 
    [
        'duelsWonPercent', 'defensiveActionsPer90', 'defensiveDuelsPer90','newDuelsWonPercent',
        'defensiveDuelsWonPercent', 'fieldAerialDuelsWonPercent',
        'interceptionsPer90', 'passesPer90', 'successfulPassesPercent','ballRecoveriesPer90',
        'forwardPassesPer90', 'successfulForwardPassesPercent','looseBallDuelsWonPer90','shotsBlockedPer90','counterpressingRecoveriesPer90',
    ],

    'Lateral ofensivo': 
    [
        'duelsWonPercent', 'defensiveActionsPer90', 'defensiveDuelsPer90', 'keyPassesPer90',
        'defensiveDuelsWonPercent', 'fieldAerialDuelsWonPercent',
        'interceptionsPer90', 'passesPer90', 'successfulPassesPercent',
        'forwardPassesPer90', 'successfulForwardPassesPercent', 'successfulAttackingActionsPer90',
        'crossesPer90', 'offensiveDuelsWonPercent', 'progressiveRunTotal',
        'accelerationsPer90', 'receivedPassPer90', 'thirdAssistsPer90',
        'successfulPassesToFinalThirdPercent', 'passesToFinalThirdPer90',
        'successfulThroughPassesPercent', 'touchInBoxPer90',
        'successfulProgressivePassesPercent','successfulSmartPassesPercent','successfulLongPassesPercent',
        'xgAssistPer90','xgAssistPer90'
    ],
          
    'Central ganador de duelos': 
    [
        'duelsPer90', 'duelsWonPercent', 'defensiveDuelsPer90',
        'defensiveDuelsWonPercent', 'fieldAerialDuelsPer90', 'fieldAerialDuelsWonPercent',
        'dribblesAgainstWonPercent','counterpressingRecoveriesPer90','aerialDuelsWonPercent'
    ],

    'Central rápido': 
    [
        'accelerationsPer90', 'progressiveRunTotal', 'interceptionsPer90',
        'defensiveDuelsPer90', 'recoveriesTotal', 'slidingTacklesPer90',
        'clearancesPer90', 'ballRecoveriesPer90'
    ],

    'Central técnico': 
    [
        'passesPer90', 'successfulPassesPercent', 'longPassesPer90', 'successfulLongPassesPercent',
        'keyPassesPer90','forwardPassesPer90', 'successfulForwardPassesPercent', 
        'backPassesPer90','successfulBackPassesPercent', 'lateralPassesPer90', 
        'successfulLateralPassesPercent', 'passesToFinalThirdPer90', 
        'successfulPassesToFinalThirdPercent','successfulProgressivePassesPercent'
    ],
       
    'Mediocentro defensivo': 
    [
        'duelsPer90', 'duelsWonPercent', 'defensiveDuelsPer90',
        'defensiveDuelsWonPercent', 'interceptionsPer90', 'slidingTacklesPer90',
        'foulsPer90', 'recoveriesTotal', 'ballRecoveriesPer90','keyPassesPer90',
        'looseBallDuelsWonPer90','xgAssistPer90', 'opponentHalfRecoveriesPer90',
        'dangerousOpponentHalfRecoveriesPer90','dribblesAgainstWonPer90','newDefensiveDuelsWonPer90',
        'aerialDuelsWonPercent','successfulSmartPassesPercent', 'successfulPassesToFinalThirdPercent', 
        'successfulThroughPassesPercent'
    ],

    'Mediocentro creador': 
    [
        'passesPer90', 'successfulPassesPercent', 'keyPassesPer90', 'passesToFinalThirdPer90', 
        'successfulPassesToFinalThirdPercent', 'xgAssistPer90','receivedPassPer90','xgShotPer90',
        'dribblesAgainstWonPer90','shotsPer90','touchInBoxPer90',
        'opponentHalfRecoveriesPer90','counterpressingRecoveriesPer90','offensiveDuelsWonPercent',
        'successfulCrossesPercent','successfulThroughPassesPercent','accelerationsPer90'
    ],

    'Mediocentro box to box': 
    [
        'duelsPer90', 'duelsWonPercent', 'passesPer90', 'successfulPassesPercent',
        'interceptionsPer90', 'recoveriesTotal', 'progressiveRunTotal', 'accelerationsPer90', 
        'shotsPer90', 'goalsPer90','assistsPer90', 'touchInBoxPer90', 'xgShotPer90',
        'xgAssistPer90','passesToFinalThirdPer90','dribblesAgainstWonPer90',
        'opponentHalfRecoveriesPer90','counterpressingRecoveriesPer90','offensiveDuelsWonPercent',
        'successfulCrossesPercent','successfulThroughPassesPercent'
    ],
             
    'Extremo regateador': 
    [
        'dribblesPer90', 'newSuccessfulDribblesPercent', 'offensiveDuelsPer90',
        'offensiveDuelsWonPercent', 'accelerationsPer90', 'shotsPer90',
        'assistsPer90', 'keyPassesPer90', 'touchInBoxPer90',
        'crossesPer90', 'successfulCrossesPercent','looseBallDuelsWonPer90',
        'opponentHalfRecoveriesPer90','xgAssistPer90','successfulSmartPassesPercent',
        'xgShotPer90','receivedPassPer90'
    ],

    'Extremo centrador': 
    [
        'crossesPer90', 'successfulCrossesPercent', 'keyPassesPer90',
        'assistsPer90', 'passesToFinalThirdPer90', 'successfulPassesToFinalThirdPercent',
        'touchInBoxPer90', 'dribblesPer90', 'accelerationsPer90', 'xgAssistPer90',
        'looseBallDuelsWonPer90','opponentHalfRecoveriesPer90',
        'successfulSmartPassesPercent','xgShotPer90','receivedPassPer90'
    ],

    'Extremo goleador': 
    [
        'goalsPer90', 'shotsPer90', 'xgShotPer90', 'headShotsPer90','shotsOnTargetPercent',
        'assistsPer90', 'keyPassesPer90','touchInBoxPer90', 'goalConversionPercent',
        'looseBallDuelsWonPer90','opponentHalfRecoveriesPer90','xgAssistPer90',
        'successfulSmartPassesPercent','receivedPassPer90','accelerationsPer90'
    ],
        
    'Delantero cabeceador': 
    [
        'headShotsTotal', 'headShotsPer90', 'fieldAerialDuelsPer90',
        'fieldAerialDuelsWonPercent', 'shotsPer90', 'goalsPer90',
        'xgShotPer90', 'receivedPassPer90', 'touchInBoxPer90','shotsTotal',
        'newDefensiveDuelsWonPercent','accelerationsPer90','interceptionsPer90'
    ],

    'Delantero killer': 
    [
        'goalsPer90', 'xgShotPer90', 'shotsPer90', 'shotsOnTargetPercent',
        'goalConversionPercent', 'assistsPer90', 'keyPassesPer90',
        'touchInBoxPer90', 'duelsWonPercent','opponentHalfRecoveriesPer90', 
        'passesToFinalThirdPer90','goalsTotal', 'shotsTotal',
        'newDefensiveDuelsWonPercent','accelerationsPer90','interceptionsPer90'
    ],

    'Delantero asociador': 
    [
        'assistsPer90', 'keyPassesPer90', 'passesPer90','successfulPassesPercent', 
        'duelsWonPercent', 'touchInBoxPer90','shotsPer90', 'xgShotPer90', 'goalsPer90',
        'opponentHalfRecoveriesPer90', 'passesToFinalThirdPer90','successfulPassesToFinalThirdPercent',
        'successfulSmartPassesPercent','receivedPassPer90','newDefensiveDuelsWonPercent',
        'successfulThroughPassesPercent','successfulKeyPassesPercent','interceptionsPer90'
    ]
}