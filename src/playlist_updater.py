"""
    Module for updating playlists on Spotify
"""
from spotapi import SpotApi


class PlaylistUpdater():

    def __init__(self, playlist_id: str):
        """
        > Params <
        ----------
        :playlist_id:
            the id of the playlist you wish to update
        """
        self.spotapi = SpotApi()
        self.playlist_id = playlist_id

    def tracks_to_playlist(
        self,
        track_uris: str,
        position: int | None = None 
    ):
        """ 
        Add tracks to a playlist given their URIs 

        > Params <
        ----------
        :track_uri:
            list containing URIs of the tracks you wish to add to the playlist
        :position:
            the index of where you'd like the track to be added
            DEFAULT: None 
                -> appends track to end of playlist
        """
        params = {'uris': track_uris}
        if position: params.update({'position': position})
        self.spotapi.post(url = f"playlists/{self.playlist_id}/tracks", params = params)

    def track_to_playlist(
        self,
        track_uri: str,
        position: int | None = None 
    ):
        """ 
        Add a track to a playlist given its URI 

        > Params <
        ----------
        :track_uri:
            the uri of the track you wish to add to the playlist
        :position:
            the index of where you'd like the track to be added
            DEFAULT: None 
                -> appends track to end of playlist
        """
        self.tracks_to_playlist([track_uri], position)

    
if __name__ == '__main__':
    pass
