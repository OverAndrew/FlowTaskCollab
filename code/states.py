from aiogram.fsm.state import StatesGroup, State
# состояния для записи данных о пользователе
class Gen(StatesGroup):
    edit_profile_name = State()
    edit_surname = State()
    edit_profile_surname = State()
    edit_project_name = State()
    edit_project_description = State()
    find_project = State()
    choose_project = State()
    edit_task_name = State()
    edit_task_description = State()
    edit_task_deadline = State()
    choose_task = State()
    del_project = State()
    talk_to_assistant = State()
    
