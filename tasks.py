import re
import requests
import xmltodict
from concurrent.futures import ThreadPoolExecutor, as_completed

codes_by_countries = {
    'AR': 'Argentina',
    'AU': 'Australia',
    'AT': 'Austria',
    'BE': 'Belgium',
    'BR': 'Brazil',
    'CA': 'Canada',
    'CL': 'Chile',
    'CO': 'Colombia',
    'CZ': 'Czechia',
    'DK': 'Denmark',
    'EG': 'Egypt',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'GR': 'Greece',
    'HK': 'Hong Kong',
    'HU': 'Hungary',
    'IN': 'India',
    'ID': 'Indonesia',
    'IE': 'Ireland',
    'IL': 'Israel',
    'IT': 'Italy',
    'JP': 'Japan',
    'KE': 'Kenya',
    'MY': 'Malaysia',
    'MX': 'Mexico',
    'NL': 'Netherlands',
    'NZ': 'New Zealand',
    'NG': 'Nigeria',
    'NO': 'Norway',
    'PE': 'Peru',
    'PH': 'Philippines',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'RU': 'Russia',
    'SA': 'Saudi Arabia',
    'SG': 'Singapore',
    'ZA': 'South Africa',
    'KR': 'South Korea',
    'ES': 'Spain',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'TW': 'Taiwan',
    'TH': 'Thailand',
    'TR': 'Türkiye',
    'UA': 'Ukraine',
    'GB': 'United Kingdom',
    'US': 'United States',
    'VN': 'Vietnam'
}

codes_by_flags = {
    'AR': '🇦🇷',
    'AU': '🇦🇺',
    'AT': '🇦🇹',
    'BE': '🇧🇪',
    'BR': '🇧🇷',
    'CA': '🇨🇦',
    'CL': '🇨🇱',
    'CO': '🇨🇴',
    'CZ': '🇨🇿',
    'DK': '🇩🇰',
    'EG': '🇪🇬',
    'FI': '🇫🇮',
    'FR': '🇫🇷',
    'DE': '🇩🇪',
    'GR': '🇬🇷',
    'HK': '🇭🇰',
    'HU': '🇭🇺',
    'IN': '🇮🇳',
    'ID': '🇮🇩',
    'IE': '🇮🇪',
    'IL': '🇮🇱',
    'IT': '🇮🇹',
    'JP': '🇯🇵',
    'KE': '🇰🇪',
    'MY': '🇲🇾',
    'MX': '🇲🇽',
    'NL': '🇳🇱',
    'NZ': '🇳🇿',
    'NG': '🇳🇬',
    'NO': '🇳🇴',
    'PE': '🇵🇪',
    'PH': '🇵🇭',
    'PL': '🇵🇱',
    'PT': '🇵🇹',
    'RO': '🇷🇴',
    'RU': '🇷🇺',
    'SA': '🇸🇦',
    'SG': '🇸🇬',
    'ZA': '🇿🇦',
    'KR': '🇰🇷',
    'ES': '🇪🇸',
    'SE': '🇸🇪',
    'CH': '🇨🇭',
    'TW': '🇹🇼',
    'TH': '🇹🇭',
    'TR': '🇹🇷',
    'UA': '🇺🇦',
    'GB': '🇬🇧',
    'US': '🇺🇸',
    'VN': '🇻🇳'
}

def str_to_int_with_regex(s):
    numeric_part = re.sub(r"[^\d]", "", s)
    return int(numeric_part)

def feed_converter(text):
    new_items = []
    rss_data = xmltodict.parse(text)
    channel = rss_data['rss']['channel']
    code = channel['link'][-2:]
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
    return {"country":codes_by_countries[code], "trends":new_items, "flag": codes_by_flags[code]}

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