from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import User, Project, Project_team, Task, Task_team
import random
from sqlalchemy import and_
engine = create_engine('sqlite:///flowtaskcollab.sqlite')
Session = sessionmaker(bind=engine)

def user_init(_id, name=None, surname=None, username = None):
    session = Session()
    try:
        user = session.query(User).filter_by(id = int(_id)).first()
        if user is None:
            user = User(id = _id, name=name, surname=surname, username = username)
            session.add(user)
        else:
            if name is not None:
                user.name = name
            if surname is not None:
                user.surname = surname
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()

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



def create_project(creator_id, name = None, description = None, num = 0):
    session = Session()
    try:
        num = round(random.random() * 1000000000000)
        while session.query(Project).filter_by(key = num).first() is not None:
            num = round(random.random()*10000000)
        project = Project(name=name, description=description, key=num)
        session.add(project)
        user = session.query(User).filter_by(id = creator_id).first()
        creator = Project_team(user_id = user.id, project_id = project.id, user_project_level=0)
        session.add(creator)
        session.commit()
        if user.username == None:
            return [f"Проект успешно создан:\nНазвание: {project.name}\nОписание: {project.description}" \
                   f"\nID проекта: {project.id}\n", f'{project.key}']
        else:
            return [f"Проект успешно создан:\nНазвание: {project.name}\nОписание: {project.description}" \
                   f"\nID проекта: {project.id}\nСоздал: @{user.username}\n", f'{project.key}']
    except Exception as e:
        return 'Ошибка'
    finally:
        session.close()

def get_project(project_id):
    session = Session()
    try:
        project = session.query(Project).filter_by(id = project_id).first()
        if project is None:
            return 'Проект не найден'
        return f'Название проекта: {project.project_name}\nОписание проекта: {project.project_description}\nКлюч: `{project.key}`'
    except Exception as e:
        return 'Произошла ошибка при получении проекта.'
    finally:
        session.close()



def get_project_team(participant_id):
    session = Session()
    try:
        pt = session.query(Project_team).filter_by(user_id = participant_id).first()
        return f'Комадна: [ID: {pt.id}, id пользователя: {pt.user_id}, id проекта: {pt.project_id}, уровень пользователя: ' \
               f'{pt.user_project_level}]'
    except Exception as e:
        return e
    finally:
        session.close()


# Функция удаления проекта по ключу
def delete_project(user_id, key):
    session = Session()
    user_id = int(user_id)
    key = int(key)
    try:
        check = session.query(Project_team).join(Project).filter(and_(Project.key == key,
                                                                      Project_team.user_id == user_id,
                                                                      Project_team.user_project_level == 0)).first()
        if check:
            project_to_delete = session.query(Project).filter_by(key = key).first()
            session.delete(project_to_delete)
            session.commit()
            return 'Проект успешно удален'
        else:
            return 'Вы не можете удалить проект'
    except Exception as e:
        return f'Ошибка: {e}'
    finally:
        session.close()

# Функция присоединения к проекту по ключу
def join_project(user_id: int, key: int):
    session = Session()
    try:
        project = session.query(Project).filter_by(key=key).first()
        if project:
            check = session.query(Project_team).filter(and_(Project_team.user_id == user_id,Project_team.project_id == project.id)).first()
            if check == None:
                project_team = Project_team(user_id=user_id, project_id=project.id, user_project_level=5)
                session.add(project_team)
                session.commit()
                return 'Вы успешно вступили в проект'
            else:
                return 'Вы уже состоите в проекте'
        else:
            return 'Неверный ключ доступа'
    except Exception as e:
        return 'Ошибка'
    finally:
        session.close()
        
# Функция выбора проекта
def select(user_id: int, text: str):
    session = Session()
    try:
        user_id = int(user_id)
        choose = text.split('_')[0]
        _id = int(text.split('_')[1])
        if choose == 'project':
            project, pt = session.query(Project, Project_team).join(Project_team).filter(
                and_(Project.id == _id, Project_team.user_id == user_id)).first()
            user = session.query(User).filter_by(id=user_id).first()
            user.selected_project = project.id
            session.commit()
            return [project.name, project.description, pt.user_project_level]
        elif choose == 'task':
            task, task_team = session.query(Task, Task_team).filter(Task.id == _id).first()
            return [task.name, task.description, task.deadline, task_team.user_team_level]
    except Exception as e:
        return e
    finally:
        session.close()
        
def get_projects_name(user_id):
    session = Session()
    try:
        project_list = session.query(Project).join(Project_team).filter(Project_team.user_id == int(user_id)).all()
        name_list = []
        id_list = []
        for project in project_list:
            name_list.append(project.name)
            id_list.append(project.id)
        project_name_id = [name_list, id_list]
        return project_name_id
    except Exception as e:
        return 'Ошибка'
    finally:
        session.close()


# Функция получения состава проекта
def get_project_members(user_id: int):
    session = Session()
    try:
        selected_project = session.query(User).filter_by(id = user_id).first().selected_project
        users = session.query(User, Project_team).join(Project_team).filter(Project_team.project_id == selected_project).all()
        res = 'Участники проекта:\n'
        for el in users:
            us = el[0]
            pt = el[1]
            temp = ''
            temp += f'\nID: {us.id}\n'
            temp += f'Тэг: @{us.username}\n'
            temp += f"Имя: {us.name or 'Нет данных'}\n"
            temp += f"Фамилия: {us.surname or 'Нет данных'}\n"
            temp+=f'Уровень доступа: {pt.user_project_level}\n'
            temp+=f'------------------------------'
            res+= temp
        return res
    except Exception as e:
        return 'Ошибка'
    finally:
        session.close()
        
# Функция получения списка заданий по id проекту
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
        
# Функция добавления задания
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
        return 'Задание добавлено!'
    except Exception as e:
        return e
    finally:
        session.close()