import requests
import time
import random
import json
from bs4 import BeautifulSoup

# Get the abstract and introduction given a DOI
def extract_paper(url):

    # Make an HTTP request to the URL and get the HTML content
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html5lib")
    except:
        print("Invalid URL")
        return 

    # Attempt to find the abstract, otherwise print an error 
    abstract = ""
    try:
        section = soup.find("div", {"class": "abstract-content"})
        paragraphs = [p.text for p in section.find_all("p")]
        abstract = " ".join(paragraphs).replace("\n", "")
    except:
        print(f"Unable to find abstract in {url}")

    # Attempt to find the introduction, otherwise print an error 
    introduction = ""
    try:
        section = soup.find("div", {"id": "section1"})
        paragraphs = [p.text for p in section.find_all("p")]
        introduction = " ".join(paragraphs).replace("\n", "")
    except:
        print(f"Unable to find introduction in {url}")

    # Attempt to extract the date, otherwise print an error
    date = ""
    try:
        raw_date = soup.find("li", {"id": "artPubDate"}).text
        date = raw_date.split(": ")[1]
    except:
        print(f"Unable to find introduction in {url}")

    # Return the abstract and introduction along with the DOI
    return {
        "doi": url,
        "date": date,
        "abstract": abstract,
        "introduction": introduction
    }

# Extract DOIs from a webpage
def extract_dois(url):

    # Attempt to extract HTML content from the URL
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html5lib")
    except:
        print(f"Unable to get from {url}")
        return []

    # Attempt to get all links from the "Research Articles" section
    doi_list = []
    try:
        header = soup.find("h2", string="Research Articles")
        articles = header.parent
        links = articles.find_all("a", href = True)
        doi_list = [a["href"] for a in links if "doi" in a["href"]]
    except:
        print(f"Unable to find links in {url}")
        return []
    
    return doi_list

# Extract data from papers in PLOS computational biology
def main():

    # Base URL for getting monthly journal pages 
    URL = "https://journals.plos.org/ploscompbiol/issue?id=10.1371/"

    # Iterate through each volume (1-20) and issue (1-12)
    # Do this in reverse order ot get the most recent things first
    doi_list = []
    for volume in range(20, 0, -1):
        for issue in range(12, 0, -1):

            print(f"Searching volume {volume}, issue {issue}")

            # Create a list of potential URLs to check
            urls = [URL + f"issue.pcbi.v{volume:02d}.i{issue:02d}"]

            # Attempt to get the DOIs from each URL: 
            for url in urls: doi_list += extract_dois(url)

            # Pause for 1-2 seconds to stop overload
            time.sleep(1 + random.random())

    # Then, scrape the abstract and introduction from each doi
    data = []
    for i, url in enumerate(doi_list):
        data.append(extract_paper(url))

        # Print a status message and wait 1-2 seconds 
        print(f"Scraping paper {i+1}/{len(doi_list)}")
        time.sleep(1 + random.random())

    # Export the data to a json file
    with open("data/plos-cb.json", "w") as f:
        json_data = json.dumps(data, ensure_ascii = False)
        f.write(json_data)

main()


