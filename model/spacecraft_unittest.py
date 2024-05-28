import unittest
from model.spacecraft import Spacecraft
from model.location import Location
from model.mars import Mars
from model.rover import Rover
from model.rock import Rock


class TestSpacecraft(unittest.TestCase):

    def setUp(self):
        self.spacecraft_location = Location(0, 0)
        self.spacecraft = Spacecraft(self.spacecraft_location)
        self.mars = Mars()

    def test_collect_rock_from_rover(self):
        rover_location = Location(1, 1)
        rover = Rover(rover_location, self.spacecraft_location)
        rock_location = Location(2, 2)
        rock = Rock(rock_location)
        rover.set_rock(rock)

        assert self.spacecraft._Spacecraft__collect_rock_from_rover(rover) is None
        assert rock in self.spacecraft._Spacecraft__collected_rocks
        assert rover.get_rock() is None

    def test_receive_rock_locations(self):
        remembered_rock_locations = [Location(1, 1), Location(2, 2), Location(3, 3)]
        self.spacecraft._Spacecraft__remembered_rock_locations = remembered_rock_locations
        self.spacecraft._Spacecraft__assigned_rovers = {
            Rover(Location(4, 4), self.spacecraft_location): Location(1, 1)
        }

        self.spacecraft._Spacecraft__receive_rock_locations([Location(5, 5), Location(6, 6)])

        expected_locations = [Location(2, 2), Location(3, 3), Location(5, 5), Location(6, 6)]
        assert self.spacecraft._Spacecraft__remembered_rock_locations == expected_locations

    def test_remove_assigned_locations(self):
        self.spacecraft._Spacecraft__remembered_rock_locations = [Location(1, 1), Location(2, 2), Location(3, 3)]
        self.spacecraft._Spacecraft__assigned_rovers = {
            Rover(Location(4, 4), self.spacecraft_location): Location(1, 1),
            Rover(Location(5, 5), self.spacecraft_location): Location(2, 2)
        }

        self.spacecraft._Spacecraft__remove_assigned_locations()

        expected_locations = [Location(3, 3)]
        assert self.spacecraft._Spacecraft__remembered_rock_locations == expected_locations

    def test_assign_target_location_to_rover(self):
        rover = Rover(Location(4, 4), self.spacecraft_location)
        remembered_rock_locations = [Location(1, 1), Location(2, 2), Location(3, 3)]
        self.spacecraft._Spacecraft__remembered_rock_locations = remembered_rock_locations

        self.spacecraft._Spacecraft__assign_target_location_to_rover(rover)

        assert rover in self.spacecraft._Spacecraft__assigned_rovers
        assert self.spacecraft._Spacecraft__assigned_rovers[rover] is not None

    def test_create_new_rover(self):
        free_locations = [Location(0, 1)]
        self.mars.get_free_adjacent_locations = lambda location: free_locations

        self.spacecraft._Spacecraft__create_new_rover(self.mars)

        assert self.mars.get_agent(Location(0, 1)) is not None

    def test_scan_for_rovers_in_adjacent_cells(self):
        adjacent_location = Location(1, 0)
        rover = Rover(adjacent_location, self.spacecraft_location)
        self.mars.set_agent(rover, adjacent_location)

        adjacent_locations = self.mars.get_adjacent_locations(self.spacecraft_location)
        rovers = self.spacecraft._Spacecraft__scan_for_rovers_in_adjacent_cells(self.mars)

        self.assertIn(rover, rovers)
        self.assertEqual(len(rovers), 1)


if __name__ == '__main__':
    unittest.main()
