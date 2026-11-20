from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import service_photo as photo_crud
from app.models.user import User
from app.schemas.service_photo import (
    ServicePhotoResponse,
    ServicePhotoUpdate,
)
from app.services.service_photo_storage import resolve_photo_path
from database import get_db


router = APIRouter(
    prefix=(
        "/drones/{drone_id}"
        "/service-sessions/{session_id}"
        "/photos"
    ),
    tags=["Service photos"],
)


@router.post(
    "",
    response_model=ServicePhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_photo(
    drone_id: int,
    session_id: int,
    file: UploadFile = File(...),
    description: str | None = Form(
        default=None,
        max_length=255,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return photo_crud.create_photo(
        db,
        drone_id,
        session_id,
        file,
        description,
        current_user,
    )


@router.get(
    "",
    response_model=list[ServicePhotoResponse],
)
def list_photos(
    drone_id: int,
    session_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return photo_crud.get_photos(
        db, drone_id, session_id, current_user, offset, limit
    )


@router.get(
    "/{photo_id}",
    response_model=ServicePhotoResponse,
)
def read_photo(
    drone_id: int,
    session_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return photo_crud.get_photo(
        db, drone_id, session_id, photo_id, current_user
    )


@router.get(
    "/{photo_id}/file",
    response_class=FileResponse,
)
def read_photo_file(
    drone_id: int,
    session_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = photo_crud.get_photo(
        db, drone_id, session_id, photo_id, current_user
    )

    path = resolve_photo_path(photo.file_path)

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Файл фотографії відсутній на сервері",
        )

    media_type = (
        "image/png"
        if path.suffix.lower() == ".png"
        else "image/jpeg"
    )

    return FileResponse(
        path=path,
        media_type=media_type,
        filename=path.name,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.put(
    "/{photo_id}",
    response_model=ServicePhotoResponse,
)
def update_photo(
    drone_id: int,
    session_id: int,
    photo_id: int,
    data: ServicePhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return photo_crud.update_photo(
        db, drone_id, session_id, photo_id, data, current_user
    )


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_photo(
    drone_id: int,
    session_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo_crud.delete_photo(
        db, drone_id, session_id, photo_id, current_user
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )