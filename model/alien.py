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

    def __sense_spacecraft_location(self, mars: Mars) -> Location:
        # Sensing spacecraft within a 3-cell radius
        current_location = self.get_location()
        for x_offset in range(-3, 4):
            for y_offset in range(-3, 4):
                x = (current_location.get_x() + x_offset) % Config.world_size
                y = (current_location.get_y() + y_offset) % Config.world_size
                sensed_location = Location(x, y)
                agent = mars.get_agent(sensed_location)
                if isinstance(agent, Spacecraft):
                    # self.__move_away_from_spacecraft(mars, sensed_location)
                    return sensed_location

    def __is_near_spacecraft(self, mars: Mars, spacecraft_location: Location) -> bool:
        # Check if within 3 cells (manhattan distance)
        current_location = self.get_location()
        return (abs(current_location.get_x() - spacecraft_location.get_x()) <= 3 and
                abs(current_location.get_y() - spacecraft_location.get_y()) <= 3)

    def __move_away_from_spacecraft(self, mars: Mars, spacecraft_location: Location) -> None:
        current_location = self.get_location()

        dx = current_location.get_x() - spacecraft_location.get_x()
        dy = current_location.get_y() - spacecraft_location.get_y()

        dir_x = -1 if dx < 0 else 1 if dx > 0 else 0
        dir_y = -1 if dy < 0 else 1 if dy > 0 else 0

        # Calculate the new target location
        target_location = Location(current_location.get_x() + dir_x, current_location.get_y() + dir_y)

        # Get free locations excluding the prohibited zone near the spacecraft
        free_locations = mars.get_free_adjacent_locations(current_location)

        if len(free_locations) > 0:
            if target_location in free_locations:
                self.__move(mars, target_location)
            else:
                # If the chosen location isn't free, move to any available free location
                self.__move(mars, random.choice(free_locations))

    def __move(self, mars: Mars, new_location: Location) -> None:
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)

    def __move_randomly(self, mars: Mars) -> None:
        free_locations = mars.get_free_adjacent_locations(self.get_location())
        if free_locations and self.__energy > 0:
            random_free_location = random.choice(free_locations)
            self.__move(mars, random_free_location)
