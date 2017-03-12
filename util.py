import config
from RoguePy.UI import Colors
from RoguePy.libtcod import libtcod
from math import pi, atan2

rand = libtcod.random_get_instance()

def randint(mx, mn=0):
    return libtcod.random_get_int(rand, mn, mx)

def randfloat(mx, mn=0):
    return libtcod.random_get_float(rand, mn, mx)

degToRad = pi / 180
radToDeg = 180 / pi
halfPi = pi / 2
twoPi = pi * 2

def bearing(ax, ay, bx, by):
    theta = -1*(atan2(bx - ax, ay - by) - halfPi)
    if theta < 0.0:
        theta += twoPi
    return radToDeg * theta

colors = [
    Colors.dark_green,
    Colors.dark_yellow,
    Colors.dark_orange,
    Colors.dark_red
]
indexes = [0, 33, 66, 100]
colorMap = libtcod.color_gen_map(colors, indexes)

# Returns a red -> green gradient color for values 0 - 100
def getColor(val):
    return colorMap[val]

def getPirateName():

    first = [
        "Captain",
        "Fluffbucket",
        "Dirty",
        "Squidlips",
        "Bowman",
        "Buccaneer",
        "Two Toes",
        "Sharkbait",
        "Ol'",
        "Peg Leg",
        "Scallywag",
        "Bucko",
        "Dead man",
        "Matey",
        "Jolly",
        "Stinky",
        "Bloody",
        "Miss",
        "Mad",
        "Red",
        "Lady",
        "Bretheren",
        "Rapscallion",
        "Landlubber",
        "Wench",
        "Freebooter",
        "One Eye",
        "Fishy",
        "Long John",
        "Rogue",
        "Ironhook",
        "Gunpowder",
        "Sassy",
        "Walker"
    ]

    middle = [
        "Creeper",
        "Head",
        "Squiffy",
        "Jim",
        "Cackle",
        "Gold",
        "Storm",
        "Patch",
        "Yellow",
        "John",
        "Bones",
        "Felony",
        "George",
        "Plank",
        "Eddie",
        "Greedy",
        "Bay",
        "Rat",
        "Sea",
        "Thomas",
        "Jack",
        "Mama",
        "Spot",
        "Legs",
        "Spike",
        "Lagoon",
        "Stubbs",
        "Slappy",
        "Claw",
        "Parrot",
        "Hook",
        "Black Jack"
    ]

    last = [
        "From the West",
        "Kidd",
        "Byrd",
        "O'Malley",
        "Jackson",
        "Barnacle",
        "Sparrow",
        "Holystone",
        "of the Coast",
        "Hornswaggle",
        "Jones",
        "McStinky",
        "Ned Head",
        "Swashbuckler",
        "Bart",
        "Sea Wolf",
        "O'Fish",
        "Beard",
        "Chumbucket",
        "Rivers",
        "Morgan",
        "Tuna Breath",
        "Three Gates",
        "Bailey",
        "of Atlantis",
        "of Dark Water",
        "Skurvy",
        "Sea Rat",
        "McGee",
        "Smuggler",
        "Rat Breath",
        "Slag",
        "of the Sea"
    ]
    
    return "{} {} {}".format(
        first[randint(len(first) - 1)], middle[randint(len(middle) - 1)], last[randint(len(last) - 1)])


def pathFunc(x1, y1, x2, y2, map):

    c = map.getCell(x2, y2)
    if not c:
        return 0
    if c.terrain.passable:
        return 1
    else:
        return 0

def getPath(map):
    path = libtcod.path_new_using_function(config.world['width'], config.world['height'], pathFunc, map, 0)
    return path

def checkPath(map, x1, y1, x2, y2, myPath=None):
    if not myPath:
        path = getPath(map)
        delete = True
    else:
        path = myPath
        delete = False

    c1 = map.getCell(x1, y1)
    c2 = map.getCell(x2, y2)
    # print "Computing from {},{} {} to {},{} {}".format(x1, y1, c1, x2, y2, c2)

    libtcod.path_compute(path, x1, y1, x2, y2)
    s = libtcod.path_size(path)
    if delete:
        deletePath(path)
    if s:
        # print "Got path, length", s
        return True
    else:
        return False

def pathSize(path):
    return libtcod.path_size(path)

def deletePath(path):
    libtcod.path_delete(path)

def pathWalk(path):
    return libtcod.path_walk(path, True)

###################################################
# LEADERBOARD FUNCTIONS

import requests
import json

private = "ss6hMRk1NUWE1cQa6Nt3hggVIwqDH3RUq_mPyjM7jxHQ"
public = "58c36b3ed60245055cd31378"

host = "http://dreamlo.com/lb/"


def addScore(name, score):
    
    url = host + private + "/add/" + name + "/" + str(score)
    response = requests.get(url)
    
    print response.text
    
    
def getScores():
    
    url = host + private + "/json"
    response = requests.get(url)
    
    jsonData = json.loads(response.text)
    
    scores = []
    
    for entry in jsonData['dreamlo']['leaderboard']['entry']:
        
        date = entry['date'].split(" ")[0]
        
        scores.append( entry['name'] + ":" + entry['score'] + ":" + date)
    
    
    return scores