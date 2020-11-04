# pylint: disable=missing-module-docstring
from fastapi import FastAPI

from .routers import task, user

tags_metadata = [
    {
        'name': 'task',
        'description': 'Operations related to tasks.',
    },
    {
        'name': 'user',
        'description': 'Operations related to users.',
    },
]

app = FastAPI(
    title='Task list',
    description='Task-list project for the **Megadados** course',
    openapi_tags=tags_metadata,
)

app.include_router(task.router, prefix='/task', tags=['task'])
app.include_router(user.router, prefix='/user', tags=['user'])
