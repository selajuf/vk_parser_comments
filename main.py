import requests
import sqlite3
import time

# Токен VK
TOKEN = 'vk1.a.oPwzQn2hmJz5iPt3-3-KgH-X9rJOYd6NR1CR794I0ORFdHAr8ajJSkohrq2bpFDwX8NEi7X_sZ6ujCZnz7slR6ac3E8fmhuQCKRqfn7sMYE1LQjVFe-Fyj_gckpwyyITjqb9RjbMsPDjDfeDYQZ5tHrGA'

# ID группы https://regvk.com/id/
GROUP_ID = "235875"

# URL для запроса последнего поста и комментариев
POST_URL = f'https://api.vk.com/method/wall.get?owner_id=-{GROUP_ID}&count=1&access_token={TOKEN}&v=5.131'
COMMENTS_URL = f'https://api.vk.com/method/wall.getComments?owner_id=-{GROUP_ID}&count=100&access_token={TOKEN}&v=5.131'


def get_last_post_id(url):
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        raise Exception(data['error']['error_msg'])

    return data['response']['items'][0]['id']


def get_comments(url, post_id):
    url = f'{url}&post_id={post_id}'
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        raise Exception(data['error']['error_msg'])

    return data['response']['items']


def create_db():
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            user_id INTEGER,
            text TEXT,
            date INTEGER
        )
    ''')

    conn.commit()
    return conn


def save_comments_to_db(conn, post_id, comments):
    cursor = conn.cursor()

    for comment in comments:
        cursor.execute('''
            INSERT INTO comments (id, post_id, user_id, text, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (comment['id'], post_id, comment['from_id'], comment['text'], comment['date']))
        print(comment['text'])

    conn.commit()


def main():
    last_saved_post_id = None
    conn = create_db()

    while True:
        try:
            last_post_id = get_last_post_id(POST_URL)

            if last_saved_post_id != last_post_id:
                comments = get_comments(COMMENTS_URL, last_post_id)
                save_comments_to_db(conn, last_post_id, comments)
                print(f"Сохранены комментарии с поста {last_post_id}")
                last_saved_post_id = last_post_id

        except Exception as e:
            print(f"Ошибка: {e}")

        # Проверка каждые 25 секунд
        time.sleep(25)


if __name__ == '__main__':
    main()