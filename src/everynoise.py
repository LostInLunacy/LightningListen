"""
    Module for scraping new releases track data from everynoise.com
"""

# Local
from track import Track

# Other
from bs4 import BeautifulSoup
import os
import pickle
import requests
from tqdm import tqdm
from typing import List
import util


URL_MAIN = 'https://everynoise.com/new_releases_by_genre.cgi?'


class SearchOptions(dict):
    """
    Class for getting search options on everynoise.com/new_releases_by_genre page
    """

    FN_SEARCH_OPTIONS = '../data/everynoise_nr_searchoptions.pkl'

    def __init__(self):
        search_options = self._get_search_options()
        super().__init__(**search_options)
        self.save()

    def _get_search_options(self) -> dict:
        """ 
        Scrape search options for everynoise.com's new releases page 
        """
        response = requests.get(URL_MAIN)
        soup = BeautifulSoup(response.text, 'lxml')
        select_tags = soup.find_all('select')

        # Get regions, dates, etc.
        initial_result = {i.get('name'): [j.get('value') for j in i.find_all('option')] for i in select_tags}

        # Get genres
        genres = [i.text for i in soup.find_all('div', attrs={'class': 'genre', 'title': True})] + ['anygenre']

        combined_results = initial_result | {'genres': genres}
        return combined_results

    """
    ** Pickleing
    """

    @classmethod
    def load(cls):
        """
        ** Alternative Constructor ** 
        Load an instance from the pickle save file if one is available 
        """
        file_path = cls.FN_SEARCH_OPTIONS

        if not os.path.exists(file_path):
            return cls()
        
        elif not util.file_last_modified_today(file_path):
            return cls()

        with open(file_path, 'rb') as pf:
            search_options = pickle.load(pf)

        return search_options

    def save(self) -> None:
        """ Pickle self to pickle save file """
        with open(self.FN_SEARCH_OPTIONS, 'wb') as pf:
            pickle.dump(self, pf)


class NewReleases():

    hide_dupes = 'on'
    style = 'list'

    pattern_spotify_track = r"spotify:track:([A-Za-z0-9]+)"
    pattern_spotify_artist = r"spotify:artist:([A-Za-z0-9]+)"

    def __init__(
        self,
        genre: str = 'anygenre',
        region: str = 'US',
        date: str | None = None, # If None, defaults to most recent week
        ) -> None:
        """
        Initialises new_releases
        
        > Parameters <
        --------------
        :genre: (str)
            the genre you wish to search by (for possible genres see everynoise.com)
        :region: (str)
            the region of the world
        :date: (str)
            format: YYYYMMDD
        """

        self.search_options = SearchOptions.load()

        # Validate genre and assign to self
        if not genre in self.search_options['genres']:
            raise ValueError(f"Invalid genre: {genre}")
        self.genre = genre

        # Validate region and assign to self
        if not region in self.search_options['region']:
            raise ValueError(f"Invalid region: {region}")
        self.region = region

        # Validate date and assign to self
        if date and date not in self.search_options['date']:
            raise ValueError(f"Invalid date: {date}")      
        self.date = date

        # Get results
        self.soup = self.get_soup()

    def __str__(self):
        # TODO test this prints prettily

        return f'''\
            NewReleases object\
            
            :genre:: {self.genre}\
            :region:: {self.region}\
            :date:: {self.date}\
            
            num_tracks: {len(self)}
        '''

    def __len__(self):
        # Returns the number of tracks found
        return len(self.tracks)

    @property
    def params(self) -> dict:
        """ Define parameters for making the request to everynoise.com """
        params = {
            'genre': self.genre,
            'region': self.region,
            'hidedupes': self.hide_dupes,
            'style': self.style
        }

        if self.date:
            params.update({'date': self.date})
        return params

    def get_soup(self):
        # Get BeautifulSoup of page
        response = requests.get(URL_MAIN, params=self.params)
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    @property
    def tracks(self) -> List[Track]:
        """ Extract the tracks for the genre specified """
        pre_results = [i.find_parent('tr') for i in self.soup.find_all('input', attrs={'name': 't'})]
        results = [i for i in pre_results if i.find_previous_sibling('tr', class_='similargenres') is None]

        print("Getting tracks from everynoise")
        return [self._get_track(i) for i in tqdm(results)] 

    @property
    def tracks_and_similar(self) -> List[Track]:
        """ Extract the tracks for the genre specified, and similar genres """
        results = [i.find_parent('tr') for i in self.soup.find_all('input', attrs={'name': 't'})]
        return [self._get_track(i) for i in results]

    @staticmethod
    def _get_track(tr) -> Track:
        """ Get track method. Mostly generated with ChatAI """
        artist_name = tr.find('a', {'href': lambda x: x and 'artist' in x}).text
        artist_id = tr.find('a', {'href': lambda x: x and 'artist' in x})['href'].replace("spotify:artist:", "")
        track_id = tr.find('span', {'class': 'play'})['trackid'].replace("spotify:track:", "")
        track_name = tr.find_all('a')[1].text
        preview_url = tr.find('span', {'class': 'play'})['preview_url']
        return Track(
            id_ = track_id,
            name = track_name,
            preview_url = preview_url,
            artists = [(artist_id, artist_name)]
        )

    def get_tracklist(self) -> List[Track]:
        """ 
        Get new releases track information from everynoise.com
            Return list of Track objects 
        """

        # Get BeautifulSoup of page
        response = requests.get(URL_MAIN, params=self.params)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract data from soup
        results = soup.find_all('span', class_='play')
        return [self._extract_track(i) for i in results]
    
    """
    ** Util
    """

    def _extract_track(self, track_tag:BeautifulSoup) -> Track:
        """ 
        Given a track_tag from the response soup, 
            extract track information and return a Track object containing it 
        """

        artist_tag = list(track_tag.next_siblings)[1]
        
        # Get attributes for creating Track object
        track_id = util.find_one(self.pattern_spotify_track, track_tag.get('trackid'))
        track_name = track_tag.text
        artist_id = util.find_one(self.pattern_spotify_artist, artist_tag.get('href'))
        artist_name = artist_tag.text
        preview_url = track_tag.get('preview_url')

        # Return Track object
        return Track(
            id_ = track_id,
            name = track_name,
            artists = list((artist_id, artist_name)),
            preview_url = preview_url
        )


if __name__ == '__main__':
    pass

    # n = NewReleases('horror punk')
    # print(n.tracks)

    