import re
import requests
from urllib.parse import quote_plus
import feedparser
from datetime import datetime as dt


def sep_title_source(title, source):
    r1 = re.compile(r"(.*)\s\.\.\.\s-\s(.*)")
    r2 = re.compile(r"(.*)\s-\s(.*)")
    if match_group := r1.fullmatch(title):
        if match_group.group(2) == source:
            return match_group.group(1)
    if match_group := r2.fullmatch(title):
        if match_group.group(2) == source:
            return match_group.group(1)
    return title


def to_dt(date_string):
    return dt.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")


def oldest(items):
    datetimes = [to_dt(i["published"]) for i in items]
    return sorted(datetimes)[0].strftime("%Y-%m-%d")


def parse_rss(res_content):
    parsed = feedparser.parse(res_content)
    assert "entries" in parsed
    sources = [item["source"]["title"] for item in parsed["entries"]]
    titles = [item["title"] for item in parsed["entries"]]
    titles = [sep_title_source(t, s) for t, s in zip(titles, sources)]
    if len(parsed["entries"]) > 0:
        first_date = oldest(parsed["entries"])
    else:
        first_date = None
    return (titles, sources, first_date)


def search(searchterms, start=None, end=None):
    if start:
        searchterms += f" before:{start}"
    if end:
        searchterms += f" after:{end}"
    query = quote_plus(searchterms)
    base_url = "https://news.google.com/rss/search?ceid=UK:en&hl=en-UK&gl=UK"
    url = base_url + f"&q={query}"
    response = requests.get(url=url)
    return response


def search_loop(searchterms, n=3):
    res = search(searchterms)
    final_titles = []
    for _ in range(n):
        titles, _, first_date = parse_rss(res.content)
        final_titles.extend(titles)
        if not first_date:
            break
        res = search(searchterms, start=first_date)
    return final_titles
