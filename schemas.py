from pydantic import BaseModel, Field

# Pydantic модель для данных
class EmergencyModel(BaseModel):
    id_emergency: int = Field(..., description="Идентификатор аварийного случая")
    id_worker: str = Field(..., description="Идентификатор работника")
    fio_worker: str = Field(..., description="ФИО работника")
    text_emergency: str = Field(..., description="Текст аварийного случая")
    date_emergency: str = Field(..., description="Дата аварийного случая")


class WorkersInfoModel(BaseModel):
    id_worker: str = Field(..., description="Идентификатор работника")
    fio: str = Field(..., description="ФИО работника")
    rank: str = Field(..., description="Должность")
    sex: str = Field(..., description="Пол")
    mobile_phone: str = Field(..., description="Мобильный телефон")
    phone_job: str = Field(..., description="Рабочий телефон")
    tabel_number: str = Field(..., description="Табельный номер")
    health: str = Field(..., description="Состояние здоровья")

class RequestData(BaseModel):
    id_bid: str = Field(..., description="Идентификатор заявки")
    id_pas: str = Field(None, description="Идентификатор пассажира")
    datetime: str = Field(..., description="Дата и время заявки в формате YYYY-MM-DD HH:MM:SS")
    time3: str = Field(..., description="Время отправления в формате HH:MM")
    time4: str = Field(..., description="Время прибытия в формате HH:MM")
    cat_pas: str = Field(..., description="Категория пассажира")
    status: str = Field(..., description="Статус заявки")
    tpz: str = Field(..., description="Тип транспортного средства")
    insp_sex_m: str = Field(..., description="Количество мужчин-инспекторов")
    insp_sex_f: str = Field(..., description="Количество женщин-инспекторов")
    time_over: str = Field(..., description="Время в пути")
    id_st1: str = Field(..., description="Идентификатор начальной станции")
    id_st2: str = Field(..., description="Идентификатор конечной станции")
    otmena_datetime: str = Field(None, description="Дата и время отмены (если отменена)")
    neyavka_datetime: str = Field(None, description="Дата и время неявки (если неявка)")
    time_perenos: str = Field(None, description="Время переноса (если перенесена)")
    phone: str = Field(..., description="Номер телефона")
    telegram: str = Field(..., description="Телеграм-аккаунт")
    feedback: str = Field(None, description="Отзыв")
    place: int = Field(..., description="Место встречи")
    comment: int = Field(..., description="Комментарий")
    obed: int = Field(..., description="Обед")

