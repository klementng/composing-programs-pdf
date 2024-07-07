from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from requests import Response

from urls import LINKS

# FUNCTION NAME MUST START WITH 'html_process_'

def html_process_remove_nav(index, response: Response, soup: BeautifulSoup):

    for e in soup.select("[class^=nav]"):
        e.decompose()


def html_process_remove_footer(index, response: Response, soup: BeautifulSoup):

    if index == 1 or index == 0:
        return

    e = soup.find(id="contentinfo")
    if e:
        e.decompose()


def html_process_edit_padding(index, response: Response, soup: BeautifulSoup):

    tags = [".inner-content"]

    for t in tags:
        e = soup.select_one(t)
        if e:
            e["style"] = e.get("style", "") + " width:100%"


def html_process_make_links_absolute(index, response: Response, soup: BeautifulSoup):
    base_url = str(response.url)

    for elem in ["a", "link", "img", "script"]:
        for tag in soup.select(elem):

            if tag.has_attr("src"):
                tag["src"] = urljoin(base_url, tag["src"])

            if tag.has_attr("href"):
                tag["href"] = urljoin(base_url, tag["href"])
