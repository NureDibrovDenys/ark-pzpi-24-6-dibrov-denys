from io import BytesIO
from pathlib import Path
from uuid import uuid4
import warnings

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError



PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = PROJECT_ROOT / "uploads"
PHOTO_DIR = UPLOAD_ROOT / "service_photos"

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000

FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
}


def resolve_photo_path(relative_path: str) -> Path:
    path = (UPLOAD_ROOT / relative_path).resolve()
    allowed_directory = PHOTO_DIR.resolve()

    if not path.is_relative_to(allowed_directory):
        raise HTTPException(
            status_code=500,
            detail="Некоректний шлях збереженої фотографії",
        )

    return path


def save_photo_file(upload: UploadFile) -> str:
    content = upload.file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=422,
            detail="Файл порожній",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Максимальний розмір фотографії — 10 МіБ",
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            with Image.open(BytesIO(content)) as image:
                image_format = image.format

                if image_format not in FORMAT_EXTENSIONS:
                    raise HTTPException(
                        status_code=415,
                        detail="Дозволені лише JPEG та PNG",
                    )

                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise HTTPException(
                        status_code=413,
                        detail="Максимальний розмір зображення — 25 мегапікселів",
                    )

                image.verify()

            # Після verify відкриваємо повторно для декодування.
            with Image.open(BytesIO(content)) as image:
                image.load()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombWarning,
        Image.DecompressionBombError,
    ):
        raise HTTPException(
            status_code=422,
            detail="Файл не є коректним зображенням",
        ) from None

    extension = FORMAT_EXTENSIONS[image_format]
    filename = f"{uuid4().hex}{extension}"

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    path = PHOTO_DIR / filename

    try:
        with path.open("xb") as destination:
            destination.write(content)
    except Exception:
        path.unlink(missing_ok=True)
        raise

    return f"service_photos/{filename}"