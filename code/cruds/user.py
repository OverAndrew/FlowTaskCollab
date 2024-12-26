from sqlalchemy.orm import sessionmaker
from code.models.database import User, Project, Project_team, Task, Task_team
from sqlalchemy import create_engine

engine = create_engine('sqlite:///flowtaskcollab.sqlite')
Session = sessionmaker(bind=engine)

## CREATE

def user_init(_id, name=None, surname=None, username=None):
    session = Session()
    try:
        user = session.query(User).filter_by(id=int(_id)).first()
        if user is None:
            user = User(id=_id, name=name, surname=surname, username=username)
            session.add(user)
        else:
            if name is not None:
                user.name = name
            if surname is not None:
                user.surname = surname
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка {e}")
    finally:
        session.close()

## READ

def get_user_data(_id):
    session = Session()
    try:
        user = session.query(User).filter_by(id=int(_id)).first()
        if user.name != None and user.surname != None:
            return f'Ваше имя: {user.name}\nВаша фамилия: {user.surname}\nВаш тэг: {user.username}'
        else:
            return 'Заполните данные'
    except Exception as e:
        return e
    finally:
        session.close()

class UserDataExtractor:
    def __init__(self):
        self.engine = create_engine('sqlite:///flowtaskcollab.sqlite')
        self.Session = sessionmaker(bind=self.engine)

    def fetch_user_and_tasks(self, input_user_id):
        """Сбор данных о пользователе, проектах и задачах."""
        with self.Session() as session:
            # Поиск пользователя и его выбранный проект
            user = session.query(User).filter(User.id == input_user_id).one_or_none()
            if not user or not user.selected_project:
                return {"error": "Пользователь или выбранный проект не найдены."}

            # Поиск пользователей, работающих над теми же задачами
            users_in_task_team = (
                session.query(User)
                .join(Project_team, User.id == Project_team.user_id)
                .join(Task_team, User.id == Task_team.user_id)
                .filter(Task_team.task_id.in_(
                    session.query(Task_team.task_id)
                    .filter(Task_team.user_id == input_user_id)
                    .subquery()
                ))
                .filter(User.id != input_user_id)
                .all()
            )

            # Получение информации по проектам
            projects = (
                session.query(Project)
                .join(Project_team, Project_team.user_id == input_user_id)
                .filter(Project.id == Project_team.project_id)
                .all()
            )

            # Получение задач пользователя во всех проектах
            tasks = (
                session.query(Task)
                .join(Task_team, Task_team.task_id == Task.id)
                .filter(Task_team.user_id == input_user_id)
                .all()
            )

            # Возвращаение данных для дальнейшей обработки
            return {
                "user": user,
                "users_in_task_team": users_in_task_team,
                "projects": projects,
                "tasks": tasks,
            }

    def convert_to_json(self, data):
        """Преобразование данных"""
        if "error" in data:
            return data

        user = data["user"]
        projects = data["projects"]
        tasks = data["tasks"]
        users_in_task_team = data.get("users_in_task_team", [])

        result = {
            "current_user": {
                "name": user.name,
                "surname": user.surname,
                "username": user.username,
                "current_selected_project": user.selected_project if user.selected_project else "Не состоит в проекте",
            },
            "other_users_doing_same_tasks": [
                {
                    "other_user_name": task_user.name,
                    "other_user_surname": task_user.surname,
                    "other_user_username": task_user.username
                }
                for task_user in users_in_task_team
            ] if users_in_task_team else "Нет других пользователей, работающих над задачами",
            "projects_info": [
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "project_description": project.description,
                }
                for project in projects
            ] if projects else "Вы не состоите ни в одном проекте",
            "tasks": [
                {
                    "task_id": task.id,
                    "task_name": task.name,
                    "task_deadline": task.deadline if task.deadline else 'Дедлайн не установлен',
                    "task_priority": task.priority if task.priority else 'Приоритет не установлен',
                    "task_description": task.description,
                    "task_status": task.status,
                    "task_project_id": task.project_id
                }
                for task in tasks
            ] if tasks else "Текущих задач нет",
        }
        return result

    def get_data(self, input_user_id):
        info = self.fetch_user_and_tasks(input_user_id)
        info = self.convert_to_json(info)
        return (str(info))


## UPDATE

## DELETE

def delete_users(name):
    session = Session()
    try:
        user_to_delete = session.query(User).filter_by(name=name).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()