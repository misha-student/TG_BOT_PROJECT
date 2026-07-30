import sqlite3
from config import DATABASE

def fill_statuses():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Добавляем статусы
    statuses = [
        ('Активный',),
        ('Завершен',),
        ('В разработке',),
        ('Приостановлен',)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO status (status_name) VALUES (?)", statuses)
    
    conn.commit()
    conn.close()
    print("Статусы добавлены!")

def fill_skills():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Добавляем навыки
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
    print("Навыки добавлены!")

if __name__ == "__main__":
    fill_statuses()
    fill_skills()