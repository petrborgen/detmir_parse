from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
import csv


firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
firefoxOptions.add_argument("--disable-infobars")
firefoxOptions.add_argument("start-maximized")
firefoxOptions.add_argument("--disable-extensions")


# Находим на каждой странице каталога карточки товаров, собираем информацию, записываем в файл
def product_parser(catalog_url, city, driver):
    link_xpath = '//a[contains(@href,"https://www.detmir.ru/product/index/id")' \
                 '][not(child::div//div[text()="Нет в наличии"])]'
    price_xpath = '/descendant::p[contains(text(), "₽")])[1]'
    price2_xpath = '/descendant::p[contains(text(), "₽")]/following-sibling::p/span'
    name_xpath = '/div/div/div/div/following-sibling::div/p'
    page_num = 1
    elements_all = []
    result_all = []

    print(f'\n- {city} -')
    while True:
        page_link = catalog_url + '/page/' + str(page_num)
        driver.get(page_link)
        availability = driver.find_elements(By.XPATH, link_xpath)

        if availability:
            driver.get(catalog_url)
            elements = driver.find_elements(By.XPATH, link_xpath)
            elements = list(set(elements) - set(elements_all))
            elements_all += elements

            for element in elements:
                product_link = element.get_attribute("href")
                product_id = product_link.rpartition('id/')[2][:-2]
                product_name = driver.find_elements(By.XPATH, f'//a[@href="{product_link}"]{name_xpath}')[0]\
                    .get_attribute("textContent")
                product_price = driver.find_elements(By.XPATH, f'//a[@href="{product_link}"]{price2_xpath}')
                if product_price:
                    price_promo = driver.find_elements(By.XPATH, f'(//a[@href="{product_link}"]{price_xpath}')[0]\
                        .get_attribute("textContent")[:-2]

                    product_price = product_price[0].get_attribute("textContent")[:-2]
                else:
                    product_price = driver.find_elements(By.XPATH, f'(//a[@href="{product_link}"]{price_xpath}')[0]\
                        .get_attribute("textContent")[:-2]
                    price_promo = ''

                result = [product_id, product_name, product_price, price_promo, product_link]
                result_all.append(result)
        else:
            break
        print(f'* страница {page_num} обработана')
        page_num += 1

    while True:
        try:
            with open(city + '_report.csv', 'w', newline='', encoding='utf-8') as csv_report:
                writer = csv.writer(csv_report)
                writer.writerow(['id', 'title', 'price', 'promo_price', 'url'])
                writer.writerows(result_all)
        except PermissionError:
            input('! Закрой, пожалуйся, файлы отчётов !')
        break
    print(f' Сохранено {len(elements_all)} позиций \n')


# Находим выыбор региона, щёлкаем по нужному городу и запускаем парсер
def city_switch(catalog_url):
    city_xpath = '''//*[name()="use" and @*="/img/f08f0e1c60833962c3a528b16b93f14d.svg#pin"]
                 /../../following-sibling::span'''
    mos_xpath = '(//div[text()="Продаем и доставляем товары в регионах:"]/../ul/li[1])[1]'
    spb_xpath = '(//div[text()="Продаем и доставляем товары в регионах:"]/../ul/li[2])[1]'
    cities = {'mos': mos_xpath, 'spb': spb_xpath}

    for city in cities.items():
        with webdriver.Firefox(executable_path='geckodriver', options=firefoxOptions) as driver:
            driver.implicitly_wait(1)
            try:
                driver.get(catalog_url)
            except WebDriverException:
                input('\n Что-то с соединением или драйвером ')
                quit()
            else:
                driver.find_element(By.XPATH, city_xpath).click()
                driver.find_element(By.XPATH, city[1]).click()
                product_parser(catalog_url, city[0], driver)
    input(' Отчёты сформированы ')
    quit()


if __name__ == '__main__':
    print('\n Скрипт запущен ')
    city_switch(catalog_url='https://www.detmir.ru/catalog/index/name/zdorovyj_perekus_pp')
