import pygame.mixer as mixer
import os

path = os.path.dirname(os.path.abspath(__file__))

mixer.pre_init(44100, -16, 2, 4096) #frequency, size, channels, buffersize
mixer.init()
mixer.music.set_volume(0.1)

# combatHitSound = mixer.Sound(os.path.join(path, 'combatHit.wav'))
# combatMissSound = mixer.Sound(os.path.join(path, 'combatMiss.wav'))
# craftSound = mixer.Sound(os.path.join(path, 'craft.wav'))
# dieSound = mixer.Sound(os.path.join(path, 'die.wav'))
# digSound = mixer.Sound(os.path.join(path, 'dig.wav'))
# fallSound = mixer.Sound(os.path.join(path, 'fall.wav'))
# pickupSound = mixer.Sound(os.path.join(path, 'pickup.wav'))
# waterSound = mixer.Sound(os.path.join(path, 'water.wav'))
# fireSound = mixer.Sound(os.path.join(path, 'fire.wav'))

hire = mixer.Sound(os.path.join(path, 'hire.wav'))
buy = mixer.Sound(os.path.join(path, 'buy.wav'))
fail = mixer.Sound(os.path.join(path, 'fail.wav'))
anchor = mixer.Sound(os.path.join(path, 'anchor.wav'))
cannon = mixer.Sound(os.path.join(path, 'cannon.wav'))
miss = mixer.Sound(os.path.join(path, 'miss.wav'))
hit = mixer.Sound(os.path.join(path, 'hit.wav')) 
sink = mixer.Sound(os.path.join(path, 'sink.wav'))
eat = mixer.Sound(os.path.join(path, 'eat.wav')) 
drink = mixer.Sound(os.path.join(path, 'drink.wav')) 
buyRound = mixer.Sound(os.path.join(path, 'buyRound.wav')) 
repairHull = mixer.Sound(os.path.join(path, 'repairHull`.wav'))
repairSail = mixer.Sound(os.path.join(path, 'repairSail.wav'))
tavern = mixer.Sound(os.path.join(path, 'tavern.wav'))
store = mixer.Sound(os.path.join(path, 'store.wav'))
castOff = mixer.Sound(os.path.join(path, 'castOff.wav'))
skillUp = mixer.Sound(os.path.join(path, 'skillUp.wav'))
noGossip = mixer.Sound(os.path.join(path, 'noGossip.wav'))
gossip = mixer.Sound(os.path.join(path, 'gossip.wav'))
brothel = mixer.Sound(os.path.join(path, 'brothel.wav'))
lowMorale = mixer.Sound(os.path.join(path, 'lowMorale.wav'))
shipyard = mixer.Sound(os.path.join(path, 'shipyard.wav'))
spawn = mixer.Sound(os.path.join(path, 'spawn.wav'))
gameover = mixer.Sound(os.path.join(path, 'gameover.wav'))

gossip.set_volume(0.1)

def setMusicVolume(val):
    mixer.music.set_volume(val)
def getMusicVolume():
    return mixer.music.get_volume()