"""
    Custom object that is used throughout the program
        Contains limited information about the Spotify track
"""

from dataclasses import dataclass
from typing import List, Callable
import copy


@dataclass
class Track():
    """ Custom class for Spotify track """
    id_: str # track_id
    name: str # track_name
    artists: List[tuple[str, str]] # [(artist1_id, artist1_name), (artist2_id, artist2_name), ...]
    preview_url: str 

    URI_PREFIX = "spotify:track:"

    def __str__(self):
 
        artists = copy.copy(self.artists)
        artist_str = artists.pop()[1]

        if artists:
            secondary_artists = '; '.join(i[1] for i in artists)
            artist_str += f" (feat. {secondary_artists})"

        # Example:
        # Death Grips (feat. Meg Myers; Madonna; Britney Spears)
        return f"{artist_str} - {self.name}"

    def __hash__(self):
        return hash(self.id_)

    def __eq__(self, other) -> bool:
        """ Returns True if the self.id_ equals that of another Track, else False """
        if not isinstance(other, Track):
            raise ValueError(f"Cannot compare type Track to type {type(other)}")
        return self.id_ == other.id_

    def __ne__(self, other) -> bool:
        """ Returns False if the self.id_ equals that of another Track, else True """
        return not self == other

    @property
    def uri(self) -> str:
        """ Returns the track_uri, used when adding the track to a playlist """
        return f"{self.URI_PREFIX}{self.id_}"

    @property
    def artist_ids(self) -> list:
        """ Returns every artist_id involved in the track """
        return [i[0] for i in self.artists]

    @property
    def artist_names(self) -> list:
        """ Returns every artist_name involved in the track """
        return [i[1] for i in self.artists]

    

def _convert_to_track_object(track:dict) -> Track:
    """ Convert scraped data to Track object """
    return Track(
        id_ = track['id'],
        name = track['name'],
        artists = [(i.get('id'), i.get('name')) for i in track['artists']],
        preview_url = track.get('preview_url')
    )


def convert_to_track_object_dec(func:Callable) -> Track:
    """
    Decorator that executes a function and 
        converts the result of that function to a Track object
    """
    def inner(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        if not result:
            return None

        if isinstance(result, str):
            return _convert_to_track_object(result)
        elif isinstance(result, list):               
            return [_convert_to_track_object(i) for i in result if i]

    return inner


