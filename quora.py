import json
import requests
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

cookies = {
    'm-login': '0',
    'm-b': 's5KbuSu_iXQfoGH7d9-SXw==',
    'm-b_lax': 's5KbuSu_iXQfoGH7d9-SXw==',
    'm-b_strict': 's5KbuSu_iXQfoGH7d9-SXw==',
    'm-s': 'dLOm6bdfgxeO5qouD3F77g==',
    'm-uid': 'None',
    'm-theme': 'light',
    'm-dynamicFontSize': 'regular',
}

def fetch_data(after:int, keyword:str):
    headers = {
        'authority': 'www.quora.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.quora.com',
        'quora-broadcast-id': '',
        'quora-canary-revision': 'false',
        'quora-formkey': '6f20147365f63dc56707217f9d90519b', #**#
        'quora-page-creation-time': '',
        'quora-revision': '',
        'quora-window-id': '',
        'referer': f'https://www.quora.com/search?q={urllib.parse.quote(keyword)}&type=question',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    json_data = {
        'queryName': 'SearchResultsListQuery',
        'variables': {
            'query': keyword,
            'disableSpellCheck': None,
            'resultType': 'answer',
            'author': None,
            'time': 'all_times',
            'first': 10,
            'after': str(after),
            'tribeId': None,
        },
        'extensions': {
            'hash': 'fda0eef0da5b7595289628f166e1c163a5fec61ae157f50a258558456c749df1', #**#
        },
    }
    try:
        response = requests.post(
            'https://www.quora.com/graphql/gql_para_POST',
            params={'q': 'SearchResultsListQuery'},
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return response.json()

def get_search_results(keyword):
    with ThreadPoolExecutor(max_workers=5) as executor:
        payloads = list(executor.map(fetch_data, [0, 9, 19, 29, 39], [keyword] * 5))
        results, all_edges = [], []
        for payload in payloads:
            search_connection = payload['data']['searchConnection']
            if search_connection is not None:
                edges = search_connection['edges']
                all_edges += edges
        for edge in all_edges:
            node = edge['node']
            question = node['question']
            link = f"https://www.quora.com{question['url']}"
            preview_answer = node['previewAnswer']
            if preview_answer is None:
                continue
            # Profile Data
            author = preview_answer['author']
            names = author['names'][0]
            profile_name = f"{names['givenName']} {names['familyName']}"
            profile_url = f"https://www.quora.com{author['profileUrl']}"
            image_url = author['profileImageUrl']
            upvotes = preview_answer['numUpvotes']
            comments = preview_answer['numDisplayComments']
            shares = preview_answer['numShares']
            views = preview_answer['numViews']
            creation_time = question['creationTime']
            content = preview_answer['content']
            content = json.loads(content)
            answer = ""
            for section in content['sections']:
                answer += section['spans'][0]['text']
            id = question['id']
            slug = question['slug'].replace('-', ' ')
            slug = slug.replace('1', '').strip() if slug.endswith("1") else slug
            text = f"{slug}\n\n{answer}"
            results.append({
                "id": id,
                "link": link,
                "views": views,
                "upvotes": upvotes,
                "comments": comments,
                "shares": shares,
                "profileName": profile_name.strip(),
                "profilImage": image_url,
                "profileUrl": profile_url,
                "text": text,
                "dateTime": creation_time,
            })
        return results
