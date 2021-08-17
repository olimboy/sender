import sqlite3

from .models import Bot, Sender


def admin_id():
    # return 732918719
    return 268223984


def create_cursor(bot: Bot):
    conn = sqlite3.connect(bot.db_path)
    cursor = conn.cursor()
    return cursor


def get_10_users(sender: Sender):
    conn = sqlite3.connect(sender.bot.db_path)
    cursor = conn.cursor()
    cursor.execute(
        f'SELECT id FROM bot_user WHERE id >= {sender.current_id} AND id <= {sender.end_id} AND active ORDER BY id LIMIT 10')
    res = cursor.fetchall()
    cursor.close()
    return res


def bot_users_count(bot: Bot):
    cursor = create_cursor(bot)
    cursor.execute(f'SELECT count(*) FROM bot_user')
    res = cursor.fetchone()
    cursor.close()
    return res[0]


def parts(bot: Bot, instance_count: int):
    count = bot_users_count(bot)
    cursor = create_cursor(bot)
    _parts = []
    per_instance = int(count / instance_count + 1)
    curr_id = 0
    for i in range(instance_count):
        cursor.execute(
            f'SELECT MIN(id), MAX(id) FROM(SELECT id FROM bot_user WHERE active AND id > {curr_id} ORDER BY id LIMIT {per_instance})'
        )
        res = cursor.fetchone()
        cursor.execute(
            f'SELECT count(*) FROM bot_user WHERE id >= {res[0]} and id <= {res[1]} and active'
        )
        cnt = cursor.fetchone()[0]
        _parts.append([*res, cnt])
        curr_id = res[1]
    cursor.close()
    return _parts
