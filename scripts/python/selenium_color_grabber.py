import json
import sys
import os
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
from config import get_config


CONFIG = get_config()
PATH_DIR = CONFIG["filePath"]["local"]["test_dir"]
PATH = CONFIG["filePath"]["local"]["tests"]
#PATH = CONFIG["filePath"]["local"]["tests"] + os.listdir(PATH_DIR)[2] if (len(sys.argv) <= 1) else CONFIG["filePath"]
STOUT = CONFIG["filePath"]["local"]["stouts"]
FILE_PATH = CONFIG["filePath"]["local"]["files"]
IMAGE_PATH = CONFIG["filePath"]["local"]["images"]
COORDS = CONFIG["fileName"]["coords"]
#TODO USE MAPS()
#if file exists don't write
BACKGROUND = "(//*/a/img[contains(@src,'logo')]/parent::a/parent::*/parent::*  | //*/a/img//following::*/a/img/parent::a/parent::*/parent::*)"
#BACKGROUND = "(//*/a/img[contains(@src,'logo')] | //*/a/img//following::*/a/img)"
# Grabs the first image then grabs td with text
FONT = "//td/a/img//following::td[contains(@style,'font-size') and contains(@style,'line-height') and contains(@style,'font-weight')]"
BUTTON = "//a[contains(@style,'border-radius')]"
coordinates_json = {
    "modeType": {
        "light": {
        },
        "dark": {
        }
    }
}
COLOR_MODES = coordinates_json["modeType"].keys()
chromedriver_autoinstaller.install()

class SeleniumListener(AbstractEventListener):
    def __init__(self):
        self.obj = {}
    def after_click(self, element, driver):
        x = driver.get_window_position().get('x')
        #print(recognize_color(r,g,b) + ' ' + rgb_to_hex(r,g,b))
    def after_navigate_to(self, url, driver):
        print("After navigate to %s" % url)
    def get_test(self):
        return self.obj

def run_chrome_driver(mode, file):
    #Chrome Configs for each mode we'll want to run on all files
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("detach", True)
    chrome_driver = webdriver.Chrome(options=chrome_options)
    seleniumObj = SeleniumListener()
    ef_driver = EventFiringWebDriver(chrome_driver, seleniumObj)
    ef_driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": mode}]}) 
    ef_driver.get(PATH + file)
    return ef_driver

def build_coords(driver, mode):
    global coordinates_json
    try:
        coordinates_json["modeType"][mode]["backgroundColor"] = driver.find_element(By.XPATH, BACKGROUND).location
        x, y = driver.find_element(By.XPATH, BUTTON).location.values()
        height, width = driver.find_element(By.XPATH, FONT).size.values()
        coordinates_json["modeType"][mode]["font"] = {"x": x,"y": y,"width": width,"height": height}
        coordinates_json["modeType"][mode]["buttonBackground"] =  driver.find_element(By.XPATH, BUTTON).location
        #print(coordinates_json)
    
    except Exception as e:
        print(e)
        return "ERROR"

def save_screenshot(driver, path):
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element(By.XPATH, '/html/body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])

def get_snapshot_coords():
    try:
        #we need another for loop i believe colors AND files
        for val in os.listdir(PATH_DIR):
            if(val != '.DS_Store'):
                print(val)
                for color in COLOR_MODES:   
                    driver = run_chrome_driver(color, val)
                    build_coords(driver, color)
                    #WE'll Need the name here to save to
                    save_screenshot(driver, f'{IMAGE_PATH}{color}_{val[:-4]}png')
                    driver.quit()
                file = open(f"{STOUT}{val[:-5]}{COORDS}", "w")
                json.dump(coordinates_json, file)
                file.close()
        print("FINISHED SELENIUM COLOR GRABBER")

    except Exception as e:
        print("get_snapshot_coords ERROR")
        return "ERROR"
