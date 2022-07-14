"""
Holds the logic of what cards to play and when
"""

from abc import ABC, abstractmethod

def BaseCardSelector(ABC):
   """
   Base abstract for picking a card to play
   """

   def __init__(self):
      pass

   def pick_card(self, history, hand,):
      pass

