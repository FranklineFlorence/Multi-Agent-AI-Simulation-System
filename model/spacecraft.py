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

