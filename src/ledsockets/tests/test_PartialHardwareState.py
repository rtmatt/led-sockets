# File: src/ledsockets/tests/test_PartialHardwareState.py

import unittest

from ledsockets.dto.AbstractDto import DTOInvalidPayloadException
from ledsockets.dto.PartialHardwareState import PartialHardwareState
from ledsockets.dto.UiClient import UiClient
from ledsockets.support.Message import Message


class TestPartialHardwareState(unittest.TestCase):
    def test_initialization_with_attributes(self):
        """Test initialization with provided attributes."""
        state = PartialHardwareState(on=True, message="Test message", id="1234")
        self.assertEqual(state.on, True)
        self.assertEqual(state.message, "Test message")
        self.assertEqual(state.id, "1234")

    def test_initialization_without_attributes(self):
        """Test initialization without attributes."""
        state = PartialHardwareState()
        self.assertIsNone(state.on)
        self.assertIsNone(state.message)
        self.assertEqual(state.id, "")

    def test_get_attributes_when_set(self):
        """Test get_attributes() returns correct values when attributes are set."""
        state = PartialHardwareState(on=True, message="active")
        attributes = state.get_attributes()
        self.assertEqual(attributes, {"on": True, "message": "active"})

    def test_get_attributes_when_empty(self):
        """Test get_attributes() returns an empty dictionary when no attributes are set."""
        state = PartialHardwareState()
        attributes = state.get_attributes()
        self.assertEqual(attributes, {})

    def test_inst_from_attributes_creates_instance_correctly(self):
        """Test _inst_from_attributes() correctly creates an instance with attributes."""
        attributes = {"on": False, "message": "inactive"}
        state = PartialHardwareState._inst_from_attributes(attributes, id="123")
        self.assertEqual(state.on, False)
        self.assertEqual(state.message, "inactive")
        self.assertEqual(state.id, "123")

    def test_from_message_valid_message(self):
        """Test from_message() parses a valid Message object correctly."""
        payload = {
            "data": {
                "type": "hardware_state_partial",
                "attributes": {"on": True, "message": "Test"},
                "id": "5678",
                "relationships": {
                    "source": {
                        "data": {"type": "ui_client", "attributes": {"name": "Client A"}, "id": "client_1"}
                    }
                },
            }
        }
        message = Message(type="patch_hardware_state", payload=payload)
        state = PartialHardwareState.from_message(message)
        self.assertEqual(state.on, True)
        self.assertEqual(state.message, "Test")
        self.assertEqual(state.id, "5678")
        self.assertIn("source", state.get_relationships())

    def test_from_message_invalid_type(self):
        """Test from_message() raises exception for invalid message type."""
        payload = {
            "data": {
                "type": "invalid_type",
                "attributes": {"on": True},
            }
        }
        message = Message(type="patch_hardware_state", payload=payload)
        with self.assertRaises(DTOInvalidPayloadException):
            PartialHardwareState.from_message(message)

    def test_from_message_missing_attributes(self):
        """Test from_message() raises exception for missing attributes in payload."""
        payload = {
            "data": {
                "type": "patch_hardware_state",
                # No "attributes" key
                "id": "5678",
            }
        }
        message = Message(type="patch_hardware_state", payload=payload)
        with self.assertRaises(DTOInvalidPayloadException):
            PartialHardwareState.from_message(message)

    def test_from_message_parses_source_relations_from_ui_client(self):
        """Test from_message() creates "source" relations out of UI client data."""
        payload = {
            "data": {
                "type": "hardware_state_partial",
                "attributes": {"on": True, "message": "Test"},
                "id": "5678",
                "relationships": {
                    "source": {
                        "data": {"type": "ui_client", "attributes": {"name": "Client A"}, "id": "client_1"}
                    }
                },
            }
        }
        message = Message(type="patch_hardware_state", payload=payload)
        state = PartialHardwareState.from_message(message)
        dict = state.toDict()
        self.assertEqual(dict['relationships']['source']['data']['type'], 'ui_client')
        self.assertEqual(dict['relationships']['source']['data']['id'], 'client_1')
        self.assertEqual(dict['relationships']['source']['data']['attributes']['name'], 'Client A')


if __name__ == "__main__":
    unittest.main()
