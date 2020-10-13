import os

import requests
import random as r
import base64
import json

import yaml
from loguru import logger


def get_client_key():
    with open('text_files\\my_info.yml', 'r', encoding='utf-8') as my_info:
        client_key = yaml.load(my_info, Loader=yaml.FullLoader)
        return client_key[0]


def parse_image(url):
    response = requests.get(url)

    random_count_for_file_name = r.randint(32476, 1234124)

    with open(f'captcha_pictures\\{random_count_for_file_name}.png', "wb") as f:
        f.write(response.content)

    return random_count_for_file_name


def reformatting_in_base64(pic_name):
    with open(f'captcha_pictures\\{pic_name}.png',
              "rb") as image:  # open binary file in read mode
        image_read = image.read()

    image_64_encode = base64.encodebytes(image_read)
    os.remove(f'captcha_pictures\\{pic_name}.png')
    return str(image_64_encode)


def pic_base64_format(pic_base64):
    pic_base64 = pic_base64.replace('\\n', '')
    pic_base64 = pic_base64.replace('b\'', '')
    pic_base64 = pic_base64.replace('\'', '')
    # pic_base64 = 'data:image/jpeg;base64,' + pic_base64

    return pic_base64


def pic_in_base64(url):
    image_file_name = parse_image(url)
    pic_code_in_base64 = reformatting_in_base64(image_file_name)
    return pic_base64_format(pic_code_in_base64)


def get_status(payload_get_result, headers_get_result):
    request_get_result = requests.post('https://api.anti-captcha.com/getTaskResult',
                                       data=json.dumps(payload_get_result), headers=headers_get_result)
    response_get_result = request_get_result.text
    response_get_result_dic = json.loads(
        response_get_result.replace("'", '"'))  # переводим строку в json, чтоб сделать словарем
    if response_get_result_dic['errorId'] != 0:
        logger.debug('Ошибка антикапчи')
    if response_get_result_dic['status'] == 'processing':
        logger.debug('Обрабатывается...')
        return None
    elif response_get_result_dic['status'] == 'ready':
        return response_get_result_dic


def send_captcha_answer(captcha_code, driver):
    logger.debug(f'Расшифровка капчи: {captcha_code}')
    driver.find_element_by_css_selector('.input-wrapper__content').send_keys(captcha_code)
    driver.find_element_by_css_selector('.submit').click()


def resolve_captcha(url, driver):
    captcha_base64 = pic_in_base64(url)
    client_key = get_client_key()
    payload_create_task = {
        'clientKey': f'{client_key}',
        'languagePool': 'rn',
        'task': {
            'type': 'ImageToTextTask',
            'body': f'{captcha_base64}',
        }}
    headers = {'content-type': 'application/json'}
    # print(payload_create_task)
    request_to_anticaptcha = requests.post('https://api.anti-captcha.com/createTask',
                                           data=json.dumps(payload_create_task), headers=headers)
    response = request_to_anticaptcha.text
    response_dic = json.loads(response.replace("'", '"'))  # переводим строку в json, чтоб сделать словарем
    task_id = response_dic['taskId']

    payload_get_result = {
        'clientKey': f'{client_key}',
        'taskId': f'{task_id}',
    }
    headers_get_result = {'content-type': 'application/json'}
    while get_status(payload_get_result, headers_get_result) is None:
        continue
    response_get_result_dic = get_status(payload_get_result, headers_get_result)
    captcha_code = response_get_result_dic['solution']['text']
    logger.debug(f'Расшифровка капчи: {captcha_code}')
    send_captcha_answer(captcha_code, driver)
