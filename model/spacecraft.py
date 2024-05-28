from __future__ import annotations
import random
from typing import List, TYPE_CHECKING
from itertools import combinations
from model.agent import Agent
from model.rover import Rover
from model.rock import Rock

if TYPE_CHECKING:
    from model.location import Location
    from model.mars import Mars


class Spacecraft(Agent):
    """
    Represents a spacecraft agent in the simulation.

    Attributes:
        __collected_rocks (List[Rock]): A list of rocks collected by the spacecraft.
        __remembered_rock_locations (List[Location]): A list of remembered locations of rocks.
        __assigned_rovers (dict[Rover, Location]): A dictionary mapping rovers to their assigned locations.
    """

    def __init__(self, location: Location):
        """
        Initialize the Spacecraft object.

        Args:
            location (Location): The initial location of the spacecraft.
        """
        super().__init__(location)
        self.__collected_rocks: List[Rock] = []
        self.__remembered_rock_locations: List[Location] = []
        self.__assigned_rovers: dict[Rover, Location] = {}

    def __str__(self) -> str:
        """
        Get a string representation of the spacecraft.

        Returns:
            str: A string representing the spacecraft's location and the number of rocks collected.
        """
        return (f"Spacecraft is located at: ({repr(self.get_location())})"
                f" rocks collected")

    def act(self, mars: Mars) -> None:
        """
        Perform actions for the spacecraft agent in the simulation.

        Args:
            mars (Mars): The Mars environment.
        """
        found_rovers = self.__scan_for_rovers_in_adjacent_cells(mars)
        if found_rovers:
            for rover in found_rovers:
                if rover.has_rock():
                    self.__collect_rock_from_rover(rover)
                    rover.get_remembered_rock_locations()
                    rover.recharge(100.0)
                    self.__assign_target_location_to_rover(rover)
                    print(f"Spacecraft collected a rock from rover {rover.get_id()}. "
                          f"Total rocks collected: {len(self.__collected_rocks)}")
        # if len(self.__collected_rocks) >= 30:
        #     # Reason to have thirty is because it already means it has collected rocks in the surroundings
        #     print(f"SpaceCraft at {self.get_location()} has collected 30 or more rocks. Initiating collaboration.")
        #     # Identify rovers available for collaboration
        #     available_rovers = self.get_available_rovers(mars)
        #     # Group rovers to retrieve distant rocks
        #     self.group_rovers_to_retrieve_distant_rock(available_rovers, mars)

        if len(self.__collected_rocks) >= 100:
            self.__create_new_rover(mars)

    def __scan_for_rovers_in_adjacent_cells(self, mars: Mars) -> List[Rover]:
        """
        Scan adjacent cells for rovers.

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

    def __collect_rock_from_rover(self, rover: Rover) -> None:
        """
        Collect a rock from a rover.

        Args:
            rover (Rover): The rover from which to collect the rock.
        """
        rock = rover.get_rock()
        if rock:
            self.__collected_rocks.append(rock)  # Store the rock in the spacecraft
            rover.drop_rock()  # Drop the rock from the rover
            self.__receive_rock_locations(rover.get_remembered_rock_locations())

    def __receive_rock_locations(self, rock_locations: List[Location]) -> None:
        """
        Receive locations of rocks from rovers.

        Args:
            rock_locations (List[Location]): A list of rock locations.
        """
        for location in rock_locations:
            if location not in self.__remembered_rock_locations and location not in self.__assigned_rovers.values():
                self.__remembered_rock_locations.append(location)
        # Remove already assigned target locations
        self.__remove_assigned_locations()

    def __remove_assigned_locations(self) -> None:
        """Remove assigned target locations."""
        self.__remembered_rock_locations = [location for location in self.__remembered_rock_locations if
                                            location not in self.__assigned_rovers.values()]

    def __assign_target_location_to_rover(self, rover: Rover) -> None:
        """
        Assign a target location to a rover.

        Args:
            rover (Rover): The rover to assign the target location to.
        """
        if rover in self.__assigned_rovers:
            target_location = self.__assigned_rovers[rover]
            if target_location in self.__remembered_rock_locations:
                return  # Rover is already assigned a valid target location

        # Find the first available remembered rock location
        for location in self.__remembered_rock_locations:
            if location not in self.__assigned_rovers.values():
                self.__assigned_rovers[rover] = location
                rover.set_target_location(location)
                self.__remembered_rock_locations.remove(location)
                # print(f"Rover {rover.get_id()} assigned to target location: {location}")
                break

    def __create_new_rover(self, mars: Mars) -> None:
        """
        Create a new rover in the environment.

        Args:
            mars (Mars): The Mars environment.
        """
        free_locations = mars.get_free_adjacent_locations(self.get_location())
        if free_locations:
            new_location = random.choice(free_locations)
            new_rover = Rover(new_location, self.get_location())
            mars.set_agent(new_rover, new_location)
            self.__collected_rocks = self.__collected_rocks[100:]  # Remove the first 100 collected rocks
            print(f"New rover created at location {new_location}")

    @staticmethod
    def find_common_adjacent_rock_locations(rovers: List[Rover], mars: Mars) -> List[Location]:
        """
        Find common adjacent rock locations for a group of rovers.

        Args:
            rovers (List[Rover]): The list of rovers in the group.
            mars (Mars): The Mars environment.

        Returns:
            List[Location]: A list of common adjacent rock locations for the group of rovers.
        """
        common_adjacent_rock_locations = []
        # Get adjacent locations for the first rover in the group
        first_rover = rovers[0]
        first_rover_adjacent_locations = mars.get_adjacent_locations(first_rover.get_location())
        # Check if each adjacent location has a rock adjacent to all rovers in the group
        for location in first_rover_adjacent_locations:
            if all(mars.get_agent(location) == rover.get_rock() for rover in rovers[1:]):
                common_adjacent_rock_locations.append(location)
        return common_adjacent_rock_locations

    def group_rovers_to_retrieve_distant_rock(self, rovers: List[Rover], mars: Mars) -> None:
        """
        Group rovers together to retrieve a distant rock.

        This method identifies pairs of rovers that can work together to retrieve a distant rock.
        It then instructs these pairs of rovers to collaborate and retrieve the rock.

        Args:
            rovers (List[Rover]): The list of rovers available for collaboration.
            mars (Mars): The Mars environment.
        """
        # Create a list to store the pairs of rovers
        rover_pairs = []
        print("Grouping rovers for collaboration...")

        # Find all possible pairs of rovers
        for rover_pair in combinations(rovers, 2):
            rover_pairs.append(rover_pair)

        # Iterate over the pairs of rovers and instruct them to retrieve a distant rock
        for rover_pair in rover_pairs:
            # Find common adjacent rock locations for the rover pair
            common_adjacent_rock_locations = self.find_common_adjacent_rock_locations(list(rover_pair), mars)
            if common_adjacent_rock_locations:
                print(f"Collaboration initiated between rovers: {[rover.get_id() for rover in rover_pair]}")
                # Instruct the rovers to move towards the common adjacent rock location and pick it up
                for location in common_adjacent_rock_locations:
                    # Set target location for all rovers in the pair
                    for rover in rover_pair:
                        rover.set_target_location(location)
                    # Move all rovers in the pair towards the rock location
                    for rover in rover_pair:
                        rover.act(mars)
                    # Check if the rock is picked up by any rover in the pair
                    if all(location == rover.get_location() for rover in rover_pair):
                        print("Rock picked up by collaborating rovers.")
                        break  # If the rock is picked up by both rovers, break out of the loop

    @staticmethod
    def get_available_rovers(mars: Mars) -> List[Rover]:
        """
        Get a list of available rovers associated with this spacecraft.

        Args:
            mars (Mars): The Mars environment.

        Returns:
            List[Rover]: A list of available rovers.
        """
        return mars.get_all_rovers()
