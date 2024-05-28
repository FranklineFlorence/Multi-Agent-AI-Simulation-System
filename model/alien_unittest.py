import unittest
from model.alien import Alien
from model.mars import Mars
from model.location import Location
from model.rover import Rover


class TestAlien(unittest.TestCase):

    def setUp(self):
        self.mars = Mars()
        self.alien_location = Location(0, 0)
        self.alien = Alien(self.alien_location)

    def test_sense_spacecraft_location(self):
        spacecraft_location = Location(1, 0)
        self.mars.set_agent(None, spacecraft_location)
        self.mars.set_agent(self.alien, self.alien_location)

        sensed_location = self.alien._Alien__sense_spacecraft_location(self.mars)

        self.assertNotEqual(sensed_location, spacecraft_location)

    def test_is_near_spacecraft(self):
        spacecraft_location = Location(1, 0)
        self.assertTrue(self.alien._Alien__is_near_spacecraft(self.mars, spacecraft_location))

    def test_move_away_from_spacecraft(self):
        spacecraft_location = Location(1, 0)
        self.alien._Alien__move_away_from_spacecraft(self.mars, spacecraft_location)

        self.assertNotEqual(self.alien_location, self.alien.get_location())

    def test_move_randomly(self):
        initial_location = self.alien.get_location()
        self.alien._Alien__move_randomly(self.mars)

        self.assertNotEqual(initial_location, self.alien.get_location())

    def test_scan_for_rovers(self):
        rover_location = Location(1, 0)
        rover = Rover(rover_location, self.alien_location)
        self.mars.set_agent(rover, rover_location)

        rovers = self.alien._Alien__scan_for_rovers(self.mars)

        self.assertIn(rover, rovers)

    def test_choose_rover_to_chase(self):
        rover_location = Location(1, 0)
        rover = Rover(rover_location, self.alien_location)
        rovers = [rover]

        chosen_rover = self.alien._Alien__choose_rover_to_chase(rovers)

        self.assertEqual(chosen_rover, rover)

    def test_move_towards_rover(self):
        rover_location = Location(1, 0)
        rover = Rover(rover_location, self.alien_location)
        self.mars.set_agent(rover, rover_location)

        initial_location = self.alien.get_location()
        self.alien._Alien__move_towards_rover(self.mars, rover)

        self.assertEqual(initial_location, self.alien.get_location())

    def test_is_adjacent_to_chasing_rover(self):
        rover_location = Location(1, 0)
        rover = Rover(rover_location, self.alien_location)
        self.mars.set_agent(rover, rover_location)

        self.assertTrue(self.alien._Alien__is_adjacent_to_chasing_rover(self.mars, rover))

    def test_attack_rover(self):
        rover_location = Location(1, 0)
        rover = Rover(rover_location, self.alien_location)
        self.mars.set_agent(rover, rover_location)

        initial_energy = self.alien._Alien__energy
        initial_rover_shield = rover.get_shield()
        self.alien._Alien__attack_rover(rover)

        self.assertEqual(self.alien._Alien__energy, initial_energy - 20)
        self.assertEqual(rover.get_shield(), initial_rover_shield - 25)

    def test_restore_energy(self):
        self.alien._Alien__energy = 50
        self.alien._Alien__hibernating = True

        self.alien._Alien__restore_energy()

        self.assertEqual(self.alien._Alien__energy, 60)
        self.assertTrue(self.alien._Alien__hibernating)


if __name__ == '__main__':
    unittest.main()
