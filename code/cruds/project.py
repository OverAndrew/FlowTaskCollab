from sqlalchemy.orm import sessionmaker
from code.models.database import User, Project, Project_team, Task, Task_team
from sqlalchemy import create_engine, and_
import random

engine = create_engine('sqlite:///flowtaskcollab.sqlite')
Session = sessionmaker(bind=engine)

## CREATE

# Функция создания нового проекта
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
        return f'Ошибка {e}'
    finally:
        session.close()

## READ

# Функция получения информации о проекте
def get_project(project_id):
    session = Session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return "Проект не найден"
        return {
            "name": project.name,
            "description": project.description,
            "key": project.key,
        }
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        session.close()

# Функция получения ключа проекта
def get_key(input_user_id: int, input_project_id: int):
    session = Session()
    _id = int(input_project_id.split('_')[1])
    try:
        project, pt = session.query(Project, Project_team).join(Project_team).filter(
            and_(Project.id == _id, Project_team.user_id == input_user_id, Project_team.user_project_level == 0)).first()
        session.commit()
        return project.key
    except Exception as e:
        return f"у вас нет доступа к ключу проекта"
    finally:
        session.close()

# Функция получения состава проекта
def get_project_members(input_user_id: int):
    session = Session()
    try:
        selected_project = session.query(User).filter_by(id = input_user_id).first().selected_project
        users = session.query(User, Project_team).join(Project_team).filter(Project_team.project_id == selected_project).all()

        if not users or not selected_project:
            return "Участники не найдены"

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

# Функция получения названий проектов
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

## UPDATE

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
            return [task.name, task.description, task.deadline, task_team.user_team_level, "выполнено" if task.status == 1 else "не выполнено"]
    except Exception as e:
        return e
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

## DELETE

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