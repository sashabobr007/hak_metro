from sqlalchemy import Integer, String, Float, Boolean, ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.schema import Column
from database import Base
from sqlalchemy.orm import relationship

class Passengers(Base):
    __tablename__ = "passengers"
    id_pas = Column(String, primary_key=True, index=True)
    fio = Column(String)
    cat_pas = Column(String)
    phone = Column(String)
    telegram = Column(String)
    request = relationship("Request", back_populates="passenger")


class TimePerehod(Base):
    __tablename__ = "time_perehod"
    id_st1 = Column(String, primary_key=True, index=True)
    id_st2 = Column(String, primary_key=True, index=True)
    time_perehod = Column(String)



class TimeStations(Base):
    __tablename__ = "time_stations"
    id_st1 = Column(String, primary_key=True, index=True)
    id_st2 = Column(String)
    time_way = Column(String)



class Request(Base):
    __tablename__ = "request"
    id_bid = Column(String, primary_key=True, index=True)
    id_pas = Column(String, ForeignKey("passengers.id_pas"))
    datetime = Column(String)
    time3 = Column(String)
    time4 = Column(String)
    cat_pas = Column(String)
    status = Column(String)
    tpz = Column(String)
    insp_sex_m = Column(String)
    insp_sex_f = Column(String)
    time_over = Column(String)
    id_st1 = Column(String)
    id_st2 = Column(String)
    otmena_datetime = Column(String)
    neyavka_datetime = Column(String)
    time_perenos = Column(String)
    phone = Column(String)
    telegram = Column(String)
    feedback = Column(String)
    place: int = Column(Integer)
    comment: int = Column(Integer)
    obed: int = Column(Integer)
    passenger = relationship("Passengers", back_populates="request")
    req = relationship("Move", back_populates="mov")

class Workers(Base):
    __tablename__ = "workers"
    id_worker = Column(String, ForeignKey("workers_info.id_worker"), primary_key=True, index=True)
    date = Column(String)
    time_work = Column(String)
    uchastok = Column(String)
    smena = Column(String)
    work_info = relationship("WorkersInfo", back_populates="work")

class Emergency(Base):
    __tablename__ = 'emergency'
    id_emergency = Column(Integer, primary_key=True)
    id_worker = Column(String, primary_key=True)
    fio_worker = Column(String, nullable=False)
    text_emergency = Column(String, nullable=False)
    date_emergency = Column(String, nullable=False)


class Obed(Base):
    __tablename__ = "obed1"

    id_worker = Column(String, primary_key=True)
    start_time = Column(String)
    end_time = Column(String)




class Move(Base):
    __tablename__ = "move"
    id_bid = Column(String , ForeignKey("request.id_bid"), primary_key=True)
    id_worker = Column(String, primary_key=True)
    st_from = Column(String)
    start_time = Column(String)
    on_place_time = Column(String)
    wait_minutes = Column(Integer)
    time3 = Column(String)
    name_station1 = Column(String)
    name_station2 = Column(String)
    path_minutes = Column(Integer)
    time4 = Column(String)
    minutes_to_st1 = Column(Integer)
    mov = relationship("Request", back_populates="req")


class NameStations(Base):
    __tablename__ = "name_stations"
    id_station = Column(String, primary_key=True, index=True)
    name_station = Column(String)
    name_line = Column(String)
    id_line = Column(String)
    coordinate1 = Column(String)
    coordinate2 = Column(String)

class WorkersInfo(Base):
    __tablename__ = "workers_info"
    id_worker = Column(String, primary_key=True, index=True)
    fio = Column(String)
    rank = Column(String)
    sex = Column(String)
    mobile_phone = Column(String)
    phone_job = Column(String)
    tabel_number = Column(String)
    health = Column(String)
    work = relationship("Workers", back_populates="work_info")







