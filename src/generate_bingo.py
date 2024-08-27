import numpy as np
import pandas as pd
import shutil
import re
from bs4 import BeautifulSoup
import argparse

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects as path_effects
import textwrap

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', type=str, default='output')
parser.add_argument('-t', '--top_word', type=str, default='GIZZO')
parser.add_argument('--album_covers', action='store_true', default=True)
parser.add_argument('--no_album_covers', dest='album_covers', action='store_false')
parser.add_argument('-w', '--weight', type=str, default='hybrid', choices=['popularity', 'year', 'hybrid', 'none'])
parser.add_argument('-s', '--seed', type=int, default=None)

args = parser.parse_args()

'''
    Generates bingo card.
    -f, --filename: str. Prefix for output filename. Writes to output/.
        Default: "output".
    -t, --top_word: str. Word at the top of card. E.g. GIZZO, BINGO, etc.
        Default: "GIZZO"
    -w, --weight: str. What type of weighting to use for random selection of songs.
        'popularity': Weight songs by number of plays on YouTube Music.
        'year': Weight songs by how recently they were released (more recent songs = more likely to show up on card).
        'hybrid': Weight songs by average of popularity weight and year weight.
        'none': Each song is equally likely to appear.
    -s, --seed: int. Seed for numpy.random.
    --no_album_covers: Add this flag to not include album covers in bingo card.
        
'''

song_df = pd.read_csv('../data/song_data.csv')

def kglw_bingo(song_df, filename='output', top_word='GIZZO', album_covers=True, weight='hybrid', seed=None):
    
    np.random.seed(seed)

    album_dict = dict(zip(song_df['title'], song_df['album_display_name']))
    prefix_dict = dict(zip(song_df['title'], song_df['prefix']))
    
    if weight == 'none':
        song_selection = np.random.choice(a=song_df['title'], size=25, replace=False)
    else:
        song_selection = np.random.choice(a=song_df['title'], size=25, replace=False, p=song_df[weight + '_weight'])
    song_selection = song_selection.reshape(5, 5)

    fig = plt.figure(figsize=(12,12))
    ax = plt.gca()
    #ax.set_aspect('equal')

    line_positions = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]

    for x in line_positions:
        ax.plot([x, x], [-0.5,4.5], color='k', linewidth=2.5)
        ax.plot([-0.5,4.5], [x,x], color='k', linewidth=2.5)

    song_selection[2][2] = 'FREE SPACE'

    ax.axis('off')
    for i in range(5):
        for j in range(5):
            if (i == 2) & (j == 2):
                pass
            else:
                song_name = song_selection[i][j]
                album_name = album_dict.get(song_name)
                prefix = prefix_dict.get(song_name)
                ax.text(s='\n'.join(textwrap.wrap(song_name, 14)), x=i, y=j, color='w',
                        va='bottom', ha='center', fontsize=14, 
                        path_effects=[path_effects.withStroke(linewidth=2, foreground="k")])
                ax.text(s='\n'.join(textwrap.wrap(album_name, 16)), x=i, y=j-0.05, color='w',
                        va='top', ha='center', fontsize=10, style='italic',
                        path_effects=[path_effects.withStroke(linewidth=1, foreground="k")])
                if album_covers:
                    image = mpl.image.imread('../album_covers/' + prefix + '.jpg')   
                    imagebox = mpl.offsetbox.OffsetImage(image, zoom=0.22, alpha=0.25)
                    ab = mpl.offsetbox.AnnotationBbox(imagebox, xy=(i,j), xycoords='data', 
                                                      frameon = False, zorder=-1)
                    ax.add_artist(ab)
    if album_covers:            
        image = mpl.image.imread('../album_covers/gator.jpg')        
        imagebox = mpl.offsetbox.OffsetImage(image, zoom=0.04, alpha=1)
        ab = mpl.offsetbox.AnnotationBbox(imagebox, xy=(2,1.9), xycoords='data', 
                                                      frameon = False, zorder=-1)
        ax.add_artist(ab)

    ax.text(s='FREE SPACE', x=2, y=2.25, color='w',
                    va='center', ha='center', fontsize=14, 
                    path_effects=[path_effects.withStroke(linewidth=2, foreground="k")])

    ax.text(s=top_word[0], x=0, y=4.75, ha='center', va='center', fontsize=74, color='w',
                        path_effects=[path_effects.withStroke(linewidth=4, foreground="k")])
    ax.text(s=top_word[1], x=1, y=4.75, ha='center', va='center', fontsize=74, color='w',
                        path_effects=[path_effects.withStroke(linewidth=4, foreground="k")])
    ax.text(s=top_word[2], x=2, y=4.75, ha='center', va='center', fontsize=74, color='w',
                        path_effects=[path_effects.withStroke(linewidth=4, foreground="k")])
    ax.text(s=top_word[3], x=3, y=4.75, ha='center', va='center', fontsize=74, color='w',
                        path_effects=[path_effects.withStroke(linewidth=4, foreground="k")])
    ax.text(s=top_word[4], x=4, y=4.75, ha='center', va='center', fontsize=74, color='w',
                        path_effects=[path_effects.withStroke(linewidth=4, foreground="k")])

    ax.text(s='Generated with KGLW Bingo Generator (weighting: ' + weight + ', seed: ' + str(seed) + ')', 
            x=2, y=-0.75, fontsize=14, va='center', ha='center')
    ax.text(s='https://github.com/reeserich/king_gizz_bingo', x=2, y=-1, fontsize=14, 
            va='center', ha='center', style='italic')

    fig.savefig('../output/' + filename + '.pdf', bbox_inches='tight')

kglw_bingo(song_df, filename=args.filename, top_word=args.top_word, album_covers=args.album_covers, weight=args.weight, seed=args.seed)