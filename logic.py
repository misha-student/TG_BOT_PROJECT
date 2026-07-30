import sqlite3
from config import DATABASE
import os

class DB_Manager:
    def __init__(self, database):
        self.database = database
    
    def create_tables(self):
        """Создание всех необходимых таблиц"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        # Таблица статусов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY,
                status_name TEXT NOT NULL
            )
        ''')
        
        # Таблица навыков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY,
                skill_name TEXT NOT NULL
            )
        ''')
        
        # Таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                photo TEXT,
                FOREIGN KEY (status_id) REFERENCES status(status_id)
            )
        ''')
        
        # Таблица связей проектов и навыков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_skills (
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
                PRIMARY KEY (project_id, skill_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Таблицы созданы")
    
    def fill_statuses(self):
        """Заполнение таблицы статусов начальными данными"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        statuses = [
            ('Активный',),
            ('Завершен',),
            ('В разработке',),
            ('Приостановлен',)
        ]
        
        cursor.executemany("INSERT OR IGNORE INTO status (status_name) VALUES (?)", statuses)
        conn.commit()
        conn.close()
        print("Статусы добавлены")
    
    def fill_skills(self):
        """Заполнение таблицы навыков начальными данными"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        skills = [
            ('Python',),
            ('JavaScript',),
            ('HTML',),
            ('CSS',),
            ('SQL',),
            ('C++',),
            ('Java',),
            ('PHP',),
            ('React',),
            ('Django',)
        ]
        
        cursor.executemany("INSERT OR IGNORE INTO skills (skill_name) VALUES (?)", skills)
        conn.commit()
        conn.close()
        print("Навыки добавлены")
    
    def add_photo_column(self):
        """Добавление столбца photo в таблицу projects"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN photo TEXT")
            conn.commit()
            print("Столбец photo добавлен в таблицу projects")
        except:
            print("Столбец photo уже существует")
        
        conn.close()
    
    def get_statuses(self):
        """Получение всех статусов"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT status_name FROM status")
        statuses = cursor.fetchall()
        conn.close()
        return statuses
    
    def get_status_id(self, status_name):
        """Получение ID статуса по названию"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT status_id FROM status WHERE status_name = ?", (status_name,))
        status_id = cursor.fetchone()[0]
        conn.close()
        return status_id
    
    def get_skills(self):
        """Получение всех навыков"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT skill_id, skill_name FROM skills")
        skills = cursor.fetchall()
        conn.close()
        return skills
    
    def get_projects(self, user_id):
        """Получение всех проектов пользователя"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE user_id = ?", (user_id,))
        projects = cursor.fetchall()
        conn.close()
        return projects
    
    def get_project_info(self, user_id, project_name):
        """Получение информации о проекте"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT project_name, description, url, status_name, photo
            FROM projects 
            JOIN status ON projects.status_id = status.status_id 
            WHERE user_id = ? AND project_name = ?
        ''', (user_id, project_name))
        info = cursor.fetchall()
        conn.close()
        return info
    
    def get_project_skills(self, project_name):
        """Получение навыков проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT skill_name 
            FROM skills 
            JOIN project_skills ON skills.skill_id = project_skills.skill_id 
            JOIN projects ON project_skills.project_id = projects.project_id 
            WHERE projects.project_name = ?
        ''', (project_name,))
        skills = cursor.fetchall()
        conn.close()
        return [skill[0] for skill in skills]
    
    def get_project_id(self, project_name, user_id):
        """Получение ID проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?", (project_name, user_id))
        project_id = cursor.fetchone()[0]
        conn.close()
        return project_id
    
    def insert_project(self, data):
        """Добавление нового проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (user_id, project_name, url, status_id) 
            VALUES (?, ?, ?, ?)
        ''', data[0])
        conn.commit()
        conn.close()
    
    def insert_skill(self, user_id, project_name, skill_name):
        """Добавление навыка проекту"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        cursor.execute("SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?", (project_name, user_id))
        project_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT skill_id FROM skills WHERE skill_name = ?", (skill_name,))
        skill_id = cursor.fetchone()[0]
        
        cursor.execute("INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (?, ?)", (project_id, skill_id))
        conn.commit()
        conn.close()
    
    def update_projects(self, attribute, data):
        """Обновление информации о проекте"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        update_info, project_name, user_id = data
        cursor.execute(f"UPDATE projects SET {attribute} = ? WHERE project_name = ? AND user_id = ?", (update_info, project_name, user_id))
        conn.commit()
        conn.close()
    
    def delete_project(self, user_id, project_id):
        """Удаление проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM project_skills WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE project_id = ? AND user_id = ?", (project_id, user_id))
        conn.commit()
        conn.close()
    
    def update_project_description(self, project_name, user_id, description):
        """Обновление описания проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET description = ? WHERE project_name = ? AND user_id = ?", (description, project_name, user_id))
        conn.commit()
        conn.close()
    
    def update_project_photo(self, project_name, user_id, photo_path):
        """Обновление фото проекта"""
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET photo = ? WHERE project_name = ? AND user_id = ?", (photo_path, project_name, user_id))
        conn.commit()
        conn.close()

# Создаем экземпляр менеджера
manager = DB_Manager(DATABASE)