from __future__ import unicode_literals
import youtube_dl
import requests
from bs4 import BeautifulSoup

options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
}

def hasLink(h3):
    h3_class = h3.get('class')
    if h3_class and h3_class[0] == 'yt-lockup-title':
        if h3.a.get("href").startswith('/watch'):
            return True
    return False

def getVids():
    with open("vids.txt", "r") as vidFile:
        vid_names = vidFile.read().splitlines()
    urls = []
    for vid_name in vid_names:
        payload = {'search_query': vid_name}
        resp = requests.get("https://www.youtube.com/results", params=payload)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            headers = soup.find_all('h3')
            links = [h3.a.get("href") for h3 in headers if hasLink(h3)]
            # for now, just use first result
            urls += [links[0]]
    
    youtube = youtube_dl.YoutubeDL(options)
    for url in urls:
        youtube.download(['http://www.youtube.com' + url])

    open("vids.txt", "w").close()


if __name__ == '__main__':
    getVids()