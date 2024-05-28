import unittest
from model.rover import Rover
from model.location import Location
from model.mars import Mars
from model.rock import Rock


class TestRover(unittest.TestCase):

    def setUp(self):
        self.rover_location = Location(0, 0)
        self.space_craft_location = Location(1, 1)
        self.rover = Rover(self.rover_location, self.space_craft_location)
        self.mars = Mars()

    def test_get_id(self):
        Rover._Rover__next_id = 1  # Resetting the ID counter
        self.rover = Rover(self.rover_location, self.space_craft_location)
        self.assertEqual(self.rover.get_id(), 1)

    def test_move_agent_to_new_location(self):
        self.rover_location = Location(0, 0)
        self.new_location = Location(1, 1)
        self.rover = Rover(self.rover_location, Location(5, 5))
        self.rover._Rover__move(self.mars, self.new_location)
        self.assertIs(self.mars.get_agent(self.new_location), self.rover)

    def test_clear_previous_location(self):
        self.rover_location = Location(0, 0)
        self.new_location = Location(1, 1)
        self.rover = Rover(self.rover_location, Location(5, 5))
        previous_location = self.rover.get_location()
        self.rover._Rover__move(self.mars, self.new_location)
        self.assertIsNone(self.mars.get_agent(previous_location))

    def test_rock_location_update(self):
        self.rover_location = Location(0, 0)
        self.new_location = Location(1, 1)
        self.rover = Rover(self.rover_location, Location(5, 5))
        rock_location = Location(2, 2)
        rock = Rock(rock_location)
        self.rover.set_rock(rock)
        self.rover._Rover__move(self.mars, self.new_location)
        self.assertEqual(self.rover.get_rock().get_location(), self.new_location)

    def test_decrease_battery_level(self):
        self.rover_location = Location(0, 0)
        self.new_location = Location(1, 1)
        self.rover = Rover(self.rover_location, Location(5, 5))
        initial_battery_level = self.rover.get_battery_level()
        self.rover._Rover__move(self.mars, self.new_location)
        self.assertEqual(self.rover.get_battery_level(), initial_battery_level - 5.0)

    def test_move_to_random_location_with_free_adjacent(self):
        # Define a list of adjacent locations
        free_locations = [Location(0, 1), Location(1, 0)]
        # Mock the Mars.get_free_adjacent_locations method to return the list of adjacent locations
        self.mars.get_free_adjacent_locations = lambda location: free_locations

        initial_location = self.rover.get_location()
        initial_battery_level = self.rover.get_battery_level()

        # Call the __move_to_random_location method
        self.rover._Rover__move_to_random_location(self.mars)

        # Check that the rover's location has changed
        assert self.rover.get_location() != initial_location
        # Check that the battery level has decreased by 5.0
        assert self.rover.get_battery_level() == initial_battery_level - 5.0

    def test_move_to_random_location_no_free_adjacent(self):
        # Mock the Mars.get_free_adjacent_locations method to return an empty list
        self.mars.get_free_adjacent_locations = lambda location: []
        # Mock the Mars.get_free_locations method to return a list of free locations
        self.mars.get_free_locations = lambda: [Location(1, 1), Location(2, 2)]

        initial_location = self.rover.get_location()
        initial_battery_level = self.rover.get_battery_level()

        # Call the __move_to_random_location method
        self.rover._Rover__move_to_random_location(self.mars)

        # Check that the rover's location has changed
        assert self.rover.get_location() != initial_location
        # Check that the battery level has decreased by 5.0
        assert self.rover.get_battery_level() == initial_battery_level - 5.0

    def test_get_battery_level(self):
        self.assertEqual(self.rover.get_battery_level(), 100.0)

    def test_recharge(self):
        self.rover.recharge(10.0)
        self.assertEqual(self.rover.get_battery_level(), 100.0)

        self.rover._Rover__battery_level = 50.0
        self.rover.recharge(30.0)
        self.assertEqual(self.rover.get_battery_level(), 80.0)

        self.rover.recharge(50.0)
        self.assertEqual(self.rover.get_battery_level(), 100.0)

    def test_share_battery(self):
        other_rover = Rover(self.rover_location, self.space_craft_location)
        self.rover._Rover__battery_level = 80.0
        self.rover.share_battery(other_rover)
        self.assertEqual(self.rover.get_battery_level(), 50.0)
        self.assertEqual(other_rover.get_battery_level(), 100.0)

        self.rover._Rover__battery_level = 30.0
        self.rover.share_battery(other_rover)
        self.assertEqual(self.rover.get_battery_level(), 30.0)

    def test_act(self):
        # Add specific act-related assertions here based on your Rover class's behavior
        # For example, move to a random location if spacecraft is not found
        initial_location = self.rover.get_location()
        self.rover.act(self.mars)
        self.assertNotEqual(self.rover.get_location(), initial_location)

    def test_pick_up_rock(self):
        rock_location = Location(2, 2)
        rock = Rock(rock_location)
        self.mars.set_agent(rock, rock_location)
        self.rover._Rover__pick_up_rock(self.mars, rock)
        self.assertTrue(self.rover.has_rock())
        self.assertEqual(self.rover.get_rock(), rock)

    def test_remember_rock_location(self):
        self.rover._Rover__remember_rock_location(Location(1, 1))
        self.assertIn(Location(1, 1), self.rover.get_remembered_rock_locations())

    def test_pick_rock_from_rover(self):
        other_rover = Rover(self.rover_location, self.space_craft_location)
        rock = Rock(self.rover_location)
        other_rover.set_rock(rock)

        self.rover.pick_rock_from_rover(other_rover)
        self.assertEqual(self.rover.get_rock(), rock)
        self.assertIsNone(other_rover.get_rock())

    def test_has_rock(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        self.assertFalse(rover.has_rock())
        rock = Rock(Location(0, 0))
        rover.set_rock(rock)
        self.assertTrue(rover.has_rock())

    def test_drop_rock(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        rock = Rock(Location(0, 0))
        rover.set_rock(rock)
        rover.drop_rock()
        self.assertIsNone(rover.get_rock())

    def test_get_remembered_rock_locations(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        rock_location = Location(1, 1)
        rover._Rover__remembered_rock_locations.append(rock_location)
        remembered_locations = rover.get_remembered_rock_locations()
        self.assertEqual(len(remembered_locations), 1)
        self.assertEqual(remembered_locations[0], rock_location)

    def test_set_target_location(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        target_location = Location(1, 1)
        rover.set_target_location(target_location)
        self.assertEqual(rover._Rover__target_location, target_location)

    def test_get_battery_level(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        self.assertEqual(rover.get_battery_level(), 100.0)

    def test_get_shield(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        self.assertEqual(rover.get_shield(), 100)

    def test_recharge(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        rover.recharge(50)
        self.assertEqual(rover.get_battery_level(), 100.0)

    def test_sustain_damage(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        rover.sustain_damage(50)
        self.assertEqual(rover.get_shield(), 50)

    def test_is_destroyed(self):
        rover = Rover(Location(0, 0), Location(0, 0))
        self.assertFalse(rover.is_destroyed())
        rover.sustain_damage(100)
        self.assertTrue(rover.is_destroyed())


if __name__ == '__main__':
    unittest.main()
