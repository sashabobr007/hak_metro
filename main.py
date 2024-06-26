from fastapi import FastAPI, Depends, File, UploadFile, Response, HTTPException
import uvicorn
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Union, Any
import random
import os
from schemas import *
from database import get_db
from models import *
from algos import algos
from to_bd import *
from db import Database
from fastapi.security import OAuth2PasswordBearer
#from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import pandas as pd

def get_worker_info(worker_id, time: str):
    timesheet = pd.read_csv('ts.csv', sep=',', index_col=[0,1], parse_dates=['start_time', 'on_place_time', 'start_request_time', 'end_time'])
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    info = timesheet.xs(worker_id, level='worker_id')
    return {'total_tasks': len(info),
            'total_completed_tasks': sum(info.end_time <= time),
            'today_tasks': sum(info.end_time.dt.date == datetime),
            'time_in_way': info.minutes_to_st1.mean(),
            'time_in_tasks': info.path_minutes.mean(),
            'time_free': info.wait_minutes.mean()}


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Алгоритм для шифрования JWT
ALGORITHM = "HS256"

# Время жизни токена в секундах
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Схема для данных, которые будут храниться в JWT
class User(BaseModel):
    username: str
    email: str
# Секретный ключ для JWT
SECRET_KEY = "secret_key"
# Функция для создания токена JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для декодирования JWT
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Неверный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Схема для авторизации с использованием JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функция для получения данных пользователя из JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Неверный токен авторизации")
    return User(username=username)

# Роут для получения токена авторизации
@app.post("/token")
async def get_token(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Роут, защищенный JWT
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Привет, {current_user.username}!", "user_data": current_user}


@app.delete("/algos_dont_tap/")
async def get_items():
    algos()
    to_bd_move()
    to_bd_obed()
    return {'m' :'s'}

@app.get("/stations/")
async def get_items(db: Session = Depends(get_db)):
    return db.query(NameStations).all()


@app.get("/pas_info_surnames/")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Passengers).all()

@app.get("/pas_info/")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Passengers).all()

@app.get("/emergency_case_get/")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Emergency).all()

@app.post("/lunch_time/")
async def get_items(id_worker : str, db: Session = Depends(get_db)):
    return db.query(Obed).filter(Obed.id_worker == id_worker).all()


@app.post("/emergency_case_post/")
async def create_emergency(emergency: EmergencyModel, db: Session = Depends(get_db)):
    """
    Создает запись об аварийном случае.
    """
    try:
        new_emergency = Emergency(**emergency.dict())
        db.add(new_emergency)
        db.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "Запись об аварийном случае успешно создана."}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при создании записи: {e}"
        )


@app.get("/list_tasks_employee/")
async def get_items(id_worker : str, db: Session = Depends(get_db)):
    return db.query(Move).filter(Move.id_worker == id_worker).all()


@app.get("/list_tasks_archive/")
async def get_items(id_worker : str, db: Session = Depends(get_db)):
    return db.query(Move).filter(Move.id_worker == id_worker).all()


@app.get("/all/")
async def get_items():
    db = Database()
    res = db.get_all()
    return res


@app.get("/request/")
async def get_items(id_bid : str):
    db = Database()
    res = db.get_req(id_bid)
    return res


@app.get("/map_employee/")
async def get_items(id_worker : str):
    db = Database()
    res = db.get_work_stations(id_worker)
    return res



@app.get("/profile_worker/")
async def get_items(id_worker,  db: Session = Depends(get_db)):
    requests = db.query(WorkersInfo, Workers).join(Workers).filter(WorkersInfo.id_worker == id_worker).all()
    response = {}
    for info, worker in requests:
        response["fio_worker"] = info.fio
        response["rank"] = info.rank
        response["sex"] = info.sex
        response["mobile_phone"] = info.mobile_phone
        response["phone_job"] = info.phone_job
        response["tabel_number"] = info.tabel_number
        response["health"] = info.health
        response["date"] = worker.date
        response["time_work"] = worker.time_work
        response["uchastok"] = worker.uchastok
        response["smena"] = worker.smena

    return response

@app.put("/change_status/")
async def change_status (id_bid: str, status : str, db: Session = Depends(get_db)):
    try:
        requests = db.query(Request).filter(Request.id_bid == id_bid).first()
        if requests:
            requests.status = status
            db.commit()
            algos()
            to_bd_move()
            to_bd_obed()
            return JSONResponse(
                status_code=200,
                content={"message": "Запись успешно обновлена."}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Запись  с id {id_bid} не найдена."
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при обновлении : {e}"
        )

@app.put("/Late_worker/")
async def change_status (id_bid: str, time_perenos : str, db: Session = Depends(get_db)):
    try:
        requests = db.query(Request).filter(Request.id_bid == id_bid).first()
        if requests:
            requests.time_perenos = time_perenos
            db.commit()
            db.close()
            algos()
            to_bd_move()
            to_bd_obed()
            return JSONResponse(
                status_code=200,
                content={"message": "Запись успешно обновлена."}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Запись  с id {id_bid} не найдена."
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при обновлении : {e}"
        )


@app.post("/add_worker")
async def add_request(request_data: WorkersInfoModel, db: Session = Depends(get_db)):

    try:
        new_w = WorkersInfo(**request_data.dict())
        db.add(new_w)
        db.commit()
        return JSONResponse(content={"message": "успешно добавлена."})
    except IntegrityError:
        db.rollback()
        return JSONResponse(content={"message": "с таким id_worker уже существует."}, status_code=409)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении: {e}")


@app.post("/add_request")
async def add_request(request_data: RequestData, db: Session = Depends(get_db)):
    """
    Вставка новой заявки в таблицу "request".
    """
    try:
        new_request = Request(**request_data.dict())
        db.add(new_request)
        db.commit()
        algos()
        to_bd_move()
        to_bd_obed()
        return JSONResponse(content={"message": "Заявка успешно добавлена."})
    except IntegrityError:
        db.rollback()
        return JSONResponse(content={"message": "Заявка с таким id_bid уже существует."}, status_code=409)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении заявки: {e}")


@app.post("/add_passenger")
async def add_request(fio : str, cat_pas : str, phone : str, telegram : str, db: Session = Depends(get_db)):
    """
    Вставка новой заявки в таблицу "request".
    """
    try:
        new_pas = Passengers(id_pas=str(random.randint(1, 1200)), fio=fio, cat_pas=cat_pas, phone=phone,
                             telegram=telegram)
        db.add(new_pas)
        db.commit()
        return JSONResponse(content={"message": "Пассажир успешно добавлен."})
    except IntegrityError:
        db.rollback()
        return JSONResponse(content={"message": "Пассажир с таким id_pas уже существует."}, status_code=409)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении: {e}")


@app.delete("/del_task/")
async def delete_item(id_bid: str, db: Session = Depends(get_db)):
    db_item = db.query(Request).filter(Request.id_bid == id_bid).first()
    if db_item is None:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}


@app.get("/get_worker_info/")
async def root(id_worker : int, date : str):
    return get_worker_info(id_worker, date)




@app.get("/")
async def root():
    return {"hello": "success"}

@app.delete("/")
async def kill():
    os.kill(os.getpid(), 9)
    return {"message": "error"}

if __name__ == '__main__':
    uvicorn.run(app, port=8000)