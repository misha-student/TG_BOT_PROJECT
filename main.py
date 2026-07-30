import os
from logic import manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

cancel_button = "Отмена 🚫"

def cansel(message):
    """Отмена текущего действия и скрытие клавиатуры"""
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)
  
def no_projects(message):
    """Сообщение о том, что у пользователя нет проектов"""
    bot.send_message(message.chat.id, 'У тебя пока нет проектов!\nМожешь добавить их с помощью команды /new_project')

def gen_inline_markup(rows):
    """Создание инлайн-клавиатуры с кнопками"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows, one_time=True):
    """Создание reply-клавиатуры с одноразовым использованием"""
    markup = ReplyKeyboardMarkup(one_time_keyboard=one_time)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

attributes_of_projects = {
    'Имя проекта': ["Введите новое имя проекта", "project_name"],
    'Описание': ["Введите новое описание проекта", "description"],
    'Ссылка': ["Введите новую ссылку на проект", "url"],
    'Статус': ["Выберите новый статус задачи", "status_id"]
}

def info_project(message, user_id, project_name):
    """Вывод полной информации о проекте"""
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    
    if not skills:
        skills = 'Навыки пока не добавлены'
    
    # Красивый вывод с эмодзи (без Markdown)
    photo_info = f"\n📷 Фото: {info[4]}" if info[4] else "\n📷 Фото: не добавлено"
    
    bot.send_message(message.chat.id, f"""📁 Информация о проекте

📌 Название: {info[0]}
📝 Описание: {info[1] or 'не указано'}
🔗 Ссылка: {info[2]}
📊 Статус: {info[3]}{photo_info}
🛠 Навыки: {skills}
""")

@bot.message_handler(commands=['start'])
def start_command(message):
    """Хэндлер для команды /start - приветствие и показ команд"""
    bot.send_message(message.chat.id, """🚀 Привет! Я бот-менеджер проектов

Помогу тебе сохранить твои проекты и информацию о них! 📁
""")
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    """Хэндлер для команды /info - список всех доступных команд"""
    bot.send_message(message.chat.id,
"""
📋 Доступные команды:

🔹 /new_project - добавить новый проект
🔹 /description - добавить описание проекту
🔹 /add_photo - добавить фото проекту
🔹 /skills - добавить навык проекту
🔹 /projects - посмотреть все проекты
🔹 /delete - удалить проект
🔹 /update_projects - изменить информацию о проекте

💡 Также ты можешь просто ввести имя проекта и узнать информацию о нем!""")
    

@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    """Хэндлер для команды /new_project - начало процесса добавления проекта"""
    bot.send_message(message.chat.id, "📌 Введите название проекта:")
    bot.register_next_step_handler(message, name_project)

def name_project(message):
    """Получение названия проекта"""
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "🔗 Введите ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)

def link_project(message, data):
    """Получение ссылки на проект"""
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()] 
    bot.send_message(message.chat.id, "📊 Введите текущий статус проекта:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)

def callback_project(message, data, statuses):
    """Обработка выбора статуса и сохранение проекта"""
    status = message.text
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    if status not in statuses:
        bot.send_message(message.chat.id, "❌ Ты выбрал статус не из списка, попробуй еще раз!)", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "✅ Проект сохранен!", reply_markup=hideBoard)


@bot.message_handler(commands=['description'])
def add_description(message):
    """Хэндлер для команды /description - добавление описания проекту"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "📝 Выбери проект для добавления описания:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, get_description, projects=projects)
    else:
        no_projects(message)

def get_description(message, projects):
    """Получение описания для проекта"""
    project_name = message.text
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    if project_name not in projects:
        bot.send_message(message.chat.id, "❌ У тебя нет такого проекта, попробуй еще раз!", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, get_description, projects=projects)
        return
    
    bot.send_message(message.chat.id, "📝 Введите описание для проекта:")
    bot.register_next_step_handler(message, save_description, project_name=project_name)

def save_description(message, project_name):
    """Сохранение описания проекта"""
    description = message.text
    user_id = message.from_user.id
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    manager.update_project_description(project_name, user_id, description)
    bot.send_message(message.chat.id, f"✅ Описание для проекта '{project_name}' добавлено!", reply_markup=hideBoard)


@bot.message_handler(commands=['add_photo'])
def add_photo(message):
    """Хэндлер для команды /add_photo - добавление фото проекту"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "🖼 Выбери проект для добавления фото:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, get_photo, projects=projects)
    else:
        no_projects(message)

def get_photo(message, projects):
    """Получение фото для проекта"""
    project_name = message.text
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    if project_name not in projects:
        bot.send_message(message.chat.id, "❌ У тебя нет такого проекта, попробуй еще раз!", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, get_photo, projects=projects)
        return
    
    bot.send_message(message.chat.id, "📷 Отправьте фото для проекта:")
    bot.register_next_step_handler(message, save_photo, project_name=project_name, user_id=message.from_user.id)

def save_photo(message, project_name, user_id):
    """Сохранение фото проекта"""
    if message.text == cancel_button:
        cansel(message)
        return
    
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте фото!")
        bot.register_next_step_handler(message, save_photo, project_name=project_name, user_id=user_id)
        return
    
    # Создаем папку для фото если ее нет
    if not os.path.exists('project_photos'):
        os.makedirs('project_photos')
    
    # Сохраняем фото
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_path = f"project_photos/{project_name}_{user_id}.jpg"
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(photo_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Сохраняем путь в БД
    manager.update_project_photo(project_name, user_id, photo_path)
    bot.send_message(message.chat.id, f"✅ Фото для проекта '{project_name}' добавлено!", reply_markup=hideBoard)


@bot.message_handler(commands=['skills'])
def skill_handler(message):
    """Хэндлер для команды /skills - добавление навыков проекту"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, '🛠 Выбери проект для добавления навыка:', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)

def skill_project(message, projects):
    """Выбор проекта для добавления навыка"""
    project_name = message.text
    
    if message.text == cancel_button:
        cansel(message)
        return
        
    if project_name not in projects:
        bot.send_message(message.chat.id, '❌ У тебя нет такого проекта, попробуй еще раз!', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(message.chat.id, '🛠 Выбери навык:', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)

def set_skill(message, project_name, skills):
    """Добавление навыка проекту"""
    skill = message.text
    user_id = message.from_user.id
    
    if message.text == cancel_button:
        cansel(message)
        return
        
    if skill not in skills:
        bot.send_message(message.chat.id, '❌ Видимо, ты выбрал навык не из списка, попробуй еще раз!)', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(message.chat.id, f'✅ Навык {skill} добавлен проекту {project_name}', reply_markup=hideBoard)


@bot.message_handler(commands=['projects'])
def get_projects(message):
    """Хэндлер для команды /projects - просмотр всех проектов"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        text = "\n".join([f"📁 {x[2]}\n🔗 {x[4]}\n" for x in projects])
        bot.send_message(message.chat.id, f"📋 Твои проекты:\n\n{text}", reply_markup=gen_inline_markup([x[2] for x in projects]))
    else:
        no_projects(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Обработка нажатия на инлайн-кнопку с проектом"""
    project_name = call.data
    info_project(call.message, call.from_user.id, project_name)


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    """Хэндлер для команды /delete - удаление проекта"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        text = "\n".join([f"📁 {x[2]}\n🔗 {x[4]}\n" for x in projects])
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, f"🗑 Выбери проект для удаления:\n\n{text}", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
    else:
        no_projects(message)

def delete_project(message, projects):
    """Удаление выбранного проекта"""
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    
    if project not in projects:
        bot.send_message(message.chat.id, '❌ У тебя нет такого проекта, попробуй выбрать еще раз!', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f'🗑 Проект {project} удален!', reply_markup=hideBoard)


@bot.message_handler(commands=['update_projects'])
def update_project(message):
    """Хэндлер для команды /update_projects - изменение информации о проекте"""
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "✏️ Выбери проект, который хочешь изменить:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
    else:
        no_projects(message)

def update_project_step_2(message, projects):
    """Выбор проекта для изменения"""
    project_name = message.text
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    if project_name not in projects:
        bot.send_message(message.chat.id, "❌ Что-то пошло не так! Выбери проект еще раз:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    
    bot.send_message(message.chat.id, "✏️ Выбери, что требуется изменить в проекте:", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)

def update_project_step_3(message, project_name):
    """Выбор атрибута для изменения"""
    attribute = message.text
    reply_markup = None
    
    if message.text == cancel_button:
        cansel(message)
        return
    
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "❌ Кажется, ты ошибся, попробуй еще раз!)", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup = gen_markup([x[0] for x in rows])
    
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1])

def update_project_step_4(message, project_name, attribute):
    """Получение нового значения и обновление проекта"""
    update_info = message.text
    
    if attribute == "status_id":
        rows = manager.get_statuses()
        
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
            return
        else:
            bot.send_message(message.chat.id, "❌ Был выбран неверный статус, попробуй еще раз!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "✅ Готово! Обновления внесены!)", reply_markup=hideBoard)


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    """Обработка текстовых сообщений - поиск проекта по названию"""
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    project = message.text
    
    if project in projects:
        info_project(message, user_id, project)
        return
    
    bot.reply_to(message, "❓ Тебе нужна помощь?\nИспользуй /info для списка команд")
    info(message)

    
if __name__ == '__main__':
    bot.infinity_polling()