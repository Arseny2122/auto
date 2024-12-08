import asyncpg
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from src.states import RegisterAuto, SendMessageAdmin
from config import ADMIN_ID
from src.keyboards import (
    start_kb_if_user_exist,
    start_kb_if_user_not_exist,
    inline_start,
)

router = Router(name=__name__)


@router.message(CommandStart())
async def start(message: Message, db_pool: asyncpg.Pool):
    async with db_pool.acquire() as conn:
        tg_id = message.from_user.id
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", tg_id)
        start_message = "Привет!\nЭтот бот принадлежит сообществу AudioBanda.\n\
Данный бот предоставляет перечень услуг которые ты можешь совершить в их автосервисе.\n\
Для продолжения работы нужно заполнить форму в которой вы укажите все основные данные о вашем автомобиле."
        if user["car_id"] is None:
            await message.answer(
                start_message, reply_markup=await start_kb_if_user_not_exist()
            )
        else:
            start_message_if_user_exist = (
                f"Привет {message.from_user.full_name}, рады снова тебя увидеть здесь!"
            )
            await message.answer(
                start_message_if_user_exist, reply_markup=await start_kb_if_user_exist()
            )


@router.message(F.text == "Заполнить данные")
async def information(message: Message, state: FSMContext):
    await message.reply("Введите брэнд автомобиля:")
    await state.set_state(RegisterAuto.BRAND)


@router.message(RegisterAuto.BRAND)
async def information_process_one(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.reply("Введите модель автомобиля:")
    await state.set_state(RegisterAuto.MODEL)


@router.message(RegisterAuto.MODEL)
async def information_process_two(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.reply("Введите год выпуска автомобиля:")
    await state.set_state(RegisterAuto.YEAR)


@router.message(RegisterAuto.YEAR)
async def information_process_three(message: Message, state: FSMContext):
    await state.update_data(year_released=int(message.text))
    await message.reply("Введите цвет автомобиля:")
    await state.set_state(RegisterAuto.COLOR)


@router.message(RegisterAuto.COLOR)
async def information_process_four(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.reply("Введите госномер автомобиля:")
    await state.set_state(RegisterAuto.LICENSE_PLATE)


@router.message(RegisterAuto.LICENSE_PLATE)
async def information_process_five(
    message: Message, state: FSMContext, db_pool: asyncpg.Pool
):
    async with db_pool.acquire() as conn:
        data = await state.get_data()
        tg_id = message.from_user.id
        license_plate = message.text

        car_id = await conn.fetchval(
            """
            INSERT INTO cars (brand, model, year_released, color, license_plate)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING car_id
            """,
            data["brand"],
            data["model"],
            data["year_released"],
            data["color"],
            license_plate,
        )

        await conn.execute(
            """
            UPDATE users
            SET car_id = $1
            WHERE user_id = $2
            """,
            car_id,
            tg_id,
        )

    await message.reply(
        "Ваши данные успешно сохранены! Теперь вы можете пользоваться ботом.",
        reply_markup=await start_kb_if_user_exist(),
    )
    await state.clear()


@router.message(F.text == "Отзыв")
async def review(message: Message, state: FSMContext):
    await message.answer("Напишите свой отзыв и он отправиться администратору!")
    await state.set_state(SendMessageAdmin.admin_message)


@router.message(SendMessageAdmin.admin_message)
async def send_message(message: Message, state: FSMContext):
    await message.bot.send_message(
        chat_id=ADMIN_ID, text=f"Отзыв от {message.from_user.username}: {message.text}"
    )
    await message.answer("Сообщение успешно отправлено администратору!")
    await state.clear()


@router.message(F.text == "Связаться")
async def contact(message: Message):
    contact_message = "Если вы столкнулись с багами бота или не корректной работой, то напишите: @argus11\n\
Администратор AudioBanda: @argus11"
    await message.answer(contact_message)


@router.message(F.text == "Записаться на услугу")
async def sign_up_for_the_service(message: Message):
    await message.answer(
        "Выберите услугу из списка ниже:", reply_markup=await inline_start()
    )


@router.message(
    F.text.in_(["Мойка", "Тонировка", "Хим-чистка", "Установка доп. оборудования"])
)
async def select_service(message: Message, db_pool: asyncpg.Pool):
    user_id = message.from_user.id
    async with db_pool.acquire() as conn:
        user_data = await conn.fetchrow(
            "SELECT cars.brand, cars.model, cars.year_released, cars.color, cars.license_plate "
            "FROM users LEFT JOIN cars ON users.car_id = cars.car_id WHERE users.user_id = $1",
            user_id,
        )
        if not user_data:
            user_data_text = "Информация об автомобиле отсутствует."
            await message.answer(user_data_text)
        else:
            await message.answer(
                "Ваша заявка успешно обработана и была отправлена администратору!"
            )
            marka = str(user_data["brand"])
            model = str(user_data["model"])
            year = str(user_data["year_released"])
            color = str(user_data["color"])
            gos_nomer = str(user_data["license_plate"])
            admin_message = (
                f"Клиент выбрал услугу: {message.text}\n"
                f"Пользователь: @{message.from_user.username}\n"
                f"Марка: {marka}\n"
                f"Модель: {model}\n"
                f"Год выпуска: {year}\n"
                f"Цвет: {color}\n"
                f"Госномер: {gos_nomer}"
            )

            await message.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
