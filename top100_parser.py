import requests, json
import logging
from bs4 import BeautifulSoup
from config import top100_url

logging.basicConfig(filename="sample.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
top100_src = requests.get(top100_url).text
soup = BeautifulSoup(top100_src, 'lxml')
tracks_data = {}

for match in soup.find_all('div', class_='module-layout'):
    try:
        if match.ul['data-id'] == '11818':
            num = 1
            for track in match.find_all('li', class_='item'):
                track_id = num
                img = track.div.div.img['data-src']
                img_id = img[img.index('s/') + 2: img.index('_')]
                tracks_data[track_id] = {
                    'artist' : f"{track['data-artist']}".replace("'", "''"),
                    'title' : f"{track['data-title']}".replace("'", "''"),
                    'img_url' : f"https://wwv.zvuch.com/img/collections/{img_id}_small.jpg"
                    }
                num += 1
    except KeyError:
        pass
    
with open('top100.json', 'w') as f:
    json.dump(tracks_data, f, indent=2)  
