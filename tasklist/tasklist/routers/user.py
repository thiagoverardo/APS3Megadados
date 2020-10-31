# pylint: disable=missing-module-docstring, missing-function-docstring, invalid-name
import uuid

from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from ..database import DBSession, get_db
from ..models import User

router = APIRouter()


@router.get(
    '',
    summary='Reads user list',
    description='Reads the whole user list.',
    response_model=Dict[uuid.UUID, User],
)
async def read_user(db: DBSession = Depends(get_db)):
    return db.read_user()


@router.post(
    '',
    summary='Creates a new user',
    description='Creates a new user and returns its UUID.',
    response_model=uuid.UUID,
)
async def create_user(item: User, db: DBSession = Depends(get_db)):
    return db.create_user(item)


@router.get(
    '/{uuid_}',
    summary='Reads user',
    description='Reads user from UUID.',
    response_model=User,
)
async def read_user(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        return db.read_user(uuid_)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='user not found',
        ) from exception


@router.put(
    '/{uuid_}',
    summary='Replaces an user',
    description='Replaces an user identified by its UUID.',
)
async def replace_user(
        uuid_: uuid.UUID,
        item: User,
        db: DBSession = Depends(get_db),
):
    try:
        db.replace_user(uuid_, item)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='user not found',
        ) from exception


@router.patch(
    '/{uuid_}',
    summary='Alters user',
    description='Alters a user identified by its UUID',
)
async def alter_user(
        uuid_: uuid.UUID,
        item: User,
        db: DBSession = Depends(get_db),
):
    try:
        old_item = db.read_user(uuid_)
        update_data = item.dict(exclude_unset=True)
        new_item = old_item.copy(update=update_data)
        db.replace_user(uuid_, new_item)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='user not found',
        ) from exception


@router.delete(
    '/{uuid_}',
    summary='Deletes user',
    description='Deletes a user identified by its UUID',
)
async def remove_user(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        db.remove_user(uuid_)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='user not found',
        ) from exception


@router.delete(
    '',
    summary='Deletes all users, use with caution',
    description='Deletes all users, use with caution',
)
async def remove_all_users(db: DBSession = Depends(get_db)):
    db.remove_all_users()
