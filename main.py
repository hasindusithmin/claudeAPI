# import os
# import poe
import requests
from enum import Enum
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Query
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from tasks import feed_converter, parallel_fetcher
from quora import get_search_results
from GoogleNews import GoogleNews
from urllib.parse import urlparse, parse_qs

app = FastAPI(title="claudeAPI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# security = HTTPBasic()

# def check_user(credentials: HTTPBasicCredentials = Depends(security)):
#     username = credentials.username
#     password = credentials.password
#     if username == os.getenv('UNAME') and password == os.getenv('PWORD'):
#         return username
#     else:
#         raise HTTPException(status_code=401, detail="Invalid username or password")

# class Body(BaseModel):
#     prompt: str
    
class Codes(BaseModel):
    codes: List[str]


# class ChatBot(str, Enum):
#     capybara ="sage"
#     a2 ="claude"
#     chinchilla="chatgpt"
#     llama_2_7b_chat = 'Llama'
    
countries_codes = ['AR', 'AU', 'AT', 'BE', 'BR', 'CA', 'CL', 'CO', 'CZ', 'DK', 'EG', 'FI', 'FR', 'DE', 'GR', 'HK', 'HU', 'IN', 'ID', 'IE', 'IL', 'IT', 'JP', 'KE', 'MY', 'MX', 'NL', 'NZ', 'NG', 'NO', 'PE', 'PH', 'PL', 'PT', 'RO', 'RU', 'SA', 'SG', 'ZA', 'KR', 'ES', 'SE', 'CH', 'TW', 'TH', 'TR', 'UA', 'GB', 'US', 'VN']

@app.get("/")
def root():
    raise HTTPException(status_code=200)

@app.head("/")
def keep():
    raise HTTPException(status_code=200)

@app.get("/trend")
async def get_trend(code: str = Query(...)):   
    code = code.upper() 
    if code not in countries_codes:
        raise HTTPException(status_code=404)
    url = f'https://trends.google.com/trends/trendingsearches/daily/rss?geo={code}'
    res = requests.get(url)
    if res.status_code != 200:
        raise HTTPException(status_code=500)
    return feed_converter(res.text)['trends']
    
@app.post("/trends")
async def get_trends(body: Codes):
    new_codes = []
    for code in body.codes:
        code = code.upper()
        if code in countries_codes:
            new_codes.append(code)
    return parallel_fetcher(new_codes)

@app.get("/quora/{keyword}")
async def get_quora_answers(keyword: str):
    return get_search_results(keyword)

def get_link(url):
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)
    return query_parameters.get('url') or ['']

class Term(BaseModel):
    query: str
    region: str

@app.post("/hotnews")
async def get_google_news(term: Term):
    googlenews = GoogleNews(
        period='7d',
        encode='utf-8',
        lang='en',
        region=term.region
    )
    googlenews.search(term.query)
    results = googlenews.results(sort=True)
    return [{"title":result['title'],"source":result['media'],"link":get_link(result['link'])[0],"time":result['date']} for result in results]
    

# @app.post("/")
# async def reply(body:Body,user: str = Depends(check_user),engine:ChatBot = None):
#     try:
#         engine = "a2" if engine is None else engine.name
#         token = os.getenv("POE")
#         print(f'🔖🔖 {token[:10]}...')
#         client = poe.Client(token)
#         prompt = body.prompt
#         for chunk in client.send_message(engine, prompt):
#             pass
#         return chunk["text"]
#     except:
#         raise HTTPException(status_code=500,detail="Please try again later")
