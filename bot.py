import telebot
from telebot import types
import mysql.connector
from datetime import date
from pandas import DataFrame
import matplotlib.pyplot as plt
import io
import time

bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def start(message):
    user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('/start', '/reg', '/change', '/coaches')
    user_markup.row('/order', '/info', '/orders', '/cancel')
    bot.send_message(message.from_user.id, 'Рады тебя приветствовать в конном клубе! Начнем? \n'
                                               'Тебе доступна панель управления: \n'
                                               'Для регистрации напиши /reg \n'
                                               'Для изменения данных пользователя напиши /change \n'
                                               'Для просмотра списка преподавателей напиши /coaches \n'
                                               'Для записи напиши /order \n'
                                               'Для получения основной информации напиши /info \n'
                                               'Для просмотра расписания напиши /orders \n'
                                               'Для отмены записи напиши /cancel \n', reply_markup=user_markup)
@bot.message_handler(commands=['coach'])
def start(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    user_id = message.from_user.id
    cur.execute(f'SELECT * FROM coaches WHERE coach_id = "%s"' % user_id)
    if cur.fetchone():
        cur.close()
        conn.close()
        user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('/new_day', '/re_order', '/timetable')
        bot.send_message(message.from_user.id, 'Успешная авторизация тренера.\nДоступна панель управления\n'
                                               'Добавить день - /new_day\n'
                                               'Изменить запись - /re_order\n'
                                               'Просмотр расписания - /timetable', reply_markup=user_markup)
    else:
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, "Недостаточно прав. Введите /start.")
@bot.message_handler(commands=['admin'])
def start(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    user_id = message.from_user.id
    cur.execute(f'SELECT * FROM admins WHERE admin_id = "%s"' % user_id)
    if cur.fetchone():
        cur.close()
        conn.close()
        user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('/new_day_for', '/re_order_for', '/analysys')
        user_markup.row('/new_coach', '/new_admin')
        user_markup.row('/archive', '/read_archive', '/from_archive')
        bot.send_message(message.from_user.id, 'Успешная авторизация администратора.\nДоступна панель управления\n'
                                               'Добавить день тренеру - /new_day_for\n'
                                               'Изменить запись тренеру - /re_order_for\n'
                                               'Перейти на панель анализа - /analysys\n'
                                               'Создать тренера - /new_coach\n'
                                               'Создать администратора - /new_admin\n'
                                               'Архивация данных из базы - /archive\n'
                                               'Чтение данных из базы - /read_archive\n'
                                               'Восстановить данные их архива - /from_archive', reply_markup=user_markup)
    else:
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, "Недостаточно прав. Введите /start.")
@bot.message_handler(commands=['analysys'])
def analysys(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    user_id = message.from_user.id
    cur.execute(f'SELECT * FROM admins WHERE admin_id = "%s"' % user_id)
    if cur.fetchone():
        cur.close()
        conn.close()
        user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.row('/a_coaches', '/a_coach', '/a_date')
        bot.send_message(message.from_user.id, 'Доступна панель анализа.\n'
                                               'Для вывода данных по тренерам напишите /a_coaches\n'
                                               'Для вывода данных по тренеру напишите /a_coach\n'
                                               'Для вывода данных о занятиях напишите /a_date\n', reply_markup=user_markup)
    else:
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, "Недостаточно прав. Введите /start.")
@bot.message_handler(content_types=['text'])
def text(message):
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
    cur = conn.cursor()
    cur.execute('DELETE FROM orders WHERE user_id IS NULL AND order_date <= CURDATE()')
    conn.commit()
    user_id = message.from_user.id
    cur.execute(f'SELECT * FROM coaches WHERE coach_id = {user_id}')
    coa = cur.fetchone()
    cur.execute(f'SELECT * FROM admins WHERE admin_id = {user_id}')
    adm = cur.fetchone()
    if message.text == '/reg':
        cur.execute('SELECT * FROM users WHERE user_id ="%s"' % user_id)
        if cur.fetchone():
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы.')
            cur.close()
            conn.close()
        else:
            cur.execute('INSERT INTO users (user_id) VALUES ("%s")' % (user_id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.from_user.id, "Введите имя.")
            bot.register_next_step_handler(message, set_name, 'users', 'user_id')
    elif message.text == '/change':
        cur.execute('SELECT * FROM users WHERE user_id ="%s"' % user_id)
        if cur.fetchone():
            bot.send_message(message.from_user.id, "Введите имя.")
            bot.register_next_step_handler(message, set_name, 'users', 'user_id')
            cur.close()
            conn.close()
        else:
            cur.execute('INSERT INTO users (user_id) VALUES ("%s")' % (user_id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.from_user.id, "Введите имя.")
            bot.register_next_step_handler(message, set_name, 'users', 'user_id')
    elif message.text == '/order':
        user_id = message.from_user.id
        cur.execute('SELECT * FROM users WHERE user_id ="%s"' % user_id)
        user_exist = cur.fetchone()
        if not user_exist:
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Вы не зарегистрированы. Введите /reg.")
        else:
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Введите фамилию тренера.")
            bot.register_next_step_handler(message, coach_order)
    elif message.text == '/info':
        bot.send_message(message.chat.id, "Добрый день! Вы обратились к боту конного клуба! Здесь Вы можете записаться на занятие к интересующему тренеру, первое занятие бесплатно!\n"
                                          "Режим работы: ежедневно 10:00 - 19:00\n"
                                          "Для записи наобходима регистрация, чтобы в случае изменений Вас оповестили. Требуется ввод фамилии и имени.\n"
                                          "Если Вы хотите изменить дату и время занятия или отменить его, позвоните по номеру 8(888)888-88-88.")
        cur.close()
        conn.close()
    elif message.text == '/cancel':
        cur.execute('SELECT * FROM orders WHERE user_id = "%s" AND order_date >= CURDATE()' % user_id)
        if not cur.fetchone():
            bot.send_message(message.from_user.id,
                             'Вы не записаны на занятие. Для записи введите /order.')
            cur.close()
            conn.close()
        else:
            cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i") FROM orders '
                        f'WHERE user_id = {user_id} AND order_date >= CURDATE()')
            order_list = cur.fetchall()
            current_date = date.today()
            markup = types.InlineKeyboardMarkup()
            i = 0
            for el in order_list:
                if el[2] >= current_date:
                    cur.execute('SELECT * FROM coaches WHERE coach_id = "%s"' % el[1])
                    info = cur.fetchone()
                    markup.add(types.InlineKeyboardButton(text=f'У тренера {info[2]} {info[1]} {el[2]} в {el[3]}',
                                                          callback_data=f'cancel_{el[0]}'))
                    i += 1
                if i == 6:
                    break
            cur.close()
            conn.close()
            markup.add(types.InlineKeyboardButton(text=f'Завершить', callback_data=f'cancellation'))
            bot.send_message(message.from_user.id, f"Выберите запись для отмены:", reply_markup=markup)
    elif message.text == '/orders':
        user_id = message.from_user.id
        cur.execute('SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE user_id ="%s" AND order_date > NOW() ORDER BY order_date' % user_id)
        info = cur.fetchall()
        txt = ""
        for el in info:
            txt += f"Дата: {el[2]}, время: {el[3]};\n"
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f"Данные о Ваших будущих занятиях:\n{txt}")
    elif message.text == '/coaches':
        cur.execute('SELECT * FROM coaches ')
        info = cur.fetchall()
        txt = ""
        for el in info:
            txt += f"{el[2]} {el[1]}\n"
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f"Наши преподаватели:\n{txt}")
    elif message.text == '/new_day' and coa:
        cur.execute('SELECT * FROM orders WHERE coach_id ="%s" ORDER BY order_date DESC LIMIT 1' % user_id)
        info = cur.fetchone()
        bot.send_message(message.from_user.id, f'Введите дату.\nПоследний день - {str(info[2])}')
        cur.close()
        conn.close()
        bot.register_next_step_handler(message, new_day, user_id)
    elif message.text == '/re_order' and coa:
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, "Для изменения записи введите дату в формате 2023-01-31.")
        bot.register_next_step_handler(message, re_order, user_id)
    elif message.text == '/timetable' and coa:
        cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE coach_id ={user_id} AND order_date >= CURDATE()')
        info = cur.fetchall()
        txt = ""
        for el in info:
            txt += f"Дата: {el[2]}, время: {el[3]}\n"
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f"Данные о Ваших будущих занятиях:\n{txt}")
        cur.close()
        conn.close()
    elif message.text == '/new_day_for' and adm:
        bot.send_message(message.chat.id, "Введите фамилию тренера.")
        cur.close()
        conn.close()
        bot.register_next_step_handler(message, new_day_for)
    elif message.text == "/a_coaches" and adm:
        cur.execute('SELECT c.surname AS surname, COUNT(o.id) AS count '
                    'FROM orders o '
                    'INNER JOIN coaches c ON c.coach_id = o.coach_id '
                    'GROUP BY c.surname '
                    'ORDER BY c.surname DESC;')
        df = DataFrame(cur.fetchall())
        df.columns = ['surname', 'count']
        cur.close()
        conn.close()
        plt.pie(df['count'], labels=df['surname'], autopct='%1.1f%%', textprops={'size': 'x-large'}, startangle=60)
        plt.legend(loc='upper right', labels=df['surname'], fontsize=12)
        plt.title('Доля занятий по тренерам', fontsize=15)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.clf()
        buf.seek(0)
        bot.send_photo(message.from_user.id, photo=buf)
    elif message.text == "/a_coach" and adm:
        bot.send_message(message.chat.id, "Введите фамилию тренера.")
        cur.close()
        conn.close()
        bot.register_next_step_handler(message, a_coach)
    elif message.text == "/a_date" and adm:
        cur.execute('SELECT c.surname AS surname, o.order_date AS date, COUNT(o.id) AS id '
                    'FROM orders o '
                    'INNER JOIN coaches c ON c.coach_id = o.coach_id '
                    'GROUP BY c.surname, o.order_date '
                    'ORDER BY c.surname DESC;')
        df = DataFrame(cur.fetchall())
        df.columns = ['surname', 'date', 'id']
        surnames = df['surname'].unique()
        for i in surnames:
            df1 = df[df['surname'] == i]
            plt.plot(df1['date'], df1['id'])
        cur.close()
        conn.close()
        plt.legend(df['date'], loc='upper right', labels=surnames, fontsize=12)
        plt.title('Занятия по датам', fontsize=15)
        plt.xticks(rotation=20)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.clf()
        buf.seek(0)
        bot.send_photo(message.from_user.id, photo=buf)
    elif message.text == "/archive" and adm:
        cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = "horse_club"')
        info = cur.fetchall()
        markup = types.InlineKeyboardMarkup()
        txt = ['администраторов', 'тренеров', 'заказов', 'пользователей']
        i = 0
        for el in info:
            markup.add(types.InlineKeyboardButton(text=f'Таблица {txt[i]}', callback_data=f'archive_{el}'))
            i += 1
        cur.close()
        conn.close()
        markup.add(types.InlineKeyboardButton(text=f'Завершить', callback_data=f'cancellation'))
        bot.send_message(message.chat.id, "Выберите таблицу для архивирования:", reply_markup=markup)
    elif message.text == "/read_archive" and adm:
        cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = "horse_club"')
        info = cur.fetchall()
        markup = types.InlineKeyboardMarkup()
        txt = ['администраторов', 'тренеров', 'заказов', 'пользователей']
        i = 0
        for el in info:
            markup.add(types.InlineKeyboardButton(text=f'Таблица {txt[i]}', callback_data=f'read_{el}'))
            i += 1
        cur.close()
        conn.close()
        markup.add(types.InlineKeyboardButton(text=f'Завершить', callback_data=f'cancellation'))
        bot.send_message(message.chat.id, "Выберите таблицу для чтения архива:", reply_markup=markup)
    elif message.text == "/from_archive" and adm:
        cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = "horse_club"')
        info = cur.fetchall()
        markup = types.InlineKeyboardMarkup()
        txt = ['администраторов', 'тренеров', 'заказов', 'пользователей']
        i = 0
        for el in info:
            markup.add(types.InlineKeyboardButton(text=f'Таблица {txt[i]}', callback_data=f'from_{el}'))
            i += 1
        cur.close()
        conn.close()
        markup.add(types.InlineKeyboardButton(text=f'Завершить', callback_data=f'cancellation'))
        bot.send_message(message.chat.id, "Выберите таблицу для внесения данных из архива:", reply_markup=markup)
    elif message.text == '/re_order_for' and adm:
        bot.send_message(message.chat.id, "Введите фамилию тренера.")
        cur.close()
        conn.close()
        bot.register_next_step_handler(message, re_order_for)
    elif message.text == '/new_admin':
        user_id = message.from_user.id
        cur.execute(f'SELECT * FROM admins WHERE admin_id = "%s"' % user_id)
        if cur.fetchone():
            cur.execute('INSERT INTO admins (admin_id) VALUE (1)')
            conn.commit()
            bot.send_message(message.chat.id,"Создание администратора. Выбранный пользователь должен ввести /new_admin")
            time.sleep(12)
            cur.execute('SELECT * FROM admins WHERE admin_id = 1')
            if not cur.fetchone():
                bot.send_message(message.chat.id, "Администратор успешно создан.")
            else:
                cur.execute('DELETE FROM admins WHERE admin_id = 1')
                conn.commit()
                bot.send_message(message.chat.id, "Доступ закрыт.")
            cur.close()
            conn.close()
        else:
            cur.execute('SELECT * FROM admins WHERE admin_id = 1')
            if cur.fetchone():
                cur.execute('UPDATE admins SET admin_id = "%s" WHERE admin_id = 1' % (user_id))
                conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id,"Введите имя")
                bot.register_next_step_handler(message, set_name, 'admins', 'admin_id')
            else:
                cur.close()
                conn.close()
    elif message.text == '/new_coach':
        user_id = message.from_user.id
        cur.execute(f'SELECT * FROM admins WHERE admin_id = "%s"' % user_id)
        if cur.fetchone():
            cur.execute('INSERT INTO coaches (coach_id) VALUE (1)')
            conn.commit()
            bot.send_message(message.chat.id,
                             "Создание тренера. Выбранный пользователь должен ввести /new_coach")
            time.sleep(12)
            cur.execute('SELECT * FROM coaches WHERE coach_id = 1')
            if not cur.fetchone():
                bot.send_message(message.chat.id, "Тренер успешно создан.")
            else:
                cur.execute('DELETE FROM coaches WHERE coach_id = 1')
                conn.commit()
                bot.send_message(message.chat.id, "Доступ закрыт.")
            cur.close()
            conn.close()
        else:
            cur.execute('SELECT coach_id FROM coaches WHERE coach_id = 1')
            if cur.fetchone():
                cur.execute('UPDATE coaches SET coach_id = "%s" WHERE coach_id = 1' % (user_id))
                conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id,"Введите имя")
                bot.register_next_step_handler(message, set_name, 'coaches', 'coach_id')
            else:
                cur.close()
                conn.close()
    else:
        bot.send_message(message.chat.id, 'Рады тебя приветствовать в конном клубе! Начнем? \n'
                                               'Тебе доступна панель управления: \n'
                                               'Для регистрации напиши /reg \n'
                                               'Для изменения данных пользователя напиши /change \n'
                                               'Для просмотра списка преподавателей напиши /coaches \n'
                                               'Для записи напиши /order \n'
                                               'Для получения основной информации напиши /info \n'
                                               'Для просмотра расписания напиши /orders \n'
                                               'Для отмены записи напиши /cancel \n')
        cur.close()
        conn.close()
def set_name(message, table_name, name_id):
    name = message.text
    user_id = message.from_user.id
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    cur.execute(f'UPDATE {table_name} SET name = "%s" WHERE {name_id} = "%s"' % (name, user_id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.from_user.id, "Введите фамилию.")
    bot.register_next_step_handler(message, set_surname, table_name, name_id)
def set_surname(message, table_name, name_id):
    surname = message.text
    user_id = message.from_user.id
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    cur.execute(f'UPDATE {table_name} SET surname = "%s" WHERE {name_id} = "%s"' % (surname, user_id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f"Данные сохранены!")
def coach_order(message):
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
    cur = conn.cursor()
    cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
    if not cur.fetchone():
        bot.send_message(message.from_user.id,
                         'Данного тренера нет в базе. Вывести список преподавателей? Напишите /coaches')
        cur.close()
        conn.close()
    else:
        cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
        info = cur.fetchone()
        coach_or = info[0]
        ns = f'{info[2]} {info[1]}'
        cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE coach_id = {coach_or}')
        order_list = cur.fetchall()
        cur.close()
        conn.close()
        current_date = date.today()
        markup = types.InlineKeyboardMarkup()
        i = 0
        for el in order_list:
            if el[2] > current_date and el[4] == None:
                markup.add(types.InlineKeyboardButton(text=f'Дата: {el[2]}, время: {el[3]}', callback_data=f'order_{el[0]}'))
                i += 1
            if i == 6:
                break
        bot.send_message(message.from_user.id, f"У тренера {ns} доступны следующие занятия:", reply_markup=markup)
def new_day(message, user_id):
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT HOUR(order_time) FROM orders WHERE order_date = '{message.text}' AND coach_id = {user_id}")
        markup = types.InlineKeyboardMarkup()
        info = cur.fetchall()
        hours_list = [row[0] for row in info]
        for i in range(10, 19):
            if i not in hours_list:
                markup.add(types.InlineKeyboardButton(text=f'Дата: {message.text}, время: {i}:00',
                                                      callback_data=f'day_{message.text}_{i}_{user_id}'))
        markup.add(types.InlineKeyboardButton(text=f'Завершить', callback_data=f'cancellation'))
        bot.send_message(message.from_user.id, f"Выберите рабочие часы:", reply_markup=markup)
    except mysql.connector.Error:
        bot.send_message(message.chat.id, f'Не удалось распознать дату.')
        cur.close()
        conn.close()
def re_order(message, user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club"
    )
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE coach_id = %s and order_date = %s', (user_id, message.text))
        info = cur.fetchall()
        markup = types.InlineKeyboardMarkup()
        for el in info:
            markup.add(types.InlineKeyboardButton(text=f'Дата: {el[2]}, время: {el[3]}', callback_data=f're_order_{el[2]}_{el[3]}'))
        markup.add(types.InlineKeyboardButton(text='Завершить', callback_data='cancellation'))
        bot.send_message(message.chat.id, "Выберите запись для изменения:", reply_markup=markup)
        cur.close()
        conn.close()
    except mysql.connector.Error:
        bot.send_message(message.chat.id, f'Не удалось распознать дату.')
        cur.close()
        conn.close()
def new_date(message, id):
    order_date = message.text
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    try:
        cur.execute(f'UPDATE orders SET order_date = STR_TO_DATE("{order_date}", "%Y-%m-%d") WHERE id = {id}')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, f'Введите время.')
        bot.register_next_step_handler(message, new_time, id)
    except ValueError:
        bot.send_message(message.chat.id, f'Не удалось распознать дату.')
        cur.close()
        conn.close()
        bot.register_next_step_handler(message, new_date, id)
def new_time(message, id):
    order_time = message.text
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    try:
        cur.execute('UPDATE orders SET order_time = %s WHERE id = %s', (order_time, id))
        conn.commit()
        cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders  WHERE id = "%s"' % id)
        info = cur.fetchone()
        bot.send_message(message.chat.id, f'Текущие данные записи:\nДата: {info[2]}, время: {info[3]}.')
        user_id = info[4]
        cur.execute(f'SELECT * FROM users WHERE user_id = "%s"' % user_id)
        info2 = cur.fetchone()
        if info2:
            txt = f"Здравствуйте, {info2[1]}!\nОбращаем Ваше внимание, что была изменена запись на занятие. Оно состоится {info[2]} в {info[3]}!\nПроверьте расписание Ваших занятий командой /orders."
            bot.send_message(chat_id=info2[0], text=txt)
        cur.close()
        conn.close()
    except ValueError:
        bot.send_message(message.chat.id, f'Не удалось распознать дату.')
        cur.close()
        conn.close()
def get_message(message, id):
    bot.register_next_step_handler(message, new_date, id)
def new_day_for(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
    if not cur.fetchone():
        bot.send_message(message.from_user.id, 'Данного тренера нет в базе. Вывести список преподавателей? Напишите /coaches.')
        cur.close()
        conn.close()
    else:
        cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
        coach = cur.fetchone()
        user_id = coach[0]
        ns = f'{coach[2]} {coach[1]}'
        cur.execute('SELECT * FROM orders WHERE coach_id ="%s" ORDER BY order_date DESC LIMIT 1' % user_id)
        info = cur.fetchall()
        cur.close()
        conn.close()
        for el in info:
            bot.send_message(message.from_user.id, f"Введите дату для добавлению записей тренеру {ns}. Последний день - {str(el[2])} ")
        bot.register_next_step_handler(message, new_day, user_id)
def a_coach(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
    if not cur.fetchone():
        bot.send_message(message.from_user.id,
                         'Данного тренера нет в базе. Вывести список преподавателей? Напишите /coaches')
        cur.close()
        conn.close()
    else:
        cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
        info = cur.fetchone()
        ns = info[2] + " " + info[1]
        cur.execute(f'SELECT o.order_date AS date '
                    'FROM orders o '
                    'INNER JOIN coaches c ON c.coach_id = o.coach_id '
                    'WHERE c.surname = "%s"' % message.text)
        df = DataFrame(cur.fetchall())
        df.columns = ['date']
        cur.close()
        conn.close()
        plt.hist(df, width = 0.6)
        plt.rcParams["figure.figsize"] = (20, 6)
        plt.title(f'Количество занятий по датам у {ns}', fontsize=15)
        plt.xticks(rotation=20)
        plt.xlabel("Дата занятий", fontsize=6)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.clf()
        buf.seek(0)
        bot.send_photo(message.from_user.id, photo=buf)
def re_order_for(message):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="horse_club")
    cur = conn.cursor()
    cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
    if not cur.fetchone():
        bot.send_message(message.from_user.id,
                         'Данного тренера нет в базе. Вывести список преподавателей? Напишите /coaches')
        cur.close()
        conn.close()
    else:
        cur.execute('SELECT * FROM coaches WHERE surname = "%s"' % message.text)
        coach = cur.fetchall()
        for el in coach:
            coach_order = el[0]
            ns = f'{el[2]} {el[1]}'
        cur.close()
        conn.close()
        bot.send_message(message.from_user.id, f"Для изменения записи тренеру {ns} введите дату в формате 2023-01-31")
        bot.register_next_step_handler(message, re_order, coach_order)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.split('_')[0] == 'order':
        order_id = call.data.split('_')[1]
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="horse_club")
        cur = conn.cursor()
        user_id = call.from_user.id
        cur.execute('UPDATE orders SET user_id = "%s" WHERE id = "%s"' % (user_id, order_id))
        conn.commit()
        cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE id = "{order_id}"')
        info = cur.fetchone()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, f'Вы успешно записались на {info[2]} в {info[3]}!')
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data.split('_')[0] == 'day':
        day_date = call.data.split('_')[1]
        day_time = call.data.split('_')[2]
        user_id = call.data.split('_')[3]
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
        cur = conn.cursor()
        cur.execute(f'INSERT INTO orders (coach_id, order_date, order_time) VALUES ({user_id}, STR_TO_DATE("{day_date}", "%Y-%m-%d"), STR_TO_DATE("{day_time}", "%H:%i"))')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.from_user.id, f'Добавлена запись на {day_date} в {day_time}:00!')
    elif call.data == 'cancellation':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data.split('_')[0] == 'cancel':
        cancel_id = call.data.split('_')[1]
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
        cur = conn.cursor()
        cur.execute(f'UPDATE orders SET user_id = NULL WHERE id = "%s"' % cancel_id)
        conn.commit()
        cur.execute(f'SELECT coach_id, order_date, DATE_FORMAT(order_time, "%H:%i") FROM orders WHERE id = {cancel_id}')
        info = cur.fetchone()
        cur.execute(f'SELECT * FROM coaches WHERE coach_id = "%s"' % info[0])
        coach_sn = cur.fetchone()
        bot.send_message(call.from_user.id,
                         f'Запись к тренеру {coach_sn[2]} {coach_sn[1]} {info[1]} в {info[2]} отменена.')
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cur.close()
        conn.close()
    elif call.data.split('_')[0] == 're' and call.data.split('_')[1] == 'order':
        order_date = call.data.split('_')[2]
        order_time = call.data.split('_')[3]
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="horse_club")
        cur = conn.cursor()
        user_id = call.from_user.id
        cur.execute('SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE coach_id = %s AND order_date = %s AND order_time = %s', (user_id, order_date, order_time))
        info = cur.fetchone()
        id = info[0]
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, f'Текущая запись: Дата: {order_date}, время - {order_time}. Введите новую дату.')
        get_message(call.message, id)
    elif call.data.split('_')[0] == 'del':
        order_id = call.data.split('_')[1]
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="horse_club")
        cur = conn.cursor()
        cur.execute(f'SELECT id, coach_id, order_date, DATE_FORMAT(order_time, "%H:%i"), user_id FROM orders WHERE id = "%s"' % order_id)
        info = cur.fetchone()
        bot.send_message(call.message.chat.id, f'Удалена запись {info[2]} в {info[3]}.')
        cur.execute('DELETE FROM orders WHERE id = "%s"' % order_id)
        conn.commit()
        cur.close()
        conn.close()
    elif call.data.split('_')[0] == 'archive':
        table_name = call.data.split('_')[1]
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="horse_club")
        cur = conn.cursor()
        table_name = table_name.strip("('',)")
        cur.execute(f'SELECT * FROM {table_name}')
        info = cur.fetchall()
        txt = ""
        for el in info:
            for i in el:
                txt += str(i) + " "
            txt += "\n"
        cur.close()
        conn.close()
        filename = f"{table_name}.txt"
        with open(filename, 'w') as file:
            file.write(txt)
            bot.send_message(call.message.chat.id, f"Данные сохранены в файл {table_name}.txt")
    elif call.data.split('_')[0] == 'read':
        table_name = call.data.split('_')[1]
        table_name = table_name.strip("('',)")
        filename = f"{table_name}.txt"
        with open(filename, 'r') as f:
            txt = f.read()
            bot.send_message(call.message.chat.id, txt)
    elif call.data.split('_')[0] == 'from':
        table_name = call.data.split('_')[1]
        table_name = table_name.strip("('',)")
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="horse_club")
        cur = conn.cursor()
        filename = f"{table_name}.txt"
        with open(filename, "r") as file:
            data = file.readlines()
        for line in data:
            values = line.strip("\n").split(" ")
            try:
                if table_name == 'users':
                    cur.execute(f'INSERT INTO {table_name} VALUES ("%s", "%s")' % (values[0], values[1]))
                elif table_name == 'admins' or table_name == 'coaches':
                    cur.execute(f'INSERT INTO {table_name} VALUES ("%s", "%s", "%s")' % (values[0], values[1], values[2]))
                elif table_name == 'orders':
                    if values[4] == "None":
                        cur.execute(f'INSERT INTO {table_name} (id, coach_id, order_date, order_time) VALUES ("%s", "%s", "%s", "%s")'
                                    % (values[0], values[1], values[2], values[3]))
                    else:
                        cur.execute(f'INSERT INTO {table_name} VALUES ("%s", "%s", "%s", "%s", "%s")' % (values[0], values[1], values[2],
                                                                                                         values[3], values[4]))
                conn.commit()
            except mysql.connector.Error:
                values = ''
        bot.send_message(call.message.chat.id, f"В базу вставлены данные таблицы {table_name}.")
        cur.close()
        conn.close()
bot.polling(none_stop=True)