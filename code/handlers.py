from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto, InputFile, BufferedInputFile
from aiogram.types.callback_query import CallbackQuery

from aiogram.fsm.context import FSMContext

import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import UserDataExtractor

import ollama
from ollama import AsyncClient

import datetime
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar, get_user_locale
from aiogram.filters.callback_data import CallbackData

from states import Gen
import db
import kb
import text

router = Router()
engine = create_engine('sqlite:///flowtaskcollab.db')
Session = sessionmaker(bind=engine)

# Начало по команде /start
@router.message(Command("start"))
async def subscribe(message: types.Message):
    if len(message.from_user.username) > 1:
        db.user_init(_id=message.from_user.id, username=message.from_user.username)
    else:
        db.user_init(_id=message.from_user.id, username=None)
    await message.answer(text.greet.format(name=message.from_user.full_name), reply_markup=kb.main_menu)



# Возвращение в главное меню
@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
async def menu(msg: Message, state: FSMContext):
    await state.clear() 
    await msg.answer(text.menu.format(name=msg.from_user.full_name), 
                     reply_markup=kb.main_menu)


@router.callback_query(F.data == "main_menu")
async def main_menu(clbck: CallbackQuery, state: FSMContext):
    await state.clear() 
    await clbck.message.edit_text(text.menu.format(name=clbck.from_user.full_name), 
                                  reply_markup=kb.main_menu)
    
# Меню "Мой профиль"
@router.callback_query(F.data == "my_profile")
async def input_weight(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(
    text=str(db.get_user_data(clbck.from_user.id)),
    reply_markup=kb.my_profile)
    
# Нажатие кнопки "Редактировать профиль"
@router.callback_query(F.data == "edit_profile")
async def edit_profile(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.answer("Введите ваше имя:")    
    await clbck.message.delete_reply_markup()
    await state.set_state(Gen.edit_profile_name)

# Получение имени от пользователя через машину состояния 
@router.message(Gen.edit_profile_name)
async def input_edit_profile_name(message: Message, state: FSMContext):
    await state.update_data(profile_name=message.text)
    await message.answer(text="Введите вашу фамилию:")
    await state.set_state(Gen.edit_profile_surname)

# Получение фамилии от пользователя через машину состояния
@router.message(Gen.edit_profile_surname)
async def input_edit_profile_name(message: Message, state: FSMContext):
    await state.update_data(profile_surname=message.text) 
    
    user_data = await state.get_data()

    name = user_data['profile_name']
    surname = user_data['profile_surname']
    db.user_init(message.from_user.id, name=name, surname=surname)
    await message.answer(text=db.get_user_data(message.from_user.id), reply_markup=kb.main_menu)
    await state.clear()  

# Меню "Проекты"
@router.callback_query(F.data == "projects")
async def projects(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(
    text="Вот что вам доступно",
    reply_markup=kb.projects)

# Нажатие кнопки "Создание проекта"
@router.callback_query(F.data == "create_project")
async def create_project(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.delete()
    await clbck.message.answer("Введите название проекта:")
    await state.set_state(Gen.edit_project_name)

# project_name 
@router.message(Gen.edit_project_name)
async def input_edit_project_name(message: Message, state: FSMContext):
    await state.update_data(project_name=message.text)
    await message.answer("Введите описание проекта:")
    await state.set_state(Gen.edit_project_description)  

# project_description
@router.message(Gen.edit_project_description)
async def input_edit_project_description(message: Message, state: FSMContext):
    await state.update_data(project_description=message.text)  
    
    user_data = await state.get_data()

    name = user_data['project_name']
    description = user_data['project_description']
    text = db.create_project(creator_id=message.from_user.id, name=name, description=description)

    await message.answer(text=text[0]+f"\nКод доступа к проекту:\n<pre>{text[1]}</pre>",
                         reply_markup=kb.main_menu)
    await state.clear()  
    
# Вступить в проект 
@router.callback_query(F.data == "find_project")
async def find_project(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.delete()
    await clbck.message.answer("Введите ключ проекта:")
    await state.set_state(Gen.find_project)
    
@router.message(Gen.find_project)
async def input_key_project(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        prompt = msg.text
        await msg.answer(db.join_project(user_id=msg.from_user.id, key=prompt), reply_markup=kb.projects)
        await state.clear()
    else:
        await msg.answer(text.error_input)
        
# Меню "Мои проекты"
@router.callback_query(F.data == "my_projects")
async def my_projects(clbck: CallbackQuery, state: FSMContext):
    type = "project"
    data = db.get_projects_name(user_id=clbck.from_user.id)
    text_butt = data[0]
    calldata_butt = data[1]
    if len(text_butt) < 1:
        if clbck.message.text != "Вы не состоите ни в одном из проектов":
            await clbck.message.edit_text("Вы не состоите ни в одном из проектов", 
                                        reply_markup=clbck.message.reply_markup)
        else:
            await clbck.answer(text="Вступите в проект или создайте свой!")
    else:
        keyboard=kb.build_keyboard(text_butt=text_butt, calldata_butt=calldata_butt, type=type, width=2)
        await state.set_state(Gen.choose_project)
        await clbck.message.edit_text("Доступные проекты", reply_markup=keyboard)

@router.callback_query(Gen.choose_project)
async def callback_data_project(callback: CallbackQuery, state: FSMContext):
    answer = str(callback.data)
    back_answer_db = db.select(user_id=callback.from_user.id, text=answer) 
    name = f"Название:\n{back_answer_db[0]}\n"
    description = f"Описание:\n{back_answer_db[1]}\n"
    user_project_level = f"Уровень доступа:\n{back_answer_db[2]}"
    await callback.message.edit_text(text=name+description+user_project_level,
                                  reply_markup=kb.my_project)
    await state.clear()

# Удаление проекта
@router.callback_query(F.data == "del_project")
async def del_project(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.delete()
    await clbck.message.answer(text="Для удаления введите ключ проекта:")
    await state.set_state(Gen.del_project)
    
@router.message(Gen.del_project)
async def input_del_key_project(msg: Message, state: FSMContext):
    prompt = msg.text
    if prompt.isdigit():
        text = db.delete_project(user_id=msg.from_user.id, key=prompt)
        await msg.answer(text=text, reply_markup=kb.main_menu)
        await state.clear()
        
# Участники проекта
@router.callback_query(F.data == "members_project")
async def my_projects(clbck: CallbackQuery, state: FSMContext):
    data = db.get_project_members(user_id=clbck.from_user.id)
    check = len(data[0])
    if check < 1:
        if clbck.message.text != "Участников не найдено":
            await clbck.message.answer("Участников не найдено", 
                                    reply_markup=clbck.message.reply_markup)
        else:
            await clbck.answer(text="Пригласите кого-нибудь")
    else:
        if clbck.message.text != data:
            await clbck.message.edit_text(data, reply_markup=kb.my_project)
        else:
            await clbck.answer("Список участников уже выведен!")

# Отправка состояния всех задач пользователя в проекте
@router.callback_query(F.data == "tasks_states")
async def send_tasks_status(clbck: CallbackQuery, state: FSMContext):
    buf = db.plot_message(clbck.from_user.id)  # BytesIO объект
    photo = BufferedInputFile(buf.getvalue(), filename="plot.png")
    await clbck.message.answer_photo(photo=photo)
    await clbck.answer()
    await clbck.message.answer('Визуализация состояния задач', reply_markup=kb.my_project)
    

# Меню "Задания"
@router.callback_query(F.data == "tasks")
async def projects(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(text="Вот что вам доступно", reply_markup=kb.tasks)


# Вывод моих задач
@router.callback_query(F.data == "my_tasks")
async def tasks(clbck: CallbackQuery, state: FSMContext):
    type = "task"
    data = db.get_task_list_from_user(user_id=clbck.from_user.id)
    text_butt = data[0]
    calldata_butt = data[1]
    if len(text_butt) < 1:
        if clbck.message.text != "У вас нет задач, chill out":
            await clbck.message.edit_text("У вас нет задач, chill out", 
                                        reply_markup=clbck.message.reply_markup)
        else:
            await clbck.answer(text="Создайте задачу!")
    else:
        keyboard=kb.build_keyboard(text_butt=text_butt, calldata_butt=calldata_butt, type=type, width=2)
        await state.set_state(Gen.choose_task)
        await clbck.message.edit_text("Доступные задания", reply_markup=keyboard)


@router.callback_query(Gen.choose_task)
async def callback_data_task(callback: CallbackQuery, state: FSMContext):
    answer = str(callback.data)
    back_answer_db = db.select(user_id=callback.from_user.id, text=answer)
    move = "Информация о задаче:\n"
    name = f"Название:\n{back_answer_db[0]}\n"
    description = f"Описание:\n{back_answer_db[1]}\n"
    deadline = f"Дедлайн:\n{back_answer_db[2]}\n"
    user_project_level = f"Уровень доступа:\n{back_answer_db[3]}\n"
    task_status = f"Статус задачи:\n{back_answer_db[4]}"
    await callback.message.edit_text(text=move+name+description+deadline+user_project_level+task_status,
                                  reply_markup=kb.task)
    await state.set_state(Gen.choose_move_task)
    await state.update_data(task_id=answer)  

@router.callback_query(Gen.choose_move_task)
async def callback_data_choose_move_task(callback: CallbackQuery, state: FSMContext):
    answer = str(callback.data)
    if answer == "tasks":
        await state.clear()
        return
    if answer == "task_done":
        user_data = await state.get_data()
        task_id_answer = user_data['task_id']
        back_answer_db = db.get_task_done(input_user_id=callback.from_user.id, input_text=task_id_answer) 
        await callback.message.edit_text(text=back_answer_db,
                                    reply_markup=kb.my_project)
        await state.clear()


# Удаление задачи
@router.callback_query(F.data == "del_task")
async def tasks(clbck: CallbackQuery, state: FSMContext):
    type = "task"
    data = db.get_task_list_from_user(user_id=clbck.from_user.id)
    text_butt = data[0]
    calldata_butt = data[1]
    if len(text_butt) < 1:
        if clbck.message.text != "У вас нет задач, chill out":
            await clbck.message.edit_text("У вас нет задач, chill out", 
                                        reply_markup=clbck.message.reply_markup)
        else:
            await clbck.answer(text="У вас нет задач!")
    else:
        keyboard=kb.build_keyboard(text_butt=text_butt, calldata_butt=calldata_butt, type=type, width=2)
        await state.set_state(Gen.del_task)
        await clbck.message.edit_text("Выберите задачу для удаления:", reply_markup=keyboard)

@router.callback_query(Gen.del_task)
async def callback_data_task(callback: CallbackQuery, state: FSMContext):
    answer = str(callback.data)
    back_answer_db = db.delete_choose_task(user_id=callback.from_user.id, text=answer) 
    await callback.message.edit_text(text=back_answer_db,
                                  reply_markup=kb.my_project)
    await state.clear()
    


# Нажатие кнопки "Добавить задание"
@router.callback_query(F.data == "add_task")
async def create_task(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.delete()
    await clbck.message.answer("Введите название задачи:")
    await state.set_state(Gen.edit_task_name)


@router.message(Gen.edit_task_name)
async def input_edit_task_name(message: Message, state: FSMContext):
    await state.update_data(task_name=message.text)  
    await message.answer("Введите описание задачи:")
    await state.set_state(Gen.edit_task_description)  

@router.message(Gen.edit_task_description)
async def input_edit_task_description(message: Message, state: FSMContext):
    await state.update_data(task_description=message.text)
    await message.answer("Выберете дедлайн задачи:",
                         reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar())
    
    
@router.callback_query(SimpleCalendarCallback.filter(), Gen.edit_task_description)
async def input_edit_task_deadline(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    print(f"Callback Data: {callback_query.data}")
    parts = callback_query.data.split(':')
    action = parts[1]
    if action == "TODAY":
        user_data = await state.get_data()
        name = user_data['task_name']
        description = user_data['task_description']
        deadline = datetime.today().strftime("%d/%m/%Y")
        text = db.add_task(name=name, description=description, deadline=deadline, user_id=callback_query.from_user.id)
        await callback_query.message.edit_text(text=text, reply_markup=kb.my_project)
        await state.clear()
        return
    elif action == "CANCEL":
        await state.clear()
        await callback_query.message.edit_text(
            text="Вы отменили выбор даты. Выход в главное меню.",
            reply_markup=kb.main_menu)
        return
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        user_data = await state.get_data()
        name = user_data['task_name']
        description = user_data['task_description']
        deadline = date.strftime("%d/%m/%Y")
    text = db.add_task(name=name, description=description, deadline=deadline, user_id=callback_query.from_user.id)
    await callback_query.message.answer(text=text, reply_markup=kb.my_project)
    await state.clear()



# Ассистент
@router.callback_query(F.data == "assistant")
async def speak_lama(clbck: types.CallbackQuery, state: FSMContext):
    # Сообщение пользователю о подключении
    await clbck.message.edit_text("Напишите свой вопрос Ламе:", reply_markup=kb.assistant_board)
    await clbck.answer()
    await state.set_state(Gen.talk_to_assistant)


@router.message(Gen.talk_to_assistant)
async def chat_with_lama(message: types.Message, state: FSMContext):
    extractor = UserDataExtractor()
    user_message = message.text + '\n' + extractor.get_data(message.from_user.id)
    # Используем клиент Ollama для общения с моделью
    client = AsyncClient()

    try:
        print(user_message)
        response = await client.chat(
            model="test_1",  # модель
            messages=[{"role": "user", "content": user_message}]  # Формируем сообщения
        )

        cleaned_response = re.sub(r'<[^>]*>', '', response['message']['content'])  # Удаляем HTML теги, могут мешать отправке сообщения в ТГ

        # Получаем данные состояния с использованием await
        state_data = await state.get_data()

        # Если это не первое сообщение, удаляем клавиатуру с предыдущего ответа
        if state_data.get('last_message_id'):
            try:
                # Удаляем клавиатуру с предыдущего ответа Ламы
                await message.bot.edit_message_reply_markup(
                    chat_id=message.chat.id,
                    message_id=state_data['last_message_id']
                )
            except Exception as e:
                print(f"Ошибка при удалении клавиатуры: {e}")

        # Отправляем ответ от Ламы
        new_message = await message.answer(cleaned_response, reply_markup=kb.assistant_board)

        # ID текущего сообщения, чтобы удалить клавиатуру в следующем цикле
        await state.update_data(last_message_id=new_message.message_id)

    except Exception as e:
        await message.answer(f"Ошибка при общении с ассистентом: {e}", reply_markup=kb.assistant_board)


# Обработчик нажатия кнопки "Закрыть связь с Ламой"
@router.callback_query(F.data == "close_assistant")
async def close_lama(clbck: types.CallbackQuery, state: FSMContext):
    await clbck.message.delete_reply_markup()
    await state.clear() 
    await clbck.message.answer(text.menu.format(name=clbck.from_user.full_name), 
                                  reply_markup=kb.main_menu)
    await clbck.answer()  # закрываем уведомление о нажатии кнопки
