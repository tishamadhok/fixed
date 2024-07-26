from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
import logging

from app.schema import QRCodeRequest, QRCodeResponse
from app.services.qr_service import generate_qr_code, list_qr_codes, delete_qr_code
from app.utils.common import decode_filename_to_url, encode_url_to_filename, generate_links
from app.config import QR_DIRECTORY, SERVER_BASE_URL, FILL_COLOR, BACK_COLOR, SERVER_DOWNLOAD_FOLDER

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/qr-codes/", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED, tags=["QR Codes"])
async def create_qr_code(request: QRCodeRequest, token: str = Depends(oauth2_scheme)):
    logging.info(f"Creating QR code for URL: {request.url}")
    
    encoded_url = encode_url_to_filename(request.url)
    qr_filename = f"{encoded_url}.png"
    qr_code_full_path = QR_DIRECTORY / qr_filename

    qr_code_download_url = f"{SERVER_BASE_URL}/{SERVER_DOWNLOAD_FOLDER}/{qr_filename}"
    
    links = generate_links("create", qr_filename, SERVER_BASE_URL, qr_code_download_url)

    if qr_code_full_path.exists():
        logging.info("QR code already exists.")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "QR code already exists.", "links": links}
        )

    generate_qr_code(request.url, qr_code_full_path, request.fill_color, request.back_color, request.size)
    return QRCodeResponse(message="QR code created successfully.", qr_code_url=qr_code_download_url, links=links)
