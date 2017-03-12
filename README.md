# 7drl2017
My entry in the 2017 Seven Day Roguelike Challenge

Started Sunday, March 5, 2017 - 23:21UTC
Completed Sunday, March 12, 2017 - 23:18UTC


### Requirements
Python 2.7 32bit

Packages:
- pygame
- requests

If you've got python 2.7 32bit installed, installing the packages can be done with:

``` 
pip install pygame
pip install requests
```

### Features

The game plays in real-time, with you controlling the heading and sail adjustment of your ship. Wind blows in roughly from the East, and jitters around, both in strength and direction as time passes, adjust your heading to compensate.

Cities are randomly-sized, and -placed around the procedurally generated map.

Meet up with other captains at sea, and learn about shortage/surpluses of goods in nearby cities and towns, and nearby Pirate threats.

Destroy Pirate ships to earn money from the city they were attacking.

### Gameplay tips

You start your journey by selecting which of the land's major cities to sail out of. You start with a respectable amount of gold, and your first task should be to buy a ship.

Visit the Shipyard ("Y" from the main city screen, if it's not already selected) and use the arrow keys to select a ship that fits your needs.

A ship's hull and sails can be repaired at the Shipyard, where you can also purchase ammo for your cannons. Cannonballs destroy the hull of a ship, while chainshot is intended to disable a ship by taking down its sails. Both are pretty devastating on crew numbers, as well.

Every good ship needs a crew, so your next stop should be at the Tavern ("T"). There, you can hire enough crew ("H") to fulfil your ship's minimum crew needs. If you feel like perking them up a little bit, you can buy them a round ("R") of drinks to increase their morale.

Morale can be increased significantly at the brothel, but you'll be charged quite a bit for it. Might want to save it for after you take out a gold-laden Pirate ship.

Your next stop should be at the general store, for some provisions. Sailors need Food and Rum while at sea, or their morale will decline pretty rapidly. Sail too long without any food in the hold, and sailors will start to die off. Sailors do NOT like watching their friends starve to death. Morale will decline sharply when this starts happening.

If any goods seem to be particularly abundant, you may want to pick some up to carry off to another port of call to try and turn a profit.

Time to cast off! Press "D" to leave the city, and you'll find yourself in an adjacent tile. Control the heading of your ship with "A/D", the left/right arrow keys, or numpad 4/6. the ship's current heading is displayed on the top left corner of the info pane. to its right is the wind direction indicator. Keep an eye on it, as strong winds can be quite hard to sail against. You can always put down your anchor, with SPACE, and the ship will remain in place.

Increase your sails with "W/S", Arrows Up/Dn, or numpad 8/2. The higher the sails setting, the closer to your ship's max speed you'll sail.

Entering a city can be accomplished by setting anchor in any adjacent tile.

...

Profit!
