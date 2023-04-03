from flask import Flask, request
import requests
from requests.exceptions import ConnectionError

from models.plate_reader import PlateReader

import io
import logging
from PIL import UnidentifiedImageError

# доступные индексы изображений
AVAILABLE_IMAGE_IDS = {'10022', '9965'}

app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
storage_server_url = 'http://51.250.83.169:7878'


@app.route('/health')
def health():
    return {
        'result': True
    }

# ip:port/toUpper?s=hello
@app.route('/upper')
def to_upper():
    if 's' not in request.args:
        return 'invalid args', 400

    s = request.args['s']
    return {
        'result': s.upper(), 
    }

# ip:port/readNumberFromID?img_id=10022[&img_id=9965]
@app.route('/readNumberFromID')
def read_number_from_id():
    if 'img_id' not in request.args:
        return 'invalid args', 400
    
    img_id_list = request.args.getlist('img_id')
    print(img_id_list)

    result = {}

    for i, img_id in enumerate(img_id_list):
        # обработка недоступных img_id
        if img_id not in AVAILABLE_IMAGE_IDS:
            return {'error': f'invalid image ID ({img_id})'}, 400

        try:
            response = requests.get(f'http://51.250.83.169:7878/images/{img_id}')
        # обработка случая недоступности сервера с изображениями
        except ConnectionError:
            return {'error': 'storage server is unreachable'}, 502

        img = io.BytesIO(response.content)
        try:
            result[img_id] = plate_reader.read_text(img)
        # обработка случая невалидного ответа сервера на запрос изображения с валидным индексом
        except UnidentifiedImageError:
            return {'error': f'Image with ID={img_id} is unavailable in storage server'}, 502
    
    return result

# /readNumber <- img bin
# {"name": "щ123у11"}
@app.route('/readNumber', methods=['POST'])
def read_number():
    # request.get_data() возвращает тело запроса - сырые байты
    body = request.get_data()
    # представляем бинарные данные через интерфейс файла
    img = io.BytesIO(body)
    try:
        res = plate_reader.read_text(img)
    except UnidentifiedImageError:
        return {'error': 'invalid image'}, 400

    return {"name": res}

if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    # для корректной декодировки ответа
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
