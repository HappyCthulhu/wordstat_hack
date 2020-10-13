import sys

import yaml
from loguru import logger
from selenium import webdriver

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
logger_format_critical = "<green>{time:DD-MM-YY HH:mm:ss}</> | <RED><fg 255,255,255>{level}" \
                         "</></> | <cyan>{file}:{function}:{line}</> | <fg 255,255,255><RED>{message}</></>" \
                         " | <RED><fg 255,255,255>❌</></>"

logger.add(sys.stderr, format=logger_format_debug, level='DEBUG', filter=debug_only)
logger.add(sys.stderr, format=logger_format_info, level='INFO', filter=info_only)
logger.add(sys.stderr, format=logger_format_critical, level='CRITICAL', filter=critical_only)


def get_proxies_from_file():
    with open('text_files\\proxies.yml', 'r', encoding='utf-8') as proxy_file:
        proxy_list = yaml.load(proxy_file, Loader=yaml.FullLoader)
    return proxy_list


def driver_settings(proxy_list):
    proxy = proxy_list[0]
    del proxy_list[0]
    if proxy == '':
        return webdriver.Chrome()
    proxy_split = proxy.split(':')
    login_proxy = proxy_split[0]
    password_proxy = proxy_split[1]
    ip_proxy = proxy_split[2]
    port_proxy = proxy_split[3]
    options = webdriver.ChromeOptions()
    proxy_set = ip_proxy + ':' + port_proxy
    options.add_extension("Proxy_Auto_Auth.crx")
    options.add_argument("--proxy-server=http://{}".format(proxy_set))

    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get("chrome-extension://ggmdpepbjljkkkdaklfihhngmmgmpggp/options.html")

    driver.find_element_by_id("login").send_keys(login_proxy)
    driver.find_element_by_id("password").send_keys(password_proxy)
    driver.find_element_by_id("retry").clear()
    driver.find_element_by_id("retry").send_keys("2")
    driver.find_element_by_id("save").click()
    logger.debug('Прокси успешно подключен')

    return driver
