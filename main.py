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

def show_all_talks_chart():
    # Displays a bar chart showing total scripture references across all talks.

    # Load data from database
    df = pd.read_sql("SELECT * FROM general_conference", engine)

    # Remove non-scripture columns
    df = df.drop(columns=["Speaker_Name", "Talk_Name", "Kicker"])

    # Sum all references across talks
    totals = df.sum()

    # Keep only books with more than 2 references
    totals = totals[totals > 2]

    # Create bar chart
    plot.figure(figsize=(12, 6))
    totals.plot(kind='bar')

    plot.title("Standard Works Referenced in General Conference")
    plot.xlabel("Standard Works Books")
    plot.ylabel("# Times Referenced")

    plot.xticks(rotation=45, ha='right')
    plot.tight_layout()
    plot.show()

#Create show single talk chart function
def show_single_talk_chart():
    df = pd.read_sql("SELECT * FROM general_conference", engine)
    #create dictionary
    num_dict = {}

    #loop through each row in database
    print("The following are the names of speakers and thier talks:")
    for row, num_rows in df.iterrows():
        print(f"{row + 1}: {num_rows["Speaker_Name"]} - {num_rows["Talk_Name"]}")
        #add display number and row index to dictionary
        num_dict[row + 1] = row

    #user input for talk they want to see and convert to integer
    talk_input = input("Please enter the number of the talk you want to see summarized:")
    talk_input = int(talk_input)

    #look up row in dictionary
    selected_row = df.loc[num_dict[talk_input]]

    #grab talk name from selected row
    talk_name = selected_row["Talk_Name"]

    #drop non scripture column from selected row
    scripture_counts = selected_row.drop(labels = ["Speaker_Name", "Talk_Name", "Kicker"])

    #only keep books with one reference
    scripture_counts = scripture_counts[scripture_counts >= 1]

    #plot bar chart
    plot.bar(scripture_counts.index, scripture_counts.values)
    plot.title(f"Standard Works Referenced in: {talk_name}")
    plot.xlabel("Standard Works Books")
    plot.ylabel("# Times Referenced")
    #rotate label so no overlap
    plot.xticks(rotation=45, ha='right')  
    #ensure nothing gets cut off
    plot.tight_layout()  
    plot.show()

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
            show_all_talks_chart()  # Person 3 — call show_all_talks_chart() here
        elif choice == '2':
            show_single_talk_chart() # Person 4 — call show_single_talk_chart() here
        else:
            print("Closing the program.")
    else:
        print("Closing the program.")

if __name__ == "__main__":
    menu()  

