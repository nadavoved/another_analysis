import time
from os import remove, listdir, mkdir
import bz2
from shutil import rmtree

from os.path import isfile, isdir, getsize
from zipfile import ZipFile
from pathlib import Path

from requests import get
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

DOWNLOAD_ABS_PATH = Path('driver/downloads').absolute()
DATA_PATH = Path('data')


def get_driver():
    if isdir(DOWNLOAD_ABS_PATH):
        rmtree(DOWNLOAD_ABS_PATH)
    mkdir(DOWNLOAD_ABS_PATH)
    if isfile('driver/msedgedriver.exe'):
        print('using existing web driver...')
    else:
        print('Downloading edge driver from the web...')
        dest = DOWNLOAD_ABS_PATH / 'driver_zip.zip'
        url = ('https://msedgedriver.azureedge.net/'
               '108.0.1462.54/edgedriver_win64.zip')
        res = get(url)
        with open(dest, mode='wb') as fp:
            fp.write(res.content)
        with ZipFile(dest) as fp:
            fp.extract(member='msedgedriver.exe', path='driver')
        remove(dest)
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option("prefs", {'download.default_directory':
                                                  str(DOWNLOAD_ABS_PATH)})
    return webdriver.Edge(service=Service('driver/msedgedriver.exe'),
                          options=options)


def extract_datasets(zip_folder: Path):
    with ZipFile(zip_folder) as fp:
        for member in fp.namelist():
            if not member.endswith('.bz2'):
                fp.extract(member, path=DATA_PATH)
            else:
                fp.extract(member, path=DOWNLOAD_ABS_PATH)
    remove(zip_folder)
    for path in DOWNLOAD_ABS_PATH.iterdir():
        current_src_path = path
        current_res_path = DATA_PATH / path.name[:-3]
        with bz2.open(current_src_path) as src:
            content = src.read()
        with open(current_res_path, mode='wb') as res:
            res.write(content)
        remove(current_src_path)


def press_download(driver):
    url = ('https://dataverse.harvard.edu/'
           'dataset.xhtml?persistentId=doi:10.7910/DVN/HG7NV7#')
    driver.get(url)
    download_menu_xpath = r'//*[@id="actionButtonBlock"]/' \
                          r'div[1]/div/button'
    download_button_id = "datasetForm:j_idt264"
    menu_button = driver.find_element(by=By.XPATH,
                                      value=download_menu_xpath)
    menu_button.click()
    download_button = driver.find_element(value=download_button_id)
    while not download_button.is_displayed():
        time.sleep(1)
    download_button.click()


def download_data():
    if len(listdir('data')) > 1:
        print('data already available in "data" folder.')
    else:
        driver = get_driver()
        try:
            print('no data found...downloading data...'
                  'Press ctrl+c to abort..')
            press_download(driver)
            print('downloading data zip file...(1.5GB)')
            complete_file = DOWNLOAD_ABS_PATH / 'dataverse_files.zip'
            while not listdir(DOWNLOAD_ABS_PATH):
                time.sleep(1)
            print('download stats:')
            temp_file = next(DOWNLOAD_ABS_PATH.iterdir())
            while not isfile(complete_file):
                size = getsize(temp_file)
                print(f'\r{int(size / 1024 ** 2)} MB', end='')
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nInteruppted, closing driver...')
            driver.quit()
            print('Closed the driver, download aborted')
        else:
            print('\nDownload completed. Closing the driver...')
            driver.quit()
            print('closed the driver.')
            print('extracting compressed data files...this may take a while...'
                  'don\'t close the program')
            extract_datasets(complete_file)
            print('data is now available at the "data" folder.')
        rmtree(DOWNLOAD_ABS_PATH)


if __name__ == '__main__':
    download_data()
