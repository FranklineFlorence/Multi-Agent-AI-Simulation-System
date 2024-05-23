from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Optional
from model.rock import Rock
from model.agent import Agent
from model.location import Location

if TYPE_CHECKING:
    from model.mars import Mars
    from model.spacecraft import Spacecraft


class Rover(Agent):
    """
    Represents a rover agent in the simulation.

    Attributes:
        __space_craft_location: The location of the spacecraft the rover is assigned to.
        __rock: The rock picked up by the rover.
    """
    __next_id = 1

    def __init__(self, location: Location, space_craft_location: Location):
        self.__id = Rover.__next_id
        Rover.__next_id += 1
        super().__init__(location)
        self.__space_craft_location = space_craft_location
        self.__rock = None
        self.__battery_level = 100.0  # Initial battery level
        self.__target_location = None
        self.__remembered_rock_locations: List[Location] = []
        self.__destroyed = False
        self.__shield_level = 100

    def __repr__(self) -> str:
        return f"Rover({repr(self.get_location())})"

    def __str__(self) -> str:
        return f"Rover is located at: ({repr(self.get_location())})"

    def __hash__(self) -> int:
        return hash(self.__id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rover):
            return NotImplemented
        return self.__id == other.__id
