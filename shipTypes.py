from RoguePy.UI import Colors
from util import randint

shipTypes = {
    "Ship o'Line": {
        'maxSpeed': 25,
        'guns': 50,
        'minCrew': 30,
        'maxCrew': 200,
        'size': 750,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 20000,
        'color': Colors.black
    },
    "Galleon": {
        'maxSpeed': 20,
        'guns': 40,
        'minCrew': 30,
        'maxCrew': 200,
        'size': 650,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 15000,
        'color': Colors.brass
    },
    "Brig": {
        'maxSpeed': 30,
        'guns': 32,
        'minCrew': 25,
        'maxCrew': 150,
        'size': 550,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 10000,
        'color': Colors.darkest_grey
    },
    "Brigantine": {
        'maxSpeed': 35,
        'guns': 16,
        'minCrew': 25,
        'maxCrew': 125,
        'size': 500,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 8000,
        'color': Colors.darkest_sepia
    },
    "Frigate": {
        'maxSpeed': 25,
        'guns': 24,
        'minCrew': 20,
        'maxCrew': 50,
        'size': 300,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 5000,
        'color': Colors.darker_grey
    },
    "Clipper": {
        'maxSpeed': 45,
        'guns': 16,
        'minCrew': 20,
        'maxCrew': 45,
        'size': 250,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 3000,
        'color': Colors.darker_blue
    },
    "Schooner": {
        'maxSpeed': 40,
        'guns': 12,
        'minCrew': 15,
        'maxCrew': 30,
        'size': 150,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 1000,
        'color': Colors.dark_blue
    },
    "Sloop": {
        'maxSpeed': 30,
        'guns': 10,
        'minCrew': 5,
        'maxCrew': 20,
        'size': 150,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 500,
        'color': Colors.light_grey
    },
    "Caravel": {
        'maxSpeed': 25,
        'guns': 8,
        'minCrew': 5,
        'maxCrew': 15,
        'size': 100,
        'hullDamage': 0,
        'sailDamage': 0,
        'price': 450,
        'color': Colors.white
    }
}

def getRandomType():
    types = shipTypes.keys()
    return types[randint(len(types) - 1)]
