from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto, InputFile, BufferedInputFile
from aiogram.types.callback_query import CallbackQuery
from aiogram import flags
from aiogram.fsm.context import FSMContext
from kb import rmk 
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# from typing import Dict

# from aiogram_dialog import DialogManager
# from aiogram_dialog.widgets.kbd import (
#     Calendar, CalendarScope, CalendarUserConfig,
# )
# from aiogram_dialog.widgets.kbd.calendar_kbd import (
#     CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView,
# )
# from aiogram_dialog.widgets.text import Const, Format


# class CustomCalendar(Calendar):
#     def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
#         return {
#             CalendarScope.DAYS: CalendarDaysView(
#                 self._item_callback_data, self.config,
#                 today_text=Format("***"),
#                 header_text=Format("> {date: %B %Y} <"),
#             ),
#             CalendarScope.MONTHS: CalendarMonthView(
#                 self._item_callback_data, self.config,
#             ),
#             CalendarScope.YEARS: CalendarYearsView(
#                 self._item_callback_data, self.config,
#             ),
#         }

#     async def _get_user_config(
#             self,
#             data: Dict,
#             manager: DialogManager,
#     ) -> CalendarUserConfig:
#         return CalendarUserConfig(
#             firstweekday=7,
#         )


# calendar = Calendar(id='calendar', on_click=on_date_selected)


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
    await state.update_data(profile_name=message.text)  # Сохраняем имя
    await message.answer(text="Введите вашу фамилию:")
    await state.set_state(Gen.edit_profile_surname)  # Переключаем на состояние для ввода фамилии

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

# Меню "Задания"
@router.callback_query(F.data == "tasks")
async def projects(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.edit_text(text="Вот что вам доступно", reply_markup=kb.tasks)

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
    name = f"Название:\n{back_answer_db[0]}\n"
    description = f"Описание:\n{back_answer_db[1]}\n"
    deadline = f"Дедлайн:\n{back_answer_db[2]}\n"
    user_project_level = f"Уровень доступа:\n{back_answer_db[3]}"
    await callback.message.edit_text(text=name+description+deadline+user_project_level,
                                  reply_markup=kb.my_project)
    await state.clear()

# Нажатие кнопки "Добавить задание"
@router.callback_query(F.data == "add_task")
async def create_task(clbck: CallbackQuery, state: FSMContext):
    await clbck.message.delete()
    await clbck.message.answer("Введите название задания:")
    await state.set_state(Gen.edit_task_name)

#  
@router.message(Gen.edit_task_name)
async def input_edit_task_name(message: Message, state: FSMContext):
    await state.update_data(task_name=message.text)  
    await message.answer("Введите описание задания:")
    await state.set_state(Gen.edit_task_description)  

@router.message(Gen.edit_task_description)
async def input_edit_task_description(message: Message, state: FSMContext):
    await state.update_data(task_description=message.text)  
    await message.answer("Введите дедлайн задания:")
    await state.set_state(Gen.edit_task_deadline)  

@router.message(Gen.edit_task_deadline)
async def input_edit_task_deadline(message: Message, state: FSMContext):
    await state.update_data(task_deadline=message.text) 
    user_data = await state.get_data()

    name = user_data['task_name']
    description = user_data['task_description']
    deadline = user_data['task_deadline']
    text = db.add_task(name=name, description=description, deadline=deadline, user_id=message.from_user.id)
    await message.answer(text=text, reply_markup=kb.my_project)
    await state.clear()


