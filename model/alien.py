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
    """
    Represents an alien agent in the simulation.

    Attributes:
        __energy (int): The energy level of the alien.
        __hibernating (bool): A flag indicating whether the alien is hibernating.
    """
    def __init__(self, location: Location) -> None:
        """
        Initialize the Alien object.

        Args:
            location (Location): The initial location of the alien.
        """
        super().__init__(location)
        self.__energy = 100
        self.__hibernating = False

    def act(self, mars: Mars) -> None:
        """
        Perform actions for the alien agent in the simulation.

        Args:
            mars (Mars): The Mars environment.
        """
        if self.__hibernating:
            self.__restore_energy()
            # print("restoring")
            return

        if self.__energy <= 20:
            self.__hibernating = True
            # print("hibernating")
            return

        spacecraft_location = self.__sense_spacecraft_location(mars)

        if spacecraft_location and self.__is_near_spacecraft(mars, spacecraft_location):
            self.__move_away_from_spacecraft(mars, spacecraft_location)
            # print(f"Alien {self.get_location()} moved away from the spacecraft")
        else:
            rovers = self.__scan_for_rovers(mars)
            if len(rovers) > 0:
                chosen_rover = self.__choose_rover_to_chase(rovers)
                if chosen_rover:
                    self.__move_towards_rover(mars, chosen_rover)
                    print(f"Alien {self.get_location()} chasing rover {chosen_rover.get_id()} {chosen_rover.get_location()}")
                    if self.__is_adjacent_to_chasing_rover(mars, chosen_rover):
                        print("Alien adjacent")
                        self.__attack_rover(chosen_rover)
                        print("Alien attacking")
                        print(f"Rover {chosen_rover.get_id()}- Shield Level: {chosen_rover.get_shield()}")
            else:
                self.__move_randomly(mars)

    def __sense_spacecraft_location(self, mars: Mars) -> Location:
        """
        Sense the location of the spacecraft within a 3-cell radius.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            Location: The sensed location of the spacecraft, if detected.
        """
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
        """
        Check if the alien is near the spacecraft.

        Args:
            mars (Mars): The Mars environment.
            spacecraft_location (Location): The location of the spacecraft.

        Returns:
            bool: True if the alien is near the spacecraft, False otherwise.
        """
        # Check if within 3 cells
        current_location = self.get_location()
        return (abs(current_location.get_x() - spacecraft_location.get_x()) <= 3 and
                abs(current_location.get_y() - spacecraft_location.get_y()) <= 3)

    def __move_away_from_spacecraft(self, mars: Mars, spacecraft_location: Location) -> None:
        """
        Move the alien away from the spacecraft.

        Args:
            mars (Mars): The Mars environment.
            spacecraft_location (Location): The location of the spacecraft.
        """
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
        """
        Move the alien to a new location.

        Args:
            mars (Mars): The Mars environment.
            new_location (Location): The new location to move to.
        """
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)

    def __move_randomly(self, mars: Mars) -> None:
        """
        Move the alien randomly.

        Args:
            mars (Mars): The Mars environment.
        """
        free_locations = mars.get_free_adjacent_locations(self.get_location())
        if free_locations and self.__energy > 0:
            random_free_location = random.choice(free_locations)
            self.__move(mars, random_free_location)

    def __scan_for_rovers(self, mars: Mars) -> List[Rover]:
        """
        Scan for nearby rovers.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            List[Rover]: A list of rovers found nearby.
        """
        current_location = self.get_location()
        found_rovers = []

        # Iterate over a range of offsets for both x and y coordinates
        for x_offset in range(-3, 4):
            for y_offset in range(-3, 4):
                # Calculate the coordinates of the adjacent location
                x = (current_location.get_x() + x_offset) % Config.world_size
                y = (current_location.get_y() + y_offset) % Config.world_size
                adjacent_location = Location(x, y)

                # Check if there's a rover at the adjacent location
                agent = mars.get_agent(adjacent_location)
                if isinstance(agent, Rover):
                    found_rovers.append(agent)
                    # print(f"Alien found rover found at location: {adjacent_location}")

        return found_rovers

    @staticmethod
    def __choose_rover_to_chase(rovers: List[Rover]) -> Optional[Rover]:
        """
        Choose a rover to chase.

        Args:
            rovers (List[Rover]): A list of rovers.

        Returns:
            Optional[Rover]: The chosen rover to chase, or None if no rover is available.
        """
        if len(rovers) > 0:
            return rovers[0]  # Choose the first rover found
        return None

    def __move_towards_rover(self, mars: Mars, rover: Rover):
        """
        Move the alien towards a rover.

        Args:
            mars (Mars): The Mars environment.
            rover (Rover): The rover to move towards.
        """
        current_x = self.get_location().get_x()
        current_y = self.get_location().get_y()
        rover_location = rover.get_location()
        dx = rover_location.get_x() - current_x
        dy = rover_location.get_y() - current_y

        dir_x = 1 if dx > 0 else -1 if dx < 0 else 0
        dir_y = 1 if dy > 0 else -1 if dy < 0 else 0

        new_location = Location(current_x + dir_x, current_y + dir_y)
        if new_location in mars.get_free_adjacent_locations(self.get_location()):
            self.__move(mars, new_location)
            self.__energy -= 20

    def __is_adjacent_to_chasing_rover(self, mars: Mars, rover: Rover):
        """
        Check if the alien is adjacent to the rover it is chasing.

        Args:
            mars (Mars): The Mars environment.
            rover (Rover): The rover being chased.

        Returns:
            bool: True if the alien is adjacent to the chasing rover, False otherwise.
        """
        current_location = self.get_location()
        adjacent_locations = mars.get_adjacent_locations(current_location)
        if rover.get_location() in adjacent_locations:
            return True
        return False

    def __attack_rover(self, rover: Rover):
        """
        Attack a rover.

        Args:
            rover (Rover): The rover being attacked.
        """
        self.__energy -= 20
        # print(f"Alien's current energy level: {self.__energy}")
        rover.sustain_damage(25)
        print(f"Alien attacking Rover {rover.get_id()}")

    def __restore_energy(self):
        """Restore energy levels for the alien."""
        self.__energy = min(self.__energy + 10, 100)
        if self.__energy == 100:
            self.__hibernating = False
