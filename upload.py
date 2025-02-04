from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.timeouts import Timeouts

import os


def upload_podcast(title, description, audio_file, season):
    options = Options()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)

    driver.get(
        "https://app.redcircle.com/shows/cc3aa3f2-8c37-47e5-a0bc-89dd0e19e887/ep/create"
    )

    if "Sign In" in driver.title:
        print("Logging in...", end="\n\n")
        log_in(driver)

    wait = WebDriverWait(driver, 10)
    title_elem = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='text'][@name='title']")
        )
    )
    title_elem.clear()
    title_elem.send_keys(title)

    description_elem = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div[3]/div/div[2]/div/div[1]/div/div/div[2]/div/form/div/div/div/div[2]/div[3]/div/div/div[2]/div[1]",
            )
        )
    )
    description_elem.click()
    description_elem.send_keys(description)

    audio_elem = driver.find_element(
        By.XPATH,
        "//div[contains(concat(' ',normalize-space(@class),' '),' audio-drop-zone-content ')]/input[@type='file']",
    )

    file_path = os.path.abspath(audio_file)
    audio_elem.send_keys(file_path)

    more_options_elem = driver.find_element(By.CSS_SELECTOR, ".form-dropdown-wrapper")
    more_options_elem.click()

    lst = os.listdir("output/0/")
    episode_number = len(lst) - 1

    episode_number_elem = driver.find_element(By.NAME, "episodeNumber")
    episode_number_elem.clear()
    episode_number_elem.send_keys(episode_number)

    season_number_elem = driver.find_element(By.NAME, "season")
    season_number_elem.clear()
    season_number_elem.send_keys(season + 1)

    submit_button = driver.find_element(
        By.XPATH,
        "/html/body/div[3]/div/div[2]/div/div[1]/div/div/div[3]/div/button[2]",
    )
    submit_button.click()
    driver.quit()


def log_in(driver):
    email_elem = driver.find_element(By.NAME, "email")
    email_elem.clear()
    email = os.environ.get("EMAIL")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.NAME, "password")
    password_elem.clear()
    password = os.environ.get("PASSWORD")
    password_elem.send_keys(password)

    ActionChains(driver).move_to_element(
        driver.find_element(By.XPATH, "//button[@type='submit']")
    ).click().perform()


if __name__ == "__main__":
    os.environ.set("EMAIL", "jollies.puffin-0o@icloud.com")
    os.environ.set("PASSWORD", "honCi9-pakfes-dicvow")
    upload_podcast(
        "Test", "Test", "output/0/S0-26-01-2025-kokoro_audio_bm_lewis-021423.mp3"
    )
