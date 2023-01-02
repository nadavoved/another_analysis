import time
from os import remove

from os.path import isfile, abspath
from zipfile import ZipFile

from requests import get
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

DRIVER_PATH = 'driver/msedgedriver.exe'
DOWNLOAD_ABS_PATH = abspath('driver/downloads/')


def get_driver():
    if isfile(DRIVER_PATH):
        print('using existing edge driver...')
    else:
        print('Downloading edge driver from the web...')
        dest = DOWNLOAD_ABS_PATH + 'driver_zip.zip'
        url = ('https://msedgedriver.azureedge.net/'
               '108.0.1462.54/edgedriver_win64.zip')
        res = get(url)
        with open(dest, mode='wb') as fp:
            fp.write(res.content)
        with ZipFile(dest) as fp:
            fp.extract(member='msedgedriver.exe', path='driver')
        remove(dest)


def download_data():
    url = ('https://dataverse.harvard.edu/'
           'dataset.xhtml?persistentId=doi:10.7910/DVN/HG7NV7#')
    download_menu_xpath = r'//*[@id="actionButtonBlock"]/div[1]/div/button'
    download_button_id = "datasetForm:j_idt264"

    options = Options()
    # options.add_argument('--headless')

    options.add_experimental_option("prefs", {'download.default_directory': DOWNLOAD_ABS_PATH})
    driver = webdriver.Edge(service=Service(DRIVER_PATH), options=options)

    # driver.get(url)
    time.sleep(1000)
    """"
    menu_button = driver.find_element(by=By.XPATH, value=download_menu_xpath)
    menu_button.click()
    download_button = driver.find_element(value=download_button_id)
    while not download_button.is_displayed():
        time.sleep(1)
    download_button.click()
    while not isfile('D:/dataverse_files.zip'):
        time.sleep(5)
    """


if __name__ == '__main__':
    download_data()
