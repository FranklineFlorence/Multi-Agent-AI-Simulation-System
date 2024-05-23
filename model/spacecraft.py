from __future__ import annotations
from typing import List, TYPE_CHECKING
from model.agent import Agent
from model.rover import Rover
from model.rock import Rock

if TYPE_CHECKING:
    from model.location import Location
    from model.mars import Mars


class Spacecraft(Agent):

    def __init__(self, location: Location):
        super().__init__(location)
        # self.__total_rocks_collected = 0
        self.__collected_rocks: List[Rock] = []
        self.__remembered_rock_locations: List[Location] = []
        self.__assigned_rovers: dict[Rover, Location] = {}

    def __str__(self) -> str:
        return (f"Spacecraft is located at: ({repr(self.get_location())})"
                f" rocks collected")

    def act(self, mars: Mars) -> None:
        found_rovers = self.__scan_for_rovers_in_adjacent_cells(mars)
        if found_rovers:
            for rover in found_rovers:
                if rover.has_rock():
                    self.__collect_rock_from_rover(rover)
                    rover.get_remembered_rock_locations()
                    rover.recharge(100.0)
                    self.__assign_target_location_to_rover(rover)
                    print(f"------------------------------------------------"
                          f"Spacecraft collected a rock from rover {rover.get_id()}. "
                          f"Total rocks collected: {len(self.__collected_rocks)}"
                          f"------------------------------------------------")

                # if rover.get_battery_level() == 0:
                #     self.send_help(rover, mars)

    def __scan_for_rovers_in_adjacent_cells(self, mars: Mars) -> List[Rover]:
        adjacent_locations = mars.get_adjacent_locations(self.get_location())
        found_rovers = []
        for adjacent_location in adjacent_locations:
            agent = mars.get_agent(adjacent_location)
            if isinstance(agent, Rover):
                found_rovers.append(agent)
        return found_rovers

    def __collect_rock_from_rover(self, rover: Rover) -> None:
        rock = rover.get_rock()
        if rock:
            self.__collected_rocks.append(rock)  # Store the rock in the spacecraft
            rover.drop_rock()  # Drop the rock from the rover
            self.receive_rock_locations(rover.get_remembered_rock_locations())
        # self.remove_remembered_rock_location(rover.get_location())

    def remove_remembered_rock_location(self, location: Location) -> None:
        if location in self.__remembered_rock_locations:
            self.__remembered_rock_locations.remove(location)

    def receive_rock_locations(self, rock_locations: List[Location]) -> None:
        for location in rock_locations:
            if location not in self.__remembered_rock_locations and location not in self.__assigned_rovers.values():
                self.__remembered_rock_locations.append(location)
        # print(f"Spacecraft received rock locations: {rock_locations}")
        # Remove already assigned target locations
        self.__remove_assigned_locations()

    def __remove_assigned_locations(self) -> None:
        self.__remembered_rock_locations = [location for location in self.__remembered_rock_locations if
                                            location not in self.__assigned_rovers.values()]

    def send_help(self, rover_in_need: Rover, mars: Mars) -> None:
        found_rovers = self.__scan_for_rovers_in_adjacent_cells(mars)
        for rover in found_rovers:
            if rover != rover_in_need and rover.get_battery_level() > 50:
                rover.share_battery(rover_in_need)
                print(f"Spacecraft coordinated help: {rover} shared battery with {rover_in_need}")
                return
        print(f"Spacecraft could not find a rover to help {rover_in_need}")

    def get_remembered_rock_locations(self) -> List[Location]:
        return self.__remembered_rock_locations

    def __assign_target_location_to_rover(self, rover: Rover) -> None:
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
                print(f"Rover {rover.get_id()} assigned to target location: {location}")
                break
        else:
            print(f"No available target locations for rover {rover.get_id()}")
    """
    def create_new_rover(self, mars: Mars) -> None:
        if self.__total_rocks_collected >= 100:
            free_locations = mars.get_free_adjacent_locations(self.get_location())
            if free_locations:
                new_location = random.choice(free_locations)
                new_rover = Rover(new_location, self.get_location())
                mars.add_agent(new_rover)
                self.__total_rocks_collected -= 100
                print(f"New rover created at location {new_location}")
    """
