# src/ledsockets/tests/test_AbstractDto.py

import json
import unittest

from src.ledsockets.dto.AbstractDto import AbstractDto, DTOInvalidPayloadException


class TestDtoClass(AbstractDto):
    TYPE = "test_dto"

    def __init__(self, id='', name='Test Name'):
        super().__init__(id)
        self.name = name

    def get_attributes(self):
        return {"name": self.name}


class TestAbstractDto(unittest.TestCase):
    def setUp(self):
        self.dto = TestDtoClass("123", "Sample Name")

    def test_to_dict(self):
        """Test the toDict method constructs a dictionary with correct structure."""
        expected = {
            "type": "test_dto",
            "id": "123",
            "attributes": {
                "name": "Sample Name"
            }
        }
        self.assertEqual(expected, self.dto.toDict())

    def test_to_json(self):
        """Test the toJSON method returns a proper JSON string."""
        expected = json.dumps({
            "type": "test_dto",
            "id": "123",
            "attributes": {
                "name": "Sample Name"
            }
        })
        self.assertEqual(expected, self.dto.toJSON())

    def test_relationship_serialization(self):
        """Test the serialization of relationships in toDict."""
        related_dto = TestDtoClass("456", "Related Name")
        self.dto.set_relationship("related", related_dto)
        result = self.dto.toDict()

        self.assertIn("relationships", result)
        self.assertIn("related", result["relationships"])
        self.assertEqual(
            {
                "data": {
                    "type": "test_dto",
                    "id": "456",
                    "attributes": {
                        "name": "Related Name"
                    }
                }
            },
            result["relationships"]["related"]
        )

    def test_append_relationship_multiple_items(self):
        """Test appending multiple items to a relationship key."""
        related_item1 = TestDtoClass("1", "Item 1")
        related_item2 = TestDtoClass("2", "Item 2")
        self.dto.append_relationship("children", related_item1.toDict())
        self.dto.append_relationship("children", related_item2.toDict())

        result = self.dto.toDict()
        self.assertEqual(len(result["relationships"]["children"]["data"]), 2)
        self.assertEqual(
            result["relationships"]["children"]["data"][0]["attributes"]["name"], "Item 1"
        )
        self.assertEqual(
            result["relationships"]["children"]["data"][1]["attributes"]["name"], "Item 2"
        )

    def test_invalid_relationship_payload_set(self):
        """Test that an invalid payload to set_relationship raises an exception."""
        with self.assertRaises(DTOInvalidPayloadException):
            self.dto.set_relationship("invalid", "not_a_dict")

    def test_invalid_relationship_payload_append(self):
        """Test that an invalid payload to append_relationship raises an exception."""
        self.dto.set_relationship("key", {"data": []})  # Ensures relationship exists
        with self.assertRaises(DTOInvalidPayloadException):
            self.dto.append_relationship("key", "not_a_dict")

    def test_remove_relationship(self):
        """Test removing an existing relationship by key."""
        related_dto = TestDtoClass("456", "Test Relationship")
        self.dto.set_relationship("related", related_dto)

        self.assertIn("related", self.dto.toDict()["relationships"])

        self.dto.remove_relationship("related")
        self.assertIsNone(self.dto.toDict().get("relationships"))

    def test_remove_nonexistent_relationship(self):
        """Test removing a nonexistent relationship doesn't raise an error."""
        self.dto.remove_relationship("nonexistent")
        self.assertIsNone(self.dto.get_relationships())


if __name__ == '__main__':
    unittest.main()
