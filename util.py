from RoguePy.UI import Colors
from RoguePy.libtcod import libtcod
from math import pi

rand = libtcod.random_get_instance()

def randint(mx, mn=0):
    return libtcod.random_get_int(rand, mn, mx)

def randfloat(mx, mn=0):
    return libtcod.random_get_float(rand, mn, mx)


degToRad = pi / 180
radToDeg = 180 / pi

def getColor(val):
    clr = Colors.dark_red
    if val <= 20:
        clr = Colors.dark_green
    elif val <= 50:
        clr = Colors.dark_lime
    elif val <= 80:
        clr = Colors.dark_orange
    return clr

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
    
    return \
        first[randint(len(first) -1)] + " " + \
        middle[randint(len(middle) -1)] + " " + \
        last[randint(len(last) -1)]
