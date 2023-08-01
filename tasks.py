import re
import requests
import xmltodict
from concurrent.futures import ThreadPoolExecutor, as_completed

def str_to_int_with_regex(s):
    numeric_part = re.sub(r"[^\d]", "", s)
    return int(numeric_part)

def feed_converter(text):
    new_items = []
    rss_data = xmltodict.parse(text)
    channel = rss_data['rss']['channel']
    country = channel['link'][-2:]
    items = channel['item']
    for item in items:
        title = item['title']
        traffic = item.get('ht:approx_traffic')
        description = item['description']
        pubDate = item['pubDate']
        picture = item.get('ht:picture')
        new_items.append({
            "title":title,
            "traffic":str_to_int_with_regex(traffic),
            "description":description,
            "pubDate":pubDate,
            "picture":picture
        })
    return {"country":country,"trends":new_items}

def fetch(endpoint_url):
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching {endpoint_url}: {e}")
        return None
    
def parallel_fetcher(codes):
    with ThreadPoolExecutor() as executor:
        successful_results = []
        futures = [executor.submit(fetch, f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={code}") for code in codes]
        for future in as_completed(futures):
            text = future.result()
            if text is not None:
                feed_data = feed_converter(text)
                successful_results.append({"country":feed_data['country'],"trends":feed_data['trends']})
        return successful_results