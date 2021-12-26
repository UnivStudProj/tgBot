import requests, json
import logging
from bs4 import BeautifulSoup
from config import top100_url

logging.basicConfig(filename="sample.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
top100_src = requests.get(top100_url).text
soup = BeautifulSoup(top100_src, 'lxml')
tracks_data = {}

# Finding block with tracks
for match in soup.find_all('div', class_='module-layout'):
    try:
        if match.ul['data-id'] == '11818':
            num = 1
            # Adding tracks data to the dictionary
            for track in match.find_all('li', class_='item'):
                track_id = num
                tracks_data[track_id] = {
                    'artist' : f"{track['data-artist']}".replace("'", "''"),
                    'title' : f"{track['data-title']}".replace("(Топ 100 лучших русских песен 2021)", "").replace("'", "''"),
                    }
                num += 1
    # Skipping not needed blocks
    except KeyError:
        pass
# Dumping to a .json file
with open('top100.json', 'w') as f:
    json.dump(tracks_data, f, indent=2)  
