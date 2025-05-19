from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import parking as schemas
from app.auth import get_current_user
from crud import parking as crud
from app.database import get_db
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models import user as models


router = APIRouter(
    tags=["parking"],
    prefix="/parking",
    dependencies=[Depends(get_current_user)],
)


# 駐輪場の新規登録
@router.post("/register", response_model=schemas.ParkingResponse)
def create_parking(
    parking: schemas.ParkingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.create_parking(db, parking, user.id)


# 駐輪場一覧を取得（UTF-8 明示）
@router.get("/all", response_model=list[schemas.ParkingResponse])
def get_all_parkings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parkings = crud.get_parkings(db, skip=skip, limit=limit)
    return JSONResponse(
        content=jsonable_encoder(parkings),
        media_type="application/json; charset=utf-8"
    )


# 駐輪場の詳細取得（owned）
@router.get("/owned", response_model=list[schemas.ParkingResponse])
def get_parking_by_owner(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    parkings = crud.get_parking_by_owner(db, user.id)
    '''if len(parkings) == 0:
        raise HTTPException(status_code=404, detail="駐輪場が見つかりません")'''
    
    response_data = []
    for parking in parkings:
        response_data.append(schemas.ParkingResponse.model_validate(parking))
    return response_data


# 駐輪場の詳細取得
@router.get("/{parking_id}", response_model=schemas.ParkingResponse)
def get_parking_detail(parking_id: int, db: Session = Depends(get_db)):
    parking = crud.get_parking(db, parking_id)
    if parking is None:
        raise HTTPException(status_code=404, detail="駐輪場が見つかりません")
    return parking


# 駐輪場情報の更新
@router.put("/update", response_model=schemas.ParkingResponse)
def update_parking(
    slot: schemas.ParkingUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    existing = crud.get_parking(db, slot.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Slot not found.")
    if existing.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this parking.")
    return crud.update_slot(db, slot)



# 駐輪場の削除
@router.delete("/delete/{id}")
def delete_parking(
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    parking = crud.get_parking(db, id)
    if not parking:
        raise HTTPException(status_code=404, detail="Slot not found.")
    if parking.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this parking.")
    
    flag = crud.delete_slot(db, id)
    return JSONResponse(
        content={"message": "Slot deleted successfully."},
        media_type="application/json; charset=utf-8"
    )
