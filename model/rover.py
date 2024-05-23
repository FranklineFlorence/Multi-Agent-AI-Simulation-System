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

    """
    ===== Display ID =====
    """
    def get_id(self) -> int:
        return self.__id

    """
    ===== Functions for Movement =====
    """

    def __move(self, mars, new_location: Location) -> None:
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)
        if self.__rock:
            self.__rock.set_location(new_location)
        self.__battery_level -= 5.0  # Decrease battery level with each move

    def __move_to_random_location(self, mars: Mars) -> None:
        free_locations = mars.get_free_adjacent_locations(self.get_location())
        if free_locations and self.__battery_level >= 5.0:
            random_free_location = random.choice(free_locations)
            self.__move(mars, random_free_location)
        else:
            # If there are no free adjacent locations, move to any available free location on the map
            all_free_locations = mars.get_free_locations()
            if all_free_locations and self.__battery_level >= 5.0:
                random_free_location = random.choice(all_free_locations)
                self.__move(mars, random_free_location)
            else:
                print(f"Rover {self.__id} cannot move due to low battery or no free locations.")

    def __move_towards_spacecraft(self, mars: Mars) -> bool:
        current_x = self.get_location().get_x()
        current_y = self.get_location().get_y()
        dx = current_x - self.__space_craft_location.get_x()
        dy = current_y - self.__space_craft_location.get_y()
        dir_x = -1 if dx > 0 else 1 if dx < 0 else 0
        dir_y = -1 if dy > 0 else 1 if dy < 0 else 0
        new_location = Location(current_x + dir_x, current_y + dir_y)

        free_adjacent_locations = mars.get_free_adjacent_locations(self.get_location())
        if new_location in free_adjacent_locations:
            self.__move(mars, new_location)
            return self.__is_adjacent_to(mars, self.__space_craft_location)
        else:
            self.__move_to_random_location(mars)
        return False

    def __move_towards_rock(self, mars: Mars, target_location: Location) -> None:
        current_x = self.get_location().get_x()
        current_y = self.get_location().get_y()
        dx = target_location.get_x() - current_x
        dy = target_location.get_y() - current_y
        dir_x = 1 if dx > 0 else -1 if dx < 0 else 0
        dir_y = 1 if dy > 0 else -1 if dy < 0 else 0
        new_location = Location(current_x + dir_x, current_y + dir_y)

        free_adjacent_locations = mars.get_free_adjacent_locations(self.get_location())
        if new_location in free_adjacent_locations:
            self.__move(mars, new_location)
        else:
            self.__move_to_random_location(mars)

    """
    ===== Functions for Rock Handling =====
    """
    def __pick_up_rock(self, mars: Mars, rock: Rock):

        if rock is not None:
            print(f"Rover {self.__id} is picking up the rock at location: {rock.get_location()}")
            self.__rock = rock
            self.__move(mars, rock.get_location())

            # Remove the picked-up rock location from remembered rock locations
            if rock.get_location() in self.__remembered_rock_locations:
                self.__remembered_rock_locations.remove(rock.get_location())

            self.__target_location = None
        else:
            print("Error: Cannot pick up rock. The rock object is None.")

    def has_rock(self) -> bool:
        return self.__rock is not None

    def drop_rock(self) -> None:
        if self.__rock:
            self.__rock = None

    def get_rock(self):
        """Return the rock the rover is carrying, if any."""
        return self.__rock

    def set_rock(self, rock):
        """Set the rock the rover is carrying."""
        self.__rock = rock

    """
    ===== Functions for Rock Management =====
    """
    def __remember_rock_location(self, location: Location) -> None:
        if location not in self.__remembered_rock_locations:
            self.__remembered_rock_locations.append(location)

    def get_remembered_rock_locations(self) -> List[Location]:
        return self.__remembered_rock_locations

    def __select_target_rock(self) -> Optional[Location]:
        if self.__remembered_rock_locations:
            return self.__remembered_rock_locations.pop(0)
        return None

    def set_target_location(self, location: Location) -> None:
        self.__target_location = location

    def get_target_location(self) -> Location:
        return self.__target_location

    def __pass_rock_to_rover(self, other_rover: Rover) -> None:
        if self.__rock:
            other_rover.__rock = self.__rock
            self.__rock = None
