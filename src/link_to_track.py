
# Local
from spotapi import SpotApi
from track import Track, convert_to_track_object_dec

# Other
import re
from typing import List


class LinkToTrack():
    """
    Scrapes track data based on links for:

    - Album
    - Artist
    - Playlist
    """

    PATTERN_LINK = r"(?:https://open.spotify.com/)?(artist|album|playlist)/([\w\d]+)(?:\?[\w\d=&]+)?"

    def __init__(self) -> None:
        self.spotapi = SpotApi()

    @classmethod
    def get_category_and_id(cls, link) -> bool:
        """ Given a full link, returns the catgeory (e.g. playlist) and id """
        result = re.findall(cls.PATTERN_LINK, link)
        return None if not result else result[0]

    """
    ** Convert to Tracks
    """
    @classmethod
    def validate_link(cls, link):
        return bool(re.findall(cls.PATTERN_LINK, link))

    def link(self, link:str):
        """
        Given a link 
            (e.g. https://open.spotify.com/playlist/4BaKglpjlo8yoCQccCyZLx?si=d2d9a07aa5144e87)
        
        Get the category and id_
            In the example: 
                category = playlist
                id_ = 4BaKglpjlo8yoCQccCyZLx
        
        Call the appropriate method based on :catgeory: with the argument :id_:
        """
        
        if not self.validate_link(link):
            # Invald value
            print(f"Invalid link: {link}")
            return
        
        category, id_ = self.get_category_and_id(link)

        match category:
            # case 'track': return self.track(id_)
            case 'album': return self.album(id_)
            case 'artist': return self.artist(id_)
            case 'playlist': return self.playlist(id_)

    # -----------------------------------

    ## BUG: 
    ## No response data returned
    ## But 200 response status code
    ## I even gave this to Chat-OpenAI and it couldn't figure out why this isn't working
    
    # @convert_to_track_object_dec
    # def track(self, track_id: str) -> Track:
    #     """ 
    #     Given a track_id
    #         - Scrape data about the track
    #         - Accordingly return Track object
    #     """
    #     suburl = f"tracks/{track_id}"
    #     response_data = self.__scrape_data(suburl)
    #     return response_data

    # -----------------------------------

    @convert_to_track_object_dec
    def playlist(self, playlist_id:str) -> List[Track]:
        """ 
        Given a playlist_id
            - Scrape tracklist data
            - Accordingly, return a list of Track objects
        """

        # Suburl for initial request
        suburl = f"playlists/{playlist_id}/tracks"

        # List of tracks that will be populated and ultimately returned
        tracks = list()

        while True:

            # Scrape playlist data
            response_data = self.__scrape_data(suburl)

            # Extract tracklist data from scraped playlist data
            tracks_data = self.__get_tracks_data(response_data)
            tracks_on_page = [i['track'] for i in tracks_data['items']]

            # Add tracks on page to tracklist
            tracks.extend(tracks_on_page)

            # Assess whether there is a next page
            # If there isn't, break
            if not (suburl := tracks_data.get('next')):
                break

            # Continue scraping next page using updated :suburl: variable

        return tracks


    @convert_to_track_object_dec
    def album(self, album_id:str) -> List[Track]:
        """ 
        Given an album_id
            - Scrape tracklist data
            - Accordingly, return a list of Track objects
        """

        # Suburl for initial request
        suburl = f"albums/{album_id}/tracks"

        # List of tracks that will be populated and ultimately returned
        tracks = list()

        while True:

            # Scrape album data
            response_data = self.__scrape_data(suburl)

            # Extract tracklist data from scraped playlist data
            tracks_data = self.__get_tracks_data(response_data)
            tracks_on_page = [i for i in tracks_data['items']]

            # Add tracks on page to tracklist
            tracks.extend(tracks_on_page)

            # Assess whether there is a next page
            # If there isn't, break
            if not (suburl := tracks_data.get('next')):
                break

            # Continue scraping next page using updated :suburl: variable

        return tracks

    def artist(self, artist_id:str, release_types:list|str = 'ALL') -> List[Track]:
        """ 
        Given an artist_id
            - Scrape tracklist data
            - Accordingly, return a list of Track objects

        NOTE this method doesn't need convert_to_track_object_dec decorator 
            because it calls methods which have it already

        > Params <
        ----------
        :artist_id:
        :include:
            comma-separated list of album types | str 'ALL' for all types
                e.g. if set to 'albums': returns only Tracks that are part of an album 
        """

        # Suburl for initial request
        suburl = f"artists/{artist_id}/albums"

        # List of tracks that will be populated and ultimately returned
        tracks = list()

        while True:

            # Scrape artist's releases data
            params = {} if release_types == 'ALL' else {'include': release_types} 
            response_data = self.__scrape_data(suburl, params=params)

            # Extract releases list data from scraped album data
            album_data = self.__get_album_data(response_data)
            albums = [i['id'] for i in album_data['items']]

            # Extend the tracks_list with the tracklist of each album on the page
            [tracks.extend(self.album(album_id)) for album_id in albums]

            # Assess whether there is a next page
            # If there isn't, break
            if not (suburl := album_data.get('next')):
                break

            # Continue scraping next page using updated :suburl: variable

        return tracks

    """
    ** Utility
    """

    def __scrape_data(self, suburl:str, **kwargs) -> dict:
        """ 
        Perform get request for given suburl and **kwargs
        Return dict by using json() method on response object
        """
        response = self.spotapi.get(suburl, **kwargs)        
        return response.json()

    @staticmethod
    def __get_tracks_data(data) -> dict:
        """ Given response data, returns the dictionary which contains track info """
        return data['tracks'] if not 'offset' in data else data

    @staticmethod
    def __get_album_data(data) -> dict:
        """ Given response data, returns the dictionary which contains album info """
        return data['albums'] if not 'offset' in data else data

    

if __name__ == '__main__':
    pass

    # l = LinkToTrack()

    # print(l.playlist('6ThB5PvYRcsoXDX0VClSa5'))
    # print(l.album('4pk3IXbfaU0cK7oHuEdbEJ'))
    # print(l.track('3BG4XnGpTL4lB79iMWdyAv'))

