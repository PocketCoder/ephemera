import os, sys

project_path = os.path.join(os.getcwd(), "Kokoro-82M")
sys.path.insert(0, project_path)

from models import build_model
import torch
import numpy as np
import re
from kokoro import generate_full as generate
from kokoro import normalize_text
import requests
import soundfile as sf
from bs4 import BeautifulSoup
from groq import Groq
from datetime import datetime

client = Groq()

device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = build_model("Kokoro-82M/kokoro-v0_19.pth", device)
VOICE_NAME = [
    "af",  # Default voice is a 50-50 mix of Bella & Sarah
    "af_bella",
    "af_sarah",
    "am_adam",
    "am_michael",
    "bf_emma",
    "bf_isabella",
    "bm_george",
    "bm_lewis",
    "af_nicole",
    "af_sky",
][8]
VOICEPACK = torch.load(f"Kokoro-82M/voices/{VOICE_NAME}.pt", weights_only=True).to(
    device
)
print(f"Loaded voice: {VOICE_NAME}")


def getFeaturedArticle():
    print("Getting Featured Article...", end="")
    article = soup.find(id="mp-tfa")
    content = article.find("p")
    print("Done")
    return content.get_text()


def getInTheNews():
    print("Getting In The News...", end="")
    article = soup.find(id="mp-itn")
    content_list = article.find_all("ul")
    content = content_list[0].find_all("li")
    items = []
    for i in content:
        items.append(i.get_text())
    print("Done")
    return items


def getDidYouKnow():
    print("Getting Did You Know...", end="")
    article = soup.find(id="mp-dyk")
    content_list = article.find_all("ul")
    content = content_list[0].find_all("li")
    items = []
    for i in content:
        items.append(i.get_text())
    print("Done")
    return items


def getOnThisDay():
    print("Getting On This Day...", end="")
    article = soup.find(id="mp-otd")
    content_list = article.find_all("ul")
    content = content_list[0].find_all("li")
    items = []
    for i in content:
        items.append(i.get_text())
    print("Done")
    return items


def getFeaturedImage():
    print("Getting Featured Image...")
    article = soup.find(id="mp-tfp")
    content = article.find_all("p")
    text = content[0].get_text()
    image_page_url = "https://en.wikipedia.org" + article.find("a").get("href")
    image_page = requests.get(image_page_url)
    image_soup = BeautifulSoup(image_page.content, "html.parser")
    thumbnail = image_soup.find_all("a", class_="mw-thumbnail-link")[0]
    image_url = thumbnail.get("href")
    full_url = "https:" + image_url
    print("Getting Featured Image Done")
    return [text, full_url]


def describeFeaturedImage():
    print("Describing Featured Image...")
    image = getFeaturedImage()[1]
    completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in 100 words or less.",
                    },
                    {"type": "image_url", "image_url": {"url": image}},
                ],
            }
        ],
        temperature=0.4,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    print("Image Description Done", end="\n\n")
    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


def compileBrief():
    print("Compiling Brief...")
    brief = {
        "Today's Featured Article": getFeaturedArticle(),
        "On This Day": getOnThisDay(),
        "In the News:": getInTheNews(),
        "Featured Image Text": getFeaturedImage()[0],
        "Featured Image Description": describeFeaturedImage(),
    }
    print("Brief Done", end="\n\n")
    print(brief, end="\n\n")
    return str(brief)


def generateScript(brief, url):
    print("Generating Script...", end="\n\n")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Your role is to act as an acclaimed podcast scriptwriter renowned for crafting engaging, detailed, and informative episodes. You write for ‘Ephemera,’ a daily podcast that explores the content of Wikipedia’s front page for the day. Each episode runs between 20 and 30 minutes, delivering a balanced mix of information and storytelling. Base the script entirely on the information provided in the daily Wikipedia brief. Do not invent details, speculate, or deviate from the given material. Accuracy and fidelity to the source are paramount. When covering the featured image, describe it using the exact description provided in the brief, painting a vivid picture for listeners while staying true to the source. The host, Lewis, has a calm and serious demeanor. Write in a tone that reflects his personality: clear, composed, and professional, yet engaging. Output only the words to be read by Lewis, avoiding commentary, instructions, or other non-script elements. Your goal is to craft a compelling and informative episode, ensuring every segment is both accurate and captivating.",
            },
            {"role": "user", "content": [{"type": "text", "text": brief}]},
        ],
        temperature=1,
        max_completion_tokens=3000,
        top_p=1,
        stream=False,
        stop=None,
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def generateIntro():
    intro = "Welcome. Today, we delve into the fleeting, daily ephemera that captivates the collective consciousness. We explore articles that, for this singular moment in time, stand atop the mountain of human curiosity. Join us as we dissect the zeitgeist, one entry at a time. This is 'Ephemera'."
    normalized = normalize_text(intro)
    audio, _ = generate(MODEL, intro, VOICEPACK, lang=VOICE_NAME[0], speed=0.9)
    return audio


def generateAudio(text):
    normalized = normalize_text(text)
    audio, _ = generate(MODEL, normalized, VOICEPACK, lang=VOICE_NAME[0], speed=0.9)
    return audio


def compileFile(audio, season, date, time):
    os.makedirs(f"output/{season}", exist_ok=True)
    output_filename = os.path.join(
        f"output/{season}", f"S{season}-{date}-kokoro_audio_{VOICE_NAME}-{time}.mp3"
    )
    sf.write(output_filename, audio, 24000)
    print(f"Audio saved to: {output_filename}")


if __name__ == "__main__":
    SEASON = 0
    DATE = datetime.today().strftime("%d-%m-%Y")
    URL = "https://en.wikipedia.org/w/index.php?title=Main_Page&oldid=1267837350"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    brief = compileBrief()
    script = generateScript(brief, getFeaturedImage()[1])
    audio = np.concatenate([generateIntro(), generateAudio(script)])
    TIME = datetime.now().strftime("%H%M%S")
    compileFile(audio, SEASON, DATE, TIME)
    print("Audio generation complete.")
