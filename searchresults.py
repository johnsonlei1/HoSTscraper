from selectorlib import Extractor
import requests 
import json 
from time import sleep


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('search_results.yml')

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

# product_data = []
with open("search_results_urls.txt",'r') as urllist, open('search_results_output.jsonl','w') as outfile, open('urls.txt','w') as product_urls:
    for url in urllist.read().splitlines():
        data = scrape(url) 
        if data:
            for product in data['products']:
                # Try primary fields
                title = product.get('title')
                link = product.get('url')
                # Fallbacks: derive from image alt and ASIN
                if not title:
                    title = product.get('img_alt')
                if not link:
                    asin = product.get('asin')
                    if asin:
                        link = f'/dp/{asin}'
                # If still missing both, skip
                if not title or not link:
                    continue
                # Normalize relative URLs
                if isinstance(link, str) and link.startswith('/'):
                    link = 'https://www.amazon.com' + link
                # Build minimal record with only requested fields
                minimal = {
                    'title': title,
                    'url': link,
                    'asin': product.get('asin'),
                    'price': product.get('price')
                }
                print("Saving Product: %s"%title)
                json.dump(minimal,outfile)
                outfile.write("\n")
                # Append normalized URL to urls.txt for product detail scraping
                try:
                    product_urls.write(link + "\n")
                except Exception:
                    pass
                # sleep(5)
    