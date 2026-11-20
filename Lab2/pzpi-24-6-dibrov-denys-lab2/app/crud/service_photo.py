import logging
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.service_session import get_service_session
from app.models.service_photo import ServicePhoto
from app.models.user import User
from app.schemas.service_photo import ServicePhotoUpdate
from app.services.service_photo_storage import (
    resolve_photo_path,
    save_photo_file,
)


logger = logging.getLogger(__name__)


def get_photo(
    db: Session,
    drone_id: int,
    session_id: int,
    photo_id: int,
    current_user: User,
    for_update: bool = False,
) -> ServicePhoto:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    statement = select(ServicePhoto).where(
        ServicePhoto.id == photo_id,
        ServicePhoto.service_session_id == session_id,
    )

    if for_update:
        statement = statement.with_for_update()

    photo = db.scalar(statement)

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Фото в цьому сервісному сеансі не знайдено",
        )

    return photo


def get_photos(
    db: Session,
    drone_id: int,
    session_id: int,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
) -> list[ServicePhoto]:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    statement = (
        select(ServicePhoto)
        .where(ServicePhoto.service_session_id == session_id)
        .order_by(ServicePhoto.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_photo(
    db: Session,
    drone_id: int,
    session_id: int,
    upload: UploadFile,
    description: str | None,
    current_user: User,
) -> ServicePhoto:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    relative_path = save_photo_file(upload)

    photo = ServicePhoto(
        service_session_id=session_id,
        file_path=relative_path,
        description=description,
    )

    try:
        db.add(photo)
        db.commit()
    except Exception:
        db.rollback()

        try:
            resolve_photo_path(relative_path).unlink(
                missing_ok=True
            )
        except OSError:
            logger.exception(
                "Не вдалося прибрати файл після помилки збереження"
            )

        raise

    db.refresh(photo)
    return photo


def update_photo(
    db: Session,
    drone_id: int,
    session_id: int,
    photo_id: int,
    data: ServicePhotoUpdate,
    current_user: User,
) -> ServicePhoto:
    photo = get_photo(
        db,
        drone_id,
        session_id,
        photo_id,
        current_user,
        for_update=True,
    )

    photo.description = data.description

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(photo)
    return photo


def delete_photo(
    db: Session,
    drone_id: int,
    session_id: int,
    photo_id: int,
    current_user: User,
) -> None:
    photo = get_photo(
        db,
        drone_id,
        session_id,
        photo_id,
        current_user,
        for_update=True,
    )

    path = resolve_photo_path(photo.file_path)
    temporary_path = None

    try:
        # Тимчасово переміщуємо файл перед видаленням запису.
        if path.is_file():
            temporary_path = path.with_name(
                f".{uuid4().hex}.deleted"
            )
            path.rename(temporary_path)

        db.delete(photo)
        db.commit()

    except Exception:
        db.rollback()

        if temporary_path is not None:
            try:
                temporary_path.rename(path)
            except OSError:
                logger.exception(
                    "Не вдалося відновити файл після відкату"
                )

        raise

    # Запис успішно видалено; прибираємо тимчасовий файл.
    if temporary_path is not None:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "Не вдалося прибрати тимчасовий файл видаленого фото"
            )