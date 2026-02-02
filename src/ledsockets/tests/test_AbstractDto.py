# src/ledsockets/tests/test_AbstractDto.py

import json
import unittest
from typing import Dict

from src.ledsockets.dto.AbstractDto import AbstractDto, DTOInvalidPayloadException


class TestDtoClass(AbstractDto):
    TYPE = "test_dto"

    def __init__(self, id='', name='Test Name'):
        super().__init__(id)
        self.name = name

    def get_attributes(self):
        return {"name": self.name}

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        inst = cls(id, attributes.get('name'))
        return inst


class TestAbstractDto(unittest.TestCase):
    def setUp(self):
        self.dto = TestDtoClass("123", "Sample Name")

    def test_from_attributes_valid(self):
        """Test from_attributes correctly initializes an instance."""
        attributes = {"name": "John Doe"}
        dto = TestDtoClass.from_attributes(attributes, "001")
        self.assertEqual(dto.id, "001")
        self.assertEqual(dto.name, "John Doe")

    def test_from_attributes_invalid(self):
        """Test from_attributes raises an exception for invalid attributes."""
        with self.assertRaises(DTOInvalidPayloadException):
            TestDtoClass.from_attributes("not_a_dict", "001")

    def test_from_dict_valid(self):
        """Test from_dict correctly parses a valid dictionary."""
        json_data = {
            "type": "test_dto",
            "id": "002",
            "attributes": {"name": "Jane Doe"}
        }
        dto = TestDtoClass.from_dict(json_data)
        self.assertEqual(dto.id, "002")
        self.assertEqual(dto.name, "Jane Doe")

    def test_from_dict_invalid(self):
        """Test from_dict raises an exception for invalid input."""
        invalid_data = {"type": "wrong_type", "attributes": None}
        with self.assertRaises(DTOInvalidPayloadException):
            TestDtoClass.from_dict(invalid_data)

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
