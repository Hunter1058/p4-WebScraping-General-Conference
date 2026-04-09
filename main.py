# P4 General Conference Webscraper
# Hunter Potter, Eugene Son, Penina Strong, Erik Peterson

# Imports
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

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

        # Filter out the Sustaining page by checking the link text
        link_text = url.get_text()
        if "Sustaining" in link_text:
            continue

        # Avoid duplicate URLs
        if fullURL not in talkURLS:
            print(f"trying to scrape url: {fullURL}")
            talkURLS.append(fullURL)

    return talkURLS

# User input menu
def menu():
    choice = input("If you want to scrape data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")
    if choice == '1':
        # TODO: Person 2 — call scrape_and_save(talk_urls) here
        talk_urls = get_talk_urls()
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
