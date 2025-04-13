from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Настройка Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")

path_to_driver = "/Users/macbookpro/Downloads/chromedriver-mac-arm64/chromedriver"
page_link = "http://pogoda-service.ru/archive_gsod.php"


def get_station_codes(country):
    service = Service(path_to_driver)

    # Инициализация драйвера
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Открываем страницу
        driver.get(page_link)

        # Ожидаем первый выпадающий список
        first_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "country"))
        )

        # Выбираем страну
        select_country = Select(first_dropdown)
        select_country.select_by_visible_text(country)

        # Ожидаем второй выпадающий список
        second_dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "station"))
        )

        # Дополнительное ожидание для обновления списка
        WebDriverWait(driver, 20).until(
            lambda driver: len(driver.find_elements(By.XPATH, "//select[@id='station']/option")) > 1
        )

        # Извлекаем опции
        options = second_dropdown.find_elements(By.TAG_NAME, 'option')

        stations = {}
        # Печатаем опции
        for option in options:
            station = option.text.strip()
            code = option.get_attribute('value').strip()
            stations[station] = code
        return stations

    finally:
        driver.quit()
