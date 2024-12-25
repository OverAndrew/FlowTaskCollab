from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu = [
    [InlineKeyboardButton(text="Проекты", callback_data="projects")],
    [InlineKeyboardButton(text="Мои задачи", callback_data="my_tasks")],
    [InlineKeyboardButton(text="Мой профиль", callback_data="my_profile")],
    [InlineKeyboardButton(text="Ассистент", callback_data="assistant")]
]
main_menu = InlineKeyboardMarkup(inline_keyboard=main_menu)

projects = [
    [InlineKeyboardButton(text="Мои проекты", callback_data="my_projects")],
    [InlineKeyboardButton(text="Вступить в проект", callback_data="find_project")],
    [InlineKeyboardButton(text="Создать проект", callback_data="create_project")],
    [InlineKeyboardButton(text="Удалить проект", callback_data="del_project")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
]
projects = InlineKeyboardMarkup(inline_keyboard=projects)

my_project = [
    [InlineKeyboardButton(text="Задачи", callback_data="tasks")],
    [InlineKeyboardButton(text="Состояние задач", callback_data="tasks_states")],
    [InlineKeyboardButton(text="Команды", callback_data="teams")],
    [InlineKeyboardButton(text="Участники проекта", callback_data="members_project")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
]
my_project = InlineKeyboardMarkup(inline_keyboard=my_project)

my_profile = [
    [InlineKeyboardButton(text="Редактировать профиль", callback_data="edit_profile")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
]
my_profile = InlineKeyboardMarkup(inline_keyboard=my_profile)

tasks = [
    [InlineKeyboardButton(text="Мои задачи", callback_data="my_tasks")],
    [InlineKeyboardButton(text="Добавить задачу", callback_data="add_task")],
    [InlineKeyboardButton(text="Удалить задачу", callback_data="del_task")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
]
tasks = InlineKeyboardMarkup(inline_keyboard=tasks)

task = [
    [InlineKeyboardButton(text="Задача выполнена", callback_data="task_done")],
    [InlineKeyboardButton(text="Выйти", callback_data="tasks")]
]
task = InlineKeyboardMarkup(inline_keyboard=task)

assistant_board = [
    [InlineKeyboardButton(text="Завершить диалог", callback_data="close_assistant")]
]
assistant_board = InlineKeyboardMarkup(inline_keyboard=assistant_board)

rmk = ReplyKeyboardRemove()

# Функция для формирования инлайн-клавиатуры на лету
def build_keyboard(text_butt: list,
                   calldata_butt: list,
                    type: str,
                    width: int = 2) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    # список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # список кнопками из аргументов args и kwargs
    if text_butt:
        for i in range(len(text_butt)):
            buttons.append(InlineKeyboardButton(
                text=text_butt[i],
                callback_data=str(type + "_" + str(calldata_butt[i])))) #максимум 64 байта
    # список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    #  объект инлайн-клавиатуры
    kb_builder.row(InlineKeyboardButton(
            text="Главное меню",
            callback_data="main_menu"
        ))
    
    return kb_builder.as_markup()
