import unittest

from ledsockets.support.NameBroker import NameBroker


class TestNameBroker(unittest.TestCase):

    def test_initialization_creates_empty_name_set(self):
        """Test that NameBroker initializes with an empty set of active names."""
        broker = NameBroker()
        self.assertEqual(len(broker._active_names), 0)

    def test_reserve_name_adds_name_to_set(self):
        """Test that reserving a name adds it to the active names set."""
        broker = NameBroker()
        broker.reserve_name("test_name")
        self.assertIn("test_name", broker._active_names)

    def test_release_name_removes_name_from_set(self):
        """Test that releasing a name removes it from the active names set."""
        broker = NameBroker()
        broker.reserve_name("test_name")
        broker.release_name("test_name")
        self.assertNotIn("test_name", broker._active_names)

    def test_name_available_checks_name_exists(self):
        """Test that name_available returns True if the name is not active and False if it is."""
        broker = NameBroker()
        self.assertTrue(broker.name_available("test_name"))
        broker.reserve_name("test_name")
        self.assertFalse(broker.name_available("test_name"))
        broker.release_name("test_name")
        self.assertTrue(broker.name_available("test_name"))

    def test_get_name_returns_faker_name(self):
        """Test that get_name returns a faker-generated string"""
        broker = NameBroker()
        self.assertIsInstance(broker.get_name(), str)

    def test_get_name_returns_preferred_name_if_available(self):
        """Test that get_name returns provided preferred name if available"""
        broker = NameBroker()
        expected = "test_name"
        name = broker.get_name(expected)
        self.assertEqual(expected, name)

    def test_get_name_returns_faker_name_if_preferred_name_unavailable(self):
        """Test that get_name returns a faker name if provided preferred name is unavailable"""
        broker = NameBroker()
        name = broker.get_name()
        name2 = broker.get_name(name)

        self.assertIsInstance(name, str)
        self.assertIsInstance(name2, str)
        self.assertNotEqual(name, name2)


if __name__ == "__main__":
    unittest.main()
