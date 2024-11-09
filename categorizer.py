import os
import time
import json
import groq
from groq import Groq

# Get the groq API key from the environment
CLIENT = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Load the prompt.txt text file
with open("prompt.txt", "r") as f:
    PROMPT = f.read()

# Load the dataset of abstracts and introductions
with open("data/plos-cb.json", "r") as f:
    DATA = json.loads(f.read())


# Analyze a paper and return the results as a dictionary 
def analyze_paper(paper, log = False):

    completion = CLIENT.chat.completions.create(
        messages = [
            {"role": "system", "content": "You are a researcher."},
            {"role": "user", "content": PROMPT},
            {"role": "user", "content": paper["abstract"]},
            {"role": "user", "content": paper["introduction"]},
            {"role": "assistant", "content": ""}
        ],
        response_format = {"type": "json_object"},
        model = "llama-3.2-90b-text-preview",
        temperature = 0,
    )

    result = json.loads(completion.choices[0].message.content)
    result["doi"] = paper["doi"]
    result["date"] = paper["date"]
    return result


# Run categorizations until you get rate limited 
def main():

    with open("data/plos-cb-categorized.json", "r") as f:
        CATEGORIZED = json.loads(f.read())

    # Get the first incomplete job
    start = len(CATEGORIZED)
    errors = 3
    i, results = 0, []

    # Categorize until we get 500 papers or rate limited
    while start + i < 500:
        print(f"Categorizing paper {start + i + 1}")

        # Catch exceptions here
        # I should add better error handling but its pretty reliable
        try:
            sentences = analyze_paper(DATA[start + i])
        except Exception as e:
            print(e)
            break

        results.append(sentences)
        i += 1

    # Save the results to plos-cb-categorized.json
    with open("data/plos-cb-categorized.json", "w") as f:
        payload = json.dumps(CATEGORIZED + results)
        f.write(payload)

main()
