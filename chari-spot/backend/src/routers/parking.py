from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import parking as schemas
from app.auth import get_current_user
from crud import parking as crud
from app.database import get_db
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/parkings",
    tags=["parking"],
    dependencies=[Depends(get_current_user)],   # ← apply to all routes here
)

# 駐輪場の新規登録
@router.post("/parkings/register", response_model=schemas.ParkingResponse)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    return crud.create_parking(db, parking)

# 駐輪場一覧を取得（UTF-8 明示）
@router.get("/parkings")
def get_all_parkings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parkings = crud.get_parkings(db, skip=skip, limit=limit)
    return JSONResponse(
        content=jsonable_encoder(parkings),
        media_type="application/json; charset=utf-8"
    )

# 駐輪場情報の更新
@router.put("/parkings/update", response_model=schemas.ParkingResponse)
def update_parking(slot: schemas.ParkingUpdate, db: Session = Depends(get_db)):
    return crud.update_slot(db, slot)

# 駐輪場の削除
@router.delete("/parkings/delete/{id}")
def delete_parking(id: int, db: Session = Depends(get_db)):
    return crud.delete_slot(db, id)

# 駐輪場の詳細取得
@router.get("/parkings/{parking_id}", response_model=schemas.ParkingResponse)
def get_parking_detail(parking_id: int, db: Session = Depends(get_db)):
    parking = crud.get_parking_by_id(db, parking_id)
    if parking is None:
        raise HTTPException(status_code=404, detail="駐輪場が見つかりません")
    return parking