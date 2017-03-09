#TODO set this to a reasonable value
fps = 999
spf = 1.0/fps

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
    'impact': 0.1,
    'maxSpeed': 20.0,
    'speedJitter': 1.0,
    'dirJitter': 5.0
}

city = {
    'possibleShops': [
        'tavern',
        'gossip',
        'brothel',
        'shipyard'
    ]
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

economy = {
    'buyMul': 1.1,
    'sellMul': 0.9,
    'lowThreshold': 50,
    'highThreshold': 1000,
    'basePrice': {
        'food': 3,
        'rum': 5,
        'wood': 10,
        'cloth': 10,
        'coffee': 20,
        'spice': 25
    }
}

maxSails = 10
sailStep = 1.0 / maxSails

speedAdjust = 0.1
