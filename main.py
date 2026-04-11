# P4 General Conference Webscraper
# Hunter Potter, Eugene Son, Penina Strong, Erik Peterson

# Imports
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

#Database connection
engine = sqlalchemy.create_engine("postgresql://postgres:PASSWORD@localhost:5432/is303")

#Dictionary
standard_works_dict = {
    'Speaker_Name' : '', 'Talk_Name' : '', 'Kicker' : '', 'Matthew': 0, 'Mark': 0, 'Luke': 0, 'John': 0, 'Acts': 0, 'Romans': 0, '1 Corinthians': 0, '2 Corinthians': 0, 'Galatians': 0, 'Ephesians': 0, 'Philippians': 0, 'Colossians': 0, '1 Thessalonians': 0, '2 Thessalonians': 0, '1 Timothy': 0, '2 Timothy': 0, 'Titus': 0, 'Philemon': 0, 'Hebrews': 0, 'James': 0, '1 Peter': 0, '2 Peter': 0, '1 John': 0, '2 John': 0, '3 John': 0, 'Jude': 0, 'Revelation': 0, 'Genesis': 0, 'Exodus': 0, 'Leviticus': 0, 'Numbers': 0, 'Deuteronomy': 0, 'Joshua': 0, 'Judges': 0, 'Ruth': 0, '1 Samuel': 0, '2 Samuel': 0, '1 Kings': 0, '2 Kings': 0, '1 Chronicles': 0, '2 Chronicles': 0, 'Ezra': 0, 'Nehemiah': 0, 'Esther': 0, 'Job': 0, 'Psalm': 0, 'Proverbs': 0, 'Ecclesiastes': 0, 'Song of Solomon': 0, 'Isaiah': 0, 'Jeremiah': 0, 'Lamentations': 0, 'Ezekiel': 0, 'Daniel': 0, 'Hosea': 0, 'Joel': 0, 'Amos': 0, 'Obadiah': 0, 'Jonah': 0, 'Micah': 0, 'Nahum': 0, 'Habakkuk': 0, 'Zephaniah': 0, 'Haggai': 0, 'Zechariah': 0, 'Malachi': 0, '1 Nephi': 0, '2 Nephi': 0, 'Jacob': 0, 'Enos': 0, 'Jarom': 0, 'Omni': 0, 'Words of Mormon': 0, 'Mosiah': 0, 'Alma': 0, 'Helaman': 0, '3 Nephi': 0, '4 Nephi': 0, 'Mormon': 0, 'Ether': 0, 'Moroni': 0, 'Doctrine and Covenants': 0, 'Moses': 0, 'Abraham': 0, 'Joseph Smith—Matthew': 0, 'Joseph Smith—History': 0, 'Articles of Faith': 0
                       }
def get_talk_urls():
    baseURL = "https://www.churchofjesuschrist.org"
    conferenceURL = "https://www.churchofjesuschrist.org/study/general-conference/2025/10?lang=eng"
    response = requests.get(conferenceURL)
    soup = BeautifulSoup(response.text, 'html.parser')

    talkURLS = []
    # Find all links
    for url in soup.find_all("a", href=True):
        href = url['href']

        # Only grab links that look like individual talk pages
        if "/study/general-conference/2025/10/" not in href:
            continue

        # Filter out session pages (e.g. Saturday Morning Session)
        if "session" in href.lower():
            continue

        fullURL = baseURL + href

        # Avoid duplicate URLs
        if fullURL not in talkURLS:
            print(f"trying to scrape url: {fullURL}")
            talkURLS.append(fullURL)

    return talkURLS

def scrape_and_save(url_list):
    with engine.connect() as connection:
        connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS general_conference"))
        connection.commit()
    
    for url in url_list:
        print(f"trying to scrape url: {url}")

        # Load page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Create fresh dictionary for each talk
        talk_dict = standard_works_dict.copy()

        # Title
        title = soup.find("h1")
        if title:
            talk_dict["Talk_Name"] = title.text.strip()

        # Filter out the Sustaining page by checking the link text
        link_text = url.get_text()
        if "Sustaining" in talk_dict["Talk_Name"]:
            continue

        # Speaker 
        speaker = soup.find("p", class_="byline")
        if speaker:
            talk_dict["Speaker_Name"] = speaker.text.replace("By ", "").strip()


        # Kicker I hardly know her
        kicker = soup.find("p", class_= "kicker")
        if kicker:
            talk_dict["Kicker"] = kicker.text.strip()

        # Footnotes
        notes_section = soup.find("footer", class_= "notes")

        if notes_section is not None:
            notes_text = notes_section.get_text()

            for key in talk_dict:
                if key not in ["Speaker_Name", "Talk_Name", "Kicker"]:
                    talk_dict[key] = notes_text.count(key)

        # Save to DB
        df = pd.DataFrame([talk_dict])
        df.to_sql("general_conference", engine, if_exists = "append", index=False)
        
    print("You've saved the scraped data to your postgres database.") 

# User input menu
def menu():
    choice = input("If you want to scrape data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")
    if choice == '1':
        # TODO: Person 2 — call scrape_and_save(talk_urls) here
        talk_urls = get_talk_urls()
        scrape_and_save(talk_urls)
    elif choice == '2':
        choice = input("You selected to see summaries. Enter 1 to see a summary of all talks. Enter 2 to select a specific talk. Enter anything else to exit: ")
        if choice == "1":
            pass  # Person 3 — call show_all_talks_chart() here
        elif choice == '2':
            pass  # Person 4 — call show_single_talk_chart() here
        else:
            print("Closing the program.")
    else:
        print("Closing the program.")

if __name__ == "__main__":
    menu()  

    