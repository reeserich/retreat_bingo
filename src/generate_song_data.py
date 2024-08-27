import numpy as np
import pandas as pd
import shutil
import re
from bs4 import BeautifulSoup

'''
    For generating song data from collected .htm files from YouTube Music.
    Data collected: August 12, 2024
'''

album_data = pd.read_csv('../data/album_data.csv', encoding='latin')

def process_album_data(filename):
    html_file = open(filename, "r", encoding='utf-8')
    soup = BeautifulSoup(html_file, 'lxml') 
    html_file.close()
    song_objects = soup.find_all('yt-formatted-string', 
              {'class':"title style-scope ytmusic-responsive-list-item-renderer complex-string"})
    play_objects = soup.find_all('yt-formatted-string', 
              {'class':"flex-column style-scope ytmusic-responsive-list-item-renderer"})
    titles = [song_object['title'] for song_object in song_objects]
    plays = [song_object['title'] for song_object in play_objects]
    plays = [num_plays(play) for play in plays]
    result_df = pd.DataFrame({'title':titles, 'plays':plays})
    return result_df

def num_plays(play_str):
    play_str = play_str.split(' plays')[0]
    if play_str[-1] == 'K':
        mult = 1_000
    elif play_str[-1] == 'M':
        mult = 1_000_000
    else:
        mult = 1
    play_str = re.sub("[^0-9.]", "", play_str)
    return float(play_str)*mult

collect = []
for index, row in album_data.iterrows():
    # get song data
    prefix = row['prefix']
    display_name = row['full album']
    year = row['Year']
    
    result_df = process_album_data('../data/' + prefix + '.htm')
    result_df['prefix'] = prefix
    result_df['album_display_name'] = display_name
    result_df['year'] = year
    collect.append(result_df)
    
    # get album cover
    shutil.copy('../data/' + prefix + '_files/unnamed.jpg', '../album_covers/' + prefix + '.jpg')
    
song_df = pd.concat(collect)
song_df = song_df[~song_df['title'].str.contains('(Extended Mix)')].copy()
song_df['year_weight'] = 1/(2025 - song_df['year'])

song_df['year_weight'] = 1/(2025 - song_df['year'])
song_df['year_weight'] = song_df['year_weight']/np.sum(song_df['year_weight'])
song_df['popularity_weight'] = song_df['plays']
song_df['popularity_weight'] = song_df['popularity_weight']/np.sum(song_df['popularity_weight'])
song_df['hybrid_weight'] = (song_df['popularity_weight'] + song_df['year_weight']) / 2

song_df.to_csv('../data/song_data.csv', index=False)