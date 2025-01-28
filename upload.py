from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def upload_podcast(title, description, audio_file):
    driver = webdriver.Firefox()
    driver.get(
        "https://app.redcircle.com/shows/cc3aa3f2-8c37-47e5-a0bc-89dd0e19e887/ep/create"
    )
    assert "Ephemera" in driver.title

    title_elem = driver.find_element(By.NAME, "title")
    title_elem.clear()
    title_elem.send_keys(title)

    description_elem = driver.find_element(By.XPATH, "//div[@class='ql-editor']")
    description_elem.clear()
    description_elem.send_keys(description)

    audio_elem = driver.find_element(By.XPATH, "//div[@class='audio-drop-zone']")
    ActionChains(driver).move_to_element(audio_elem).click().perform()


if __name__ == "__main__":
    upload_podcast(
        "Test", "Test", "output/0/S0-26-01-2025-kokoro_audio_bm_lewis-021423.mp3"
    )
