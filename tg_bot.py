from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
import pandas as pd

conn = 'postgresql://postgres:1712@localhost/metro'
#conn = 'postgresql://aleksandralekseev:@localhost/metro'



def tel_bot():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Клавиатура с ролями
    roles_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    roles_keyboard.add(KeyboardButton("Оператор"), KeyboardButton("Сотрудник"))

    # Клавиатура для выбора действия оператора
    operator_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    operator_keyboard.add(KeyboardButton("Список заявок"), KeyboardButton("Создать заявку на сопровождение"),
                          KeyboardButton("Написать специалисту"))

    # Клавиатура для выбора места встречи
    meeting_place_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    meeting_place_keyboard.add(KeyboardButton("У входных дверей"), KeyboardButton("У турникетов"),
                               KeyboardButton("В вестибюле"), KeyboardButton("На платформе, в центре зала"))

    # Клавиатура для ответа на вопрос о багаже
    baggage_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    baggage_keyboard.add(KeyboardButton("Да"), KeyboardButton("Нет"))



    # Обработка команды /start
    @dp.message_handler(commands=["start"])
    async def start(message: types.Message):
        await message.answer("Здравствуйте, Я телеграмм бот Центра мобильности Московского метрополитена.\n"
                             "Пожалуйста, выберите роль для авторизации.",
                             reply_markup=roles_keyboard)

    # Обработка выбора роли
    @dp.message_handler(text=["Оператор", "Сотрудник"])
    async def handle_role(message: types.Message):
        if message.text == "Оператор":
            await message.answer("Добро пожаловать! Вы авторизовались под ролью Оператора.\n"
                                 "Под этой ролью вы можете посмотреть список заявок, создать новую или связаться со специалистом.",
                                 reply_markup=operator_keyboard)
        else:
            # Логика для сотрудника
            await message.answer("Добро пожаловать, сотрудник! Что-то для вас пошло не так.")

    # Обработка выбора действия оператора
    @dp.message_handler(text=["Список заявок", "Создать заявку на сопровождение", "Написать специалисту"], state="*")
    async def handle_operator_action(message: types.Message):
        if message.text == "Список заявок":
            # Вывод списка заявок
            applications_text = ""
            try:
                df = pd.read_sql_table(table_name='request', con=conn)
                df.to_excel('request.xlsx')
                with open('request.xlsx', 'rb') as file:
                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=types.InputFile(file)
                    )

            except FileNotFoundError:
                print("Файл request.xlsx не найден. Создайте файл с данными заявок.")
                exit()

        elif message.text == "Создать заявку на сопровождение":
            await message.answer("Введите ФИО пассажира:")
            await dp.current_state().set_state("create_application_fio")
        elif message.text == "Написать специалисту":
            await dp.current_state().set_state("problem")
            await message.answer("Опишите ваш вопрос или проблему и специалист ответит вам.")


    @dp.message_handler(state="problem")
    async def handle_fio(message: types.Message):
        await message.answer("Спасибо")
        await dp.current_state().set_state(None)

    # Обработка ввода ФИО пассажира
    @dp.message_handler(state="create_application_fio")
    async def handle_fio(message: types.Message):
        fio = message.text
        await dp.current_state().update_data(fio=fio)
        await message.answer("Введите номер телефона пассажира:")
        await dp.current_state().set_state("create_application_phone")

    # Обработка ввода номера телефона
    @dp.message_handler(state="create_application_phone")
    async def handle_phone(message: types.Message):
        phone = message.text
        await dp.current_state().update_data(phone=phone)
        await message.answer("Введите дату поездки в формате день.месяц.год:")
        await dp.current_state().set_state("create_application_date")

    # Обработка ввода даты поездки
    @dp.message_handler(state="create_application_date")
    async def handle_date(message: types.Message):
        date = message.text
        await dp.current_state().update_data(date=date)
        await message.answer("Введите время поездки в формате ЧЧ:ММ:")
        await dp.current_state().set_state("create_application_time")

    # Обработка ввода времени поездки
    @dp.message_handler(state="create_application_time")
    async def handle_time(message: types.Message):
        time = message.text
        await dp.current_state().update_data(time=time)
        await message.answer("Введите станцию отправления:")
        await dp.current_state().set_state("create_application_departure_station")

    # Обработка ввода станции отправления
    @dp.message_handler(state="create_application_departure_station")
    async def handle_departure_station(message: types.Message):
        departure_station = message.text
        await dp.current_state().update_data(departure_station=departure_station)
        await message.answer("Введите станцию прибытия:")
        await dp.current_state().set_state("create_application_arrival_station")

    # Обработка ввода станции прибытия
    @dp.message_handler(state="create_application_arrival_station")
    async def handle_arrival_station(message: types.Message):
        arrival_station = message.text
        await dp.current_state().update_data(arrival_station=arrival_station)
        await message.answer("Введите кол-во необходимых сотрудников мужчин:")
        await dp.current_state().set_state("create_application_men_count")

    # Обработка ввода количества мужчин
    @dp.message_handler(state="create_application_men_count")
    async def handle_men_count(message: types.Message):
        men_count = message.text
        await dp.current_state().update_data(men_count=men_count)
        await message.answer("Введите кол-во необходимых сотрудников женщин:")
        await dp.current_state().set_state("create_application_women_count")

    # Обработка ввода количества женщин
    @dp.message_handler(state="create_application_women_count")
    async def handle_women_count(message: types.Message):
        women_count = message.text
        await dp.current_state().update_data(women_count=women_count)
        await message.answer("Выберите место встречи с инспектором службы на станции отправления:",
                             reply_markup=meeting_place_keyboard)
        await dp.current_state().set_state("create_application_meeting_place")

    # Обработка выбора места встречи
    @dp.message_handler(state="create_application_meeting_place")
    async def handle_meeting_place(message: types.Message):
        meeting_place = message.text
        await dp.current_state().update_data(meeting_place=meeting_place)
        await message.answer("Введите описание места встречи:")
        await dp.current_state().set_state("create_application_meeting_description")

    # Обработка ввода описания места встречи
    @dp.message_handler(state="create_application_meeting_description")
    async def handle_meeting_description(message: types.Message):
        meeting_description = message.text
        await dp.current_state().update_data(meeting_description=meeting_description)
        await message.answer("Введите категорию заявки:")
        await dp.current_state().set_state("create_application_category")

    # Обработка ввода категории заявки
    @dp.message_handler(state="create_application_category")
    async def handle_category(message: types.Message):
        category = message.text
        await dp.current_state().update_data(category=category)
        await message.answer("Укажите есть ли у вас багаж?", reply_markup=baggage_keyboard)
        await dp.current_state().set_state("create_application_baggage")

    # Обработка ответа на вопрос о багаже
    @dp.message_handler(state="create_application_baggage")
    async def handle_baggage(message: types.Message):
        baggage = message.text
        await dp.current_state().update_data(baggage=baggage)
        if baggage == "Да":
            await message.answer("Опишите багаж:")
            await dp.current_state().set_state("create_application_baggage_description")
        else:
            await message.answer("Укажите телеграмм для связи:")
            await dp.current_state().set_state("create_application_telegram")

    # Обработка ввода описания багажа
    @dp.message_handler(state="create_application_baggage_description")
    async def handle_baggage_description(message: types.Message):
        baggage_description = message.text
        await dp.current_state().update_data(baggage_description=baggage_description)
        await message.answer("Укажите телеграмм для связи:")
        await dp.current_state().set_state("create_application_telegram")

    # Обработка ввода телеграмма
    @dp.message_handler(state="create_application_telegram")
    async def handle_telegram(message: types.Message):
        telegram = message.text
        await dp.current_state().update_data(telegram=telegram)
        await message.answer("Введите комментарий:")
        await dp.current_state().set_state("create_application_comment")

    # Обработка ввода комментария
    @dp.message_handler(state="create_application_comment")
    async def handle_comment(message: types.Message):
        comment = message.text
        data = await dp.current_state().get_data()
        # Сохранение заявки в Excel
        # Загрузка данных из Excel
        try:
            df = pd.read_excel("applications.xlsx")
        except FileNotFoundError:
            print("Файл applications.xlsx не найден. Создайте файл с данными заявок.")
            exit()
        print(data)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel("applications.xlsx", index=False)
        await message.answer("Заявка успешно создана!")
        await dp.current_state().set_state(None)


    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    tel_bot()