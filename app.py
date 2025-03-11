from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

db_file = 'translations.db'


# Лепим и варим БД, если ранее ее не создали
def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT NOT NULL,
                transliterated TEXT NOT NULL
            )
        ''')
        conn.commit()


init_db()

def transliterate(text):
    translit_map = {

        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }


    return ''.join(translit_map.get(char, char) for char in text)

def transliterate_en_ru(text):

    translit_en_to_ru_map = {
        'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д',
        'e': 'е', 'yo': 'ё', 'zh': 'ж', 'z': 'з', 'i': 'и',
        'y': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
        'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т',
        'u': 'у', 'f': 'ф', 'kh': 'х', 'ts': 'ц', 'ch': 'ч',
        'sh': 'ш', 'shch': 'щ', 'y': 'ы', 'e': 'э', 'yu': 'ю', 'ya': 'я'
    }

    return ''.join(translit_en_to_ru_map.get(char, char) for char in text)


@app.route('/арі', methods=['POST'])
def transliterate_text():
    data = request.json
    text = data.get('data', '')

    if (transliterate(text) is None) or (transliterate(text) == text):
        transliterated_text = transliterate_en_ru(text)
    else:
        transliterated_text = transliterate(text)


    return jsonify({"status": "success", "data": transliterated_text})


@app.route('/save', methods=['POST'])
def save_translation():
    data = request.json
    original_text = data.get('original', '')
    transliterated_text = data.get('transliterated', '')

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO translations (original, transliterated)
            VALUES (?, ?)
        ''', (original_text, transliterated_text))
        conn.commit()

    return jsonify({"status": "success"})


@app.route('/history', methods=['GET'])
def get_history():
    n = int(request.args.get('n', 5))  # Получаем N из параметра запроса
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()

    # Получаем последние N записей
    cursor.execute('SELECT original, transliterated FROM translations ORDER BY id DESC LIMIT ?', (n,))
    rows = cursor.fetchall()

    # Форматируем данные для ответа
    history_data = [{'original': row[0], 'transliterated': row[1]} for row in rows]

    conn.close()
    return jsonify({"data": history_data})


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(port=3000)
