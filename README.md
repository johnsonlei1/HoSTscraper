thanks to selectorlib for template

amazon webscraper that scrapes products from a page of search results and scrapes each individual product from that page

Libraries needed: - selectorlib, requests

Usage:

Optional: create a virtual environment 
1. run python -m venv .venv
2. run Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
3. run .venv\Scripts\activate

in terminal run pip install -r requirements.txt
put search result page url in search_results_urls.txt
run searchresults.py
product urls will be saved to urls.txt, and general product data will be saved to search_results_output.jsonl
run amazon.py
product urls from urls.txt will be scraped, and in-depth data will be saved to output.jsonl