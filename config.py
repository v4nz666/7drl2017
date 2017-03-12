#TODO set this to a reasonable value
fps = 90
spf = 1.0/fps

maxSails = 10
sailStep = 1.0 / maxSails
speedAdjust = 0.075

layout = {
    'uiWidth': 75,
    'uiHeight': 50
}

world = {
    'width': 127,
    'height': 127,
    'cityCount': 30
}

wind = {
    'impact': 0.075,
    'maxSpeed': 20.0,
    'speedJitter': 1.0,
    'dirJitter': 5.0
}

projectile = {
    'speed': 200.0,
    'maxDistance': 10
}

city = {
    'possibleShops': [
        'tavern',
        'gossip',
        'brothel',
        'shipyard'
    ],
    'viewRadius': 30
}

brothel = {
    'baseRate': 10,
    'baseReturn': 25
}

shipyard = {
    'repairRate': 20,
    'repairReturn': 5,
    'ammoRate': 20,
    'ammoBuyCount': 10
}

tavern = {
    'hireRate': 10,
    'drinkPrice': 1,
    'drinkMorale': 5

}

morale = {
    'daysToStarve': 5,
    'crewStarved': 10,
    'noFood': 2,
    'noRum': 3,
    'daysAtSea': 1,
    'daysAtSeaReturn': 0.5,
    #TODO lower
    'awolThreshold': 25
}

economy = {
    'buyMul': 1.1,
    'sellMul': 0.9,
    'scarceThreshold': 50,
    'lowThreshold': 100,
    'highThreshold': 200,
    'surplusThreshold': 400,
    'basePrice': {
        'food': 2,
        'rum': 4,
        'wood': 10,
        'cloth': 10,
        'coffee': 20,
        'spice': 25
    },
    'goods':
        ['food','rum','wood','cloth','coffee','spice']
}

news = {
    'genThreshold': 0.4,
    'propogateThreshold': 0.6
}

captains = {
    'genDelay': fps * 30,
    'genThreshold': 0.5,
    'maxCount': 10,
    'fovRecalcCooldown': 2,
    'minRange': 5
}

skill = {
    'max': 20,
    'navDays': 5,
    'gunShots': 50
}

damage = {
    'rocks': 5,
    #TODO use this in damage calc
    'gunMod': 1.5
}

rep = {
    'attack': 10,
    'sink': 10,
    'threshold': 40
}


ship = {
    'minView': 6,
    'maxView': 20,
    'coolDown': fps# * 5
}
