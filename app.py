from flask import Flask, jsonify, request
import cv2
import numpy as np
import csv

app = Flask(__name__)


def classify_fluorogram(image):
    """
    Функция классификации флюорограммы на негатив или позитив.

    Args:
        image: Изображение для классификации.

    Returns:
        Словарь с результатом классификации
        ('result': 'n' для негатива, 'p' для позитива).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape

    # Определяем середину нижней 1/10 части изображения
    lower_tenth_height = int(height * 9 / 10)
    lower_tenth_width_start = int(width * 2 / 6)
    lower_tenth_width_end = int(width * 4 / 6)

    lower_tenth_region = gray[
        lower_tenth_height:, lower_tenth_width_start:lower_tenth_width_end
    ]

    # Проверка черных пикселей в середине нижней 1/10 части для классификации
    mean_pixel_value = cv2.mean(lower_tenth_region)[0]
    threshold = 127

    if mean_pixel_value > threshold:
        result = 'n'  # Негатив
    else:
        result = 'p'  # Позитив

    return {'result': result}


def validate_image(file):
    """
    Функция для проверки формата изображения.

    Args:
        file: Файл изображения для проверки.

    Returns:
        True, если формат изображения допустим, иначе False.
    """
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if file and '.' in file.filename and file.filename.rsplit(
        '.', 1
    )[-1].lower() in allowed_extensions:
        return True
    return False


@app.errorhandler(400)
def bad_request(error):
    """
    Обработчик ошибки неверного запроса.

    Returns:
        JSON с сообщением об ошибке и статусом 400.
    """
    response = jsonify({'error': 'Bad Request'})
    response.status_code = 400
    return response


@app.route('/classify', methods=['POST'])
def classify_image():

    # Проверяем наличие файла изображения в запросе
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    # Проверяем формат изображения
    if not validate_image(file):
        return jsonify({'error': 'Invalid image format'}), 400

    # Изображение декодируем и классифицируем с помощью classify_fluorogram()
    try:
        image = cv2.imdecode(
            np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR
        )
        result = classify_fluorogram(image)

        # Сохраненяем результаты в CSV файл
        with open(
            'classification_results.csv', mode='a', newline=''
        ) as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(['image_id', 'type'])
            writer.writerow([file.filename, result['result']])
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
