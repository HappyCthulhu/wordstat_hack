import os
import sys
import time
import yaml
import random as r

from loguru import logger
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from py_files.settings import get_proxies_from_file, driver_settings
from py_files.resolve_captcha import resolve_captcha

logger.remove()


# настраиваем логгирование

def debug_only(record):
    return record["level"].name == "DEBUG"


def critical_only(record):
    return record["level"].name == "CRITICAL"


def info_only(record):
    return record["level"].name == "INFO"


logger_format_debug = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><blue>{level}</></> | " \
                      "<cyan>{file}:{function}:{line}</> | <blue>{message}</> | <blue>🛠</>"
logger_format_info = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><fg 255,255,255>{level}</></> | " \
                     "<cyan>{file}:{function}:{line}</> | <fg 255,255,255>{message}</> | <fg 255,255,255>✔</>"
logger_format_critical = "<green>{time:DD-MM-YY HH:mm:ss}</> | <RED><fg 255,255,255>{level}</></> " \
                         "| <cyan>{file}:{function}:{line}</> | <fg 255,255,255><RED>{message}</></> | " \
                         "<RED><fg 255,255,255>❌</></>"

logger.add(sys.stderr, format=logger_format_debug, level='DEBUG', filter=debug_only)
logger.add(sys.stderr, format=logger_format_info, level='INFO', filter=info_only)
logger.add(sys.stderr, format=logger_format_critical, level='CRITICAL', filter=critical_only)


# logger.add('file.txt')

def ip_check():
    driver.get('https://2ip.ru/')
    ip = driver.find_element_by_xpath('//div[@class="ip"]/span').text
    logger.debug(f'Ваш прокси: {ip}')
    return ip


def request_appointment(request_list):
    request = request_list[0]
    del request_list[0]
    logger.debug(f'Назначили запрос: {request}')
    return request, request_list


def email_appointment(emails_list):
    email_login_pass = emails_list[0]
    email_login_pass_list = email_login_pass.split(':')
    del emails_list[0]
    email_login = email_login_pass_list[0]
    email_pass = email_login_pass_list[1]
    logger.debug(f'Взяли почту: {email_login}')
    return email_login, email_pass, emails_list


# def input_func():
#     logger.debug('Ниже введите желаемое количество запросов')
#     count = int(input())
#     logger.debug('Ниже введите желаемый ключ поиска')
#     search_key = input()
#     logger.debug('Ниже введите комментарий')
#     comment = input()
#
#     return count, search_key, comment

def authorization_in_yandex(email_login, email_pass):
    driver.get('https://passport.yandex.ru/auth')
    WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#passp-field-login')))
    driver.find_element_by_css_selector('#passp-field-login').send_keys(email_login)
    driver.find_element_by_css_selector('[type="submit"]').click()
    WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#passp-field-passwd')))
    driver.find_element_by_css_selector('#passp-field-passwd').send_keys(email_pass)
    driver.find_element_by_css_selector('[type="submit"]').click()
    time.sleep(2)
    logger.debug('Залогинились в Яндекс.Почте')
    return email_login


def search(stop_count, search_key):
    logger.debug('Начинаем отправлять запросы')
    start_time = datetime.now()
    count_now = 0
    while stop_count > count_now:
        driver.get(f'https://yandex.ru/search/?text={search_key}&lr=2')
        while 'showcaptcha' in driver.current_url:
            logger.debug('Вылезла капча')
            captcha_image_link = driver.find_element_by_css_selector('.captcha__image [src]').get_attribute('src')
            resolve_captcha(captcha_image_link, driver)
            if 'showcaptcha' in driver.current_url:
                logger.info('Капча решена неправильно, пробуем еще раз')
                continue
        count_now += 1
        with open('.' + os.path.join(os.sep, 'text_files', 'report.txt'), 'a', encoding='utf-8-sig') as report_file:
            report_file.write(f'\ndate,time: {datetime.now()}, IP: {ip}, search key: {search_key}, '
                              f'count: {count_now}/{stop_count}')
        logger.debug(f'Разослано запросов по ключу "{search_key}": {count_now}/{stop_count}')
        pause = r.randint(4, 10)
        logger.debug(f'Длительность паузы в секундах: {pause}')
        time.sleep(pause)
    report_file.close()
    end_time = datetime.now()
    logger.info(
        f'Работа успешно завершена. Осталось {len(request_list)} ключей поиска. '
        f'Результаты можете посмотреть в report.txt и final_report.txt')
    return count_now, start_time, end_time


# запускаем основной скрипт

proxy_list = get_proxies_from_file()


with open('.' + os.path.join(os.sep, 'text_files', 'emails.yml'), 'r', encoding='utf-8-sig') as emails_file:
    emails_list = yaml.load(emails_file, Loader=yaml.FullLoader)
logger.debug('Распаковали email.yml')

with open('.' + os.path.join(os.sep, 'text_files', 'requests.yml'), 'r', encoding='utf-8-sig') as request_file:
    request_list = yaml.load(request_file, Loader=yaml.FullLoader)
logger.debug('Распаковали requests.yml')

# запускаем цикл драйвера (смена ключей поиска и проксей по списку)

for i in range(len(request_list)):
    driver = driver_settings(proxy_list)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })

    ip = ip_check()
    # count, search_key, comment = input_func()
    search_key, request_list = request_appointment(request_list)
    email_login, email_pass, emails_list = email_appointment(emails_list)
    count = r.randint(89, 150)
    logger.info(f'Будет сделано запросов: {count}')
    driver.delete_all_cookies()
    authorization_in_yandex(email_login, email_pass)
    request_count, start_time, end_time = search(count, search_key)
    wasted_time = end_time - start_time
    with open('.' + os.path.join(os.sep, 'text_files', 'report.txt'), 'a', encoding='utf-8-sig') as final_report:
        final_report.write(
            f'\ndate,time:{datetime.now()}| wasted time:{wasted_time}| IP:{ip}| search key:{search_key}| '
            f'number of requests:{request_count}| email:{email_login}')
    driver.quit()
