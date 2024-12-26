from sqlalchemy.orm import sessionmaker
from code.models.database import Task, User, Task_team
from sqlalchemy import create_engine, and_
from code.visualize import show_plots
engine = create_engine('sqlite:///flowtaskcollab.sqlite')
Session = sessionmaker(bind=engine)

## CREATE

# Функция добавления задачи
def add_task(name: str, description: str, deadline: str, user_id: int):
    session = Session()
    try:
        user_id = int(user_id)
        user = session.query(User).filter_by(id = user_id).first()
        task = Task(name=name, description=description, deadline=deadline, project_id=user.selected_project, status=0)
        session.add(task)
        session.commit()
        team = Task_team(user_id=user_id, task_id=task.id, user_team_level=0)
        session.add(team)
        session.commit()
        return 'Задача добавлена!'
    except Exception as e:
        return e
    finally:
        session.close()

## READ

# Функция получения всех задач пользователя
def get_all_user_tasks(input_user_id: int):
    session = Session()
    try:
        tasks = session.query(Task).join(Task_team).filter(
            Task_team.user_id == input_user_id
        ).all()
        tasks_info = []
        for task in tasks:
            task = {
                "deadline": task.deadline,
                "status" : task.status
            }
            tasks_info.append(task)
        return tasks_info
    except Exception as e:
        return f'Ошибка: {str(e)}'
    finally:
        session.close()
#
# def get_task_list(user_id):
#     session = Session()
#     try:
#         user = session.query(User).filter_by(id=user_id).first()
#         if not user or not user.selected_project:
#             return "Выберите проект перед просмотром задач"
#
#         tasks = session.query(Task).join(Task_team).filter(
#             and_(
#                 Task_team.user_id == user_id,
#                 Task.project_id == user.selected_project
#             )
#         ).all()
#         return [{"id": task.id, "name": task.name, "status": "выполнено" if task.status else "не выполнено"} for task in
#                 tasks]
#     except Exception as e:
#         return f"Ошибка: {e}"
#     finally:
#         session.close()

# Функция получения списка задач по id проекту
def get_task_list_from_user(user_id: int):
    session = Session()
    try:
        user = session.query(User).filter_by(id = user_id).first()
        tasks = session.query(Task).join(Task_team).filter(and_(Task_team.user_id == int(user_id), Task.project_id == user.selected_project)).all()
        task_name = []
        task_id = []
        for task in tasks:
            task_name.append(task.name)
            task_id.append(task.id)
        task_name_id = [task_name, task_id]
        return task_name_id
    except Exception as e:
        return 'Ошибка'
    finally:
        session.close()

# Построение графиков по задачам пользователя
def plot_message(input_user_id: int):
    try:
        tasks = get_all_user_tasks(input_user_id)
        if not tasks:
            return "Ошибка"
        res = show_plots(tasks)
        return res
    except Exception as e:
        return "Ошибка"

# Функция получения команд
def get_project_teams_members(input_user_id: int):
    session = Session()
    try:
        selected_project = session.query(User).filter_by(id=input_user_id).first().selected_project

        task_teams = (
            session.query(Task.name, User.username)
            .join(Task_team, Task.id == Task_team.task_id)
            .join(User, Task_team.user_id == User.id)
            .filter(Task.project_id == selected_project)
            .all()
        )
        if not task_teams:
            return "Команды не найдены"
        tasks_with_users = {}
        for task_name, username in task_teams:
            tasks_with_users.setdefault(task_name, []).append(username)
        res = []
        for task_name, users in tasks_with_users.items():
            res.append(
                f"Название задачи:\n{task_name}\n"
                f"Состав команды:\n" +
                "\n".join(f" - @{user}" for user in users) +
                f"\n--------------------------------"
            )
        return "\n".join(res)
    except Exception as e:
        return str(e)
    finally:
        session.close()

## UPDATE

# Функция выполнения задачи
def get_task_done(input_user_id: int, input_text: str):
    session = Session()
    try:
        user_id = int(input_user_id)
        input_task_id = int(input_text.split('_')[1])

        user = session.query(User).filter_by(id=user_id).first()

        task = session.query(Task).filter_by(id=input_task_id).first()
        task.status = 1
        session.commit()
        return 'Задача выполнена!'
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        session.close()

## DELETE

# Функция удаления задачи
def delete_choose_task(user_id: int, text: str):
    session = Session()
    try:
        user_id = int(user_id)
        choose = text.split('_')[0]
        _id = int(text.split('_')[1])

        if choose == 'task':
            task_team_entry = session.query(Task_team).filter(Task_team.task_id == _id).first()

            if task_team_entry:
                session.delete(task_team_entry)
                remaining_task_entries = session.query(Task_team).filter_by(task_id=_id).all()
                if not remaining_task_entries:
                    task = session.query(Task).filter_by(id=_id).first()
                    if task:
                        session.delete(task)
                session.commit()
                return f"Задача была удалена успешно."
            else:
                return f"Задачи не найдено."

    except Exception as e:
        session.rollback()
        return f"Ошибка: {e}"

    finally:
        session.close()