from typing import Dict

from ledsockets.dto.AbstractDto import AbstractDto


class ChangeDetail(AbstractDto):
    TYPE = 'change_detail'

    def __init__(self, new_value: None, old_value: None, description='', source_name='', action_description='',
                 source_type='', source_id='', id=''):
        super().__init__(id)
        self.new_value = new_value
        self.old_value = old_value
        self.description = description
        self.source_name = source_name
        self.action_description = action_description
        self.source_type = source_type
        self.source_id = source_id

    def get_attributes(self):
        return {
            "new_value": self.new_value,
            "old_value": self.old_value,
            "description": self.description,
            "source_name": self.source_name,
            "action_description": self.action_description,
            "source_type": self.source_type,
            "source_id": self.source_id,
        }

    @classmethod
    def _inst_from_attributes(cls, attributes: Dict, id: str = ''):
        return cls(
            attributes.get('new_value'),
            attributes.get('old_value'),
            attributes.get('description'),
            attributes.get('source_name'),
            attributes.get('action_description'),
            attributes.get('source_type'),
            attributes.get('source_id'),
        )
