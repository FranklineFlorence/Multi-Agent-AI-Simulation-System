from __future__ import annotations
import random
from typing import TYPE_CHECKING, List
from model.rock import Rock
from model.agent import Agent
from model.location import Location
if TYPE_CHECKING:
    from model.mars import Mars


class Rover(Agent):
    """
    Represents a rover agent in the simulation.

    Attributes:
        Attributes:
        __next_id (int): The next ID to be assigned to a rover.
        __id (int): The unique identifier of the rover.
        __space_craft_location (Location): The location of the spacecraft the rover is assigned to.
        __rock (Rock): The rock picked up by the rover.
        __battery_level (float): The current battery level of the rover.
        __target_location (Location): The target location the rover is moving towards.
        __remembered_rock_locations (List[Location]): A list of remembered rock locations.
        __shield_level (int): The shield level of the rover.
    """
    __next_id = 1

    def __init__(self, location: Location, space_craft_location: Location):
        """
        Initialize the Rover object.

        Args:
            location (Location): The initial location of the rover.
            space_craft_location (Location): The location of the spacecraft the rover is assigned to.
        """
        self.__id = Rover.__next_id
        Rover.__next_id += 1
        super().__init__(location)
        self.__space_craft_location = space_craft_location
        self.__rock = None
        self.__battery_level = 100.0  # Initial battery level
        self.__target_location = None
        self.__remembered_rock_locations: List[Location] = []
        self.__shield_level = 100

    def __repr__(self) -> str:
        """
        Return a string representation of the rover.

        Returns:
            str: The string representation of the rover.
        """
        return f"Rover({repr(self.get_location())})"

    def __str__(self) -> str:
        """
        Return a string representation of the rover.

        Returns:
            str: The string representation of the rover.
        """
        return f"Rover is located at: ({repr(self.get_location())})"

    def __hash__(self) -> int:
        """
        Return the hash value of the rover.

        Returns:
            int: The hash value of the rover.
        """
        return hash(self.__id)

    def __eq__(self, other: object) -> bool:
        """
        Compare if two rover objects are equal.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the two rover objects are equal, False otherwise.
        """
        if not isinstance(other, Rover):
            return NotImplemented
        return self.__id == other.__id

    """
    ===== Display ID =====
    """
    def get_id(self) -> int:
        """
        Get the ID of the rover.

        Returns:
            int: The ID of the rover.
        """
        return self.__id

    """
    ===== Functions for Movement =====
    """

    def __move(self, mars, new_location: Location) -> None:
        """
        Move the rover to a new location on Mars.

        Args:
            mars (Mars): The Mars environment.
            new_location (Location): The new location where the rover will be moved.
        """
        previous_location = self.get_location()
        mars.set_agent(self, new_location)
        self.set_location(new_location)
        mars.set_agent(None, previous_location)
        if self.__rock:
            self.__rock.set_location(new_location)
        self.__battery_level -= 5.0  # Decrease battery level with each move

    def __move_to_random_location(self, mars: Mars) -> None:
        """
        Move the rover to a randomly selected adjacent location on Mars.

        Args:
            mars (Mars): The Mars environment.
        """
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

    def __move_towards_spacecraft(self, mars: Mars) -> bool:
        """
        Move the rover towards the spacecraft.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            bool: True if the rover is adjacent to the spacecraft after moving, False otherwise.
        """
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
        """
        Move the rover towards a target rock location.

        Args:
            mars (Mars): The Mars environment.
            target_location (Location): The target location of the rock.
        """
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
        """
        Pick up a rock from the Mars environment and update rover's state.

        Args:
            mars (Mars): The Mars environment.
            rock (Rock): The rock to pick up.
        """

        if rock is not None:
            self.__rock = rock
            self.__move(mars, rock.get_location())

            # Remove the picked-up rock location from remembered rock locations
            if rock.get_location() in self.__remembered_rock_locations:
                self.__remembered_rock_locations.remove(rock.get_location())
            self.__target_location = None

    def has_rock(self) -> bool:
        """
        Check if the rover is carrying a rock.

        Returns:
            bool: True if the rover is carrying a rock, False otherwise.
        """
        return self.__rock is not None

    def drop_rock(self) -> None:
        """Drop the rock the rover is carrying."""
        if self.__rock:
            self.__rock = None

    def get_rock(self):
        """
        Get the rock the rover is carrying, if any.

        Returns:
            Rock: The rock the rover is carrying, or None if not carrying any rock.
        """
        return self.__rock

    def set_rock(self, rock):
        """
        Set the rock the rover is carrying.

        Args:
            rock: The rock object to set as the rover's carried rock.
        """
        self.__rock = rock

    """
    ===== Functions for Rock Management =====
    """

    def __remember_rock_location(self, location: Location) -> None:
        """
        Remember the location of a rock on Mars.

        Args:
            location (Location): The location of the rock to remember.
        """
        if location not in self.__remembered_rock_locations:
            self.__remembered_rock_locations.append(location)

    def get_remembered_rock_locations(self) -> List[Location]:
        """
        Get the remembered locations of rocks on Mars.

        Returns:
            List[Location]: A list of remembered rock locations.
        """
        return self.__remembered_rock_locations

    def set_target_location(self, location: Location) -> None:
        """
        Set the target location for the rover.

        Args:
            location (Location): The target location to set.
        """
        self.__target_location = location

    """
    ===== Functions for Scanning =====
    """

    def __scan_for_spacecraft_in_adjacent_cells(self, mars: Mars) -> bool:
        """
        Scan adjacent cells for the presence of a spacecraft and recharge if found.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            bool: True if a spacecraft is found in adjacent cells, False otherwise.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        for loc in adjacent_locations:
            if loc == self.__space_craft_location:
                recharge_amount = 100.0 - self.__battery_level
                self.recharge(recharge_amount)  # Recharge to full battery
                return True
        return False

    def __scan_for_rocks(self, mars: Mars) -> List[Rock]:
        """
        Scan adjacent cells for rocks.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            List[Rock]: A list of rocks found in adjacent cells.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        found_rocks = []
        for adjacent_location in adjacent_locations:
            agent = mars.get_agent(adjacent_location)
            if isinstance(agent, Rock):
                found_rocks.append(agent)
        return found_rocks

    def __is_adjacent_to_target(self, mars: Mars, target_location: Location) -> bool:
        """
        Check if the rover is adjacent to a target location.

        Args:
            mars (Mars): The Mars environment.
            target_location (Location): The target location to check.

        Returns:
            bool: True if the rover is adjacent to the target location, False otherwise.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        for adjacent_location in adjacent_locations:
            if adjacent_location == target_location:
                return True
        return False

    def __scan_for_rovers(self, mars: Mars) -> List[Rover]:
        """
        Scan adjacent cells for other rovers.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            List[Rover]: A list of rovers found in adjacent cells.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        found_rovers = []
        for adjacent_location in adjacent_locations:
            agent = mars.get_agent(adjacent_location)
            if isinstance(agent, Rover):
                found_rovers.append(agent)
        return found_rovers

    def __is_adjacent_to(self, mars: Mars, location: Location) -> bool:
        """
        Check if the rover is adjacent to a specific location.

        Args:
            mars (Mars): The Mars environment.
            location (Location): The location to check adjacency.

        Returns:
            bool: True if the rover is adjacent to the location, False otherwise.
        """
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        return location in adjacent_locations

    """
    ===== Functions for Battery Management =====
    """

    def get_battery_level(self) -> float:
        """
        Get the battery level of the rover.

        Returns:
            float: The battery level of the rover.
        """
        return self.__battery_level

    def get_shield(self) -> int:
        """
        Get the shield level of the rover.

        Returns:
            int: The shield level of the rover.
        """
        return self.__shield_level

    def recharge(self, amount: float):
        """
        Recharge the rover's battery level.

        Args:
            amount (float): The amount by which to recharge the battery level.
        """
        self.__battery_level = min(self.__battery_level + amount, 100.0)

    def share_battery(self, other_rover: Rover):
        """
        Share battery power with another rover.

        Args:
            other_rover (Rover): The rover to share battery power with.
        """
        if self.__battery_level > 50:
            share_amount = self.__battery_level - 50
            self.__battery_level -= share_amount
            other_rover.recharge(share_amount)
            print(f"Rover {self.__id} shared {share_amount} battery with Rover {other_rover.get_id()}")

    def sustain_damage(self, damage):
        """
        Sustain damage to the rover's shield.

        Args:
            damage: The amount of damage sustained.
        """
        self.__shield_level -= damage
        if self.__shield_level <= 0:
            self.__shield_level = 0

    def is_destroyed(self):
        """
        Check if the rover is destroyed.
        """

        return self.__shield_level == 0

    """
    ===== COLLABORATION =====
    """
    def pick_rock_from_rover(self, other_rover: Rover) -> None:
        """
        Pick up a rock from another rover.

        Parameters:
            other_rover (Rover): The other rover from which to pick up the rock.
        """
        print(f"Attempting to pick rock from Rover {other_rover.get_id()} by ##Rover {self.get_id()}")
        rock = other_rover.get_rock()
        if rock and not self.get_rock():
            # Transfer the rock from the other rover to this rover
            self.set_rock(rock)
            other_rover.drop_rock()
            print(f"Rover {self.__id} picked rock from Rover {other_rover.__id}")

    """
    ===== ACT METHOD =====
    """

    def act(self, mars: Mars):
        """
        Define the actions of the rover in the simulation.

        Args:
            mars (Mars): The Mars environment.
        """
        print(f"Rover {self.__id}- Battery level: {self.__battery_level}, Current location: {self.get_location()}")
        if self.__shield_level == 0:
            return
        if self.__battery_level > 0:
            if self.__rock:
                if self.__scan_for_spacecraft_in_adjacent_cells(mars):
                    return
                else:
                    # print(f"Rover {self.__id} moving towards spacecraft.")
                    self.__move_towards_spacecraft(mars)
            elif self.__target_location:
                # print(f"Rover {self.__id} has target")
                if self.__is_adjacent_to_target(mars, self.__target_location):
                    # print("🚀 is adjacent to target")
                    rock_at_target = mars.get_agent(self.__target_location)
                    if isinstance(rock_at_target, Rock):
                        self.__pick_up_rock(mars, rock_at_target)
                        # print(f"Target {self.__target_location} picked!")
                    else:
                        self.__target_location = None
                else:
                    self.__move_towards_rock(mars, self.__target_location)
                    # print(f"Rover {self.__id} moving towards rock at target location: {self.__target_location}")

            else:
                adjacent_rocks = self.__scan_for_rocks(mars)
                if len(adjacent_rocks) > 0:
                    print(f"Rover {self.__id} picking up adjacent rock.")
                    self.__pick_up_rock(mars, adjacent_rocks[0])
                    if len(adjacent_rocks) > 1:
                        remaining_rocks = adjacent_rocks[1:]
                        for rock in remaining_rocks:
                            self.__remember_rock_location(rock.get_location())
                            print(f"Rover {self.__id} remembering rock location =>{rock.get_location()}|")
                else:
                    # print(f"Rover {self.__id} moving to random location.")
                    self.__move_to_random_location(mars)
        else:
            # Check if adjacent to another rover
            if self.__scan_for_spacecraft_in_adjacent_cells(mars):
                self.recharge(100)
            else:
                nearby_rovers = self.__scan_for_rovers(mars)
                for nearby_rover in nearby_rovers:
                    if nearby_rover.get_battery_level() > 50:
                        print(f"Rover {self.__id} requesting battery from nearby rover {nearby_rover.get_id()}")
                        nearby_rover.share_battery(self)
                        if self.__rock is None:
                            self.pick_rock_from_rover(nearby_rover)
