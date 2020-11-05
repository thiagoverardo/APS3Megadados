# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

import uuid  # uuid: unique id


# pylint: disable=too-few-public-methods
class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )
    uuid_user: uuid.UUID = Field(
        title='uuid of user linked to rask',
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                'uuid_user': 'e4415e56-bad0-4c0a-9b19-d3504e4dc1f1',
            }
        }

# user


class User(BaseModel):
    name: str = Field(
        title='User name',
        max_length=32,
    )

    class Config:
        schema_extra = {
            'example': {
                'name': 'vitor',
            }
        }
