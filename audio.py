"""Quiet procedural arcade cues; no external sound files are required."""
from __future__ import annotations
from array import array
import math, pygame

class AudioBus:
    def __init__(self, muted=False):
        self.muted=muted; self.sounds={}
        try:
            if not pygame.mixer.get_init(): pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.sounds={'coin':self._tone(660,.045,.10),'power':self._tone(330,.18,.12),'ghost':self._tone(880,.12,.12),'lost':self._tone(125,.25,.10),'clear':self._tone(520,.22,.12),'over':self._tone(90,.3,.10),'menu':self._tone(440,.04,.07)}
        except pygame.error: self.sounds={}
    @staticmethod
    def _tone(freq,duration,volume):
        rate=22050;count=int(rate*duration);data=array('h',(int(math.sin(2*math.pi*freq*i/rate)*32767*volume*(1-i/count)) for i in range(count)))
        return pygame.mixer.Sound(buffer=data.tobytes())
    def play(self,event):
        if not self.muted and event in self.sounds:self.sounds[event].play()
