from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Optional
from model.rover import Rover
from controller.config import Config
from model.agent import Agent
from model.spacecraft import Spacecraft
from model.location import Location  # Import Location class

if TYPE_CHECKING:
    from model.mars import Mars
    from model.rover import Rover


class Alien(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location)
        self.__energy = 100
        self.__hibernating = False
