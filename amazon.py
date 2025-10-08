from selectorlib import Extractor
import requests 
import json 
from time import sleep
import re
import html
import unicodedata


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')

def scrape(url):  

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    return e.extract(r.text)

# --- Helpers for cleaning ---
def normalize_unicode(text):
    if not isinstance(text, str):
        return text
    # Normalize and replace common problematic characters
    text = unicodedata.normalize('NFKC', text)
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u00a0': ' ',  # nbsp
        '\u00ad': '',   # soft hyphen
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def clean_text(value):
    if not value:
        return value
    text = html.unescape(value)
    text = normalize_unicode(text)
    # Remove boilerplate phrases commonly found in Amazon content
    boilerplate_patterns = [
        r'\bSee (more )?product details\b',
        r'\bSee more\b',
        r'\bLearn more\b',
        r'\bSponsored\b',
    ]
    for pat in boilerplate_patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    # Collapse whitespace/newlines
    text = re.sub(r'[\s\u00a0]+', ' ', text, flags=re.UNICODE).strip()
    return text

def clean_price(value):
    return clean_text(value)

def clean_rating(value):
    if not value:
        return value
    value = clean_text(value)
    m = re.search(r'(\d+(?:\.\d+)?)', value)
    return m.group(1) if m else value

def clean_reviews(value):
    if not value:
        return value
    value = clean_text(value)
    m = re.search(r'([\d,]+)', value)
    return m.group(1) if m else value

def clean_description(value):
    if not value:
        return value
    # Prefer a cleaner text: strip common headers
    value = clean_text(value)
    value = re.sub(r'^About this item\s*', '', value, flags=re.IGNORECASE)
    # Remove embedded JSON/config blobs sometimes injected into description blocks
    value = re.sub(r'\{[^}]*?(isProductSummaryAvailable|isStructuredProductSummaryAvailable|"device")[^}]*\}', '', value, flags=re.IGNORECASE)
    # Collapse whitespace again after removals
    value = re.sub(r'[\s\u00a0]+', ' ', value).strip()
    return value

# product_data = []
with open("urls.txt",'r') as urllist, open('output.jsonl','w', encoding='utf-8') as outfile:
    for url in urllist.read().splitlines():
        data = scrape(url) 
        if data:
            minimal = {
                'title': clean_text(data.get('name')),
                'price': clean_price(data.get('price')),
                'rating': clean_rating(data.get('rating')),
                'number_of_reviews': clean_reviews(data.get('number_of_reviews')),
                'product_description': clean_description(data.get('product_description'))
            }
            json.dump(minimal, outfile, ensure_ascii=False)
            outfile.write("\n")
            # sleep(5)
    