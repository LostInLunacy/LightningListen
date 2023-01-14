"""
    Main file to run the program
"""

# Local
from link_to_track import LinkToTrack
from playlist_updater import PlaylistUpdater
from everynoise import NewReleases, SearchOptions
import util

# Other
import atexit
import copy
import os
import pickle
import random
from selenium import webdriver
import threading
import time
from typing import Self


# Ignore nonsense errors
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])


class Settings():
    """ Settings for the main application """

    DEFAULTS = {
        'listen_time': 7,
        'new': 'track',
        'unique': 'track',
        'shuffle': False,
        'destination_playlist': None
    }
    
    def __init__(self) -> None:

        # Set default attributes
        [self.__setattr__(k,v) for k,v in self.DEFAULTS.items()]

    def update(self) -> None:
        
        # Display current (at first execution, default) settings to user
        print(f"Current settings:\n{self}")

        # Set attributes
        if (result := self.choose_destination_playlist()):
            self.destination_playlist = result

        if (result := self.choose_listen_time()):
            self.listen_time = result

        if (result := self.choose_unique()):
            self.unique = result

        if (result := self.choose_new()):
            self.new = result

        if (result := self.choose_shuffle()):
            self.shuffle = result

        # Display updated settings to user
        print(f"Updated settings:\n{self}")
    
    def __str__(self):
        return f"""\
        Listen time: {self.listen_time}
        New: {self.new}
        Unique: {self.unique}
        Shuffle: {self.shuffle}
        Destination Playlist: {self.destination_playlist}
        """

    def choose_shuffle(self) -> bool | None:
        """
        > Modifies <
        ------------
        (if user_input is not empty)
            self.shuffle 
        """
        print(f"\nShuffle tracks? | Current: {self.shuffle}")
        allowed_response = ('', 'y', 'n')
        while True:

            # '' -> no change
            # 'y' -> shuffle = True
            # 'n' -> shuffle = False
            choice = input('> ')

            if choice in allowed_response:
                break
            print(f"Invalid input: {choice}")
        
        
        return choice == 'y' if choice else None

    def choose_listen_time(self) -> int | None:
        """
        > Modifies <
        ------------
        (if user_input is not empty)
            self.shuffle 
        """
        print(f"\nListen time (1-30) | Current: {self.listen_time}")
        while True:

            # '' -> no change
            # '21' -> 21
            choice = input('> ')

            if not choice or choice.isdigit():
                break
            print(f"Invalid input: {choice}")

        return int(choice) if choice else None

    def choose_new(self) -> str | None:
        print(f"\nOnly include new (i.e. those you haven't yet listened to)... | Current: {self.new}")
        
        # '' -> no change
        # 'list_option' -> 'list_option'
        choice = util.select_from_list(['OFF', 'track', 'artist'], allow_none=True)
        
        return choice if choice else None

    def choose_unique(self) -> None:
        print(f"\nOnly include unique (i.e. not more than one of)... | Current: {self.unique}")
        
        # '' -> no change
        # 'list_option' -> 'list_option'
        choice = util.select_from_list(['OFF', 'track', 'artist'], allow_none=True)
        
        return choice if choice else None

    def choose_destination_playlist(self) -> str:
        print("\nThe playlist to which any liked tracks will be saved")

        pattern_link = r"(?:https://open.spotify.com/playlist)/([\w\d]+)(?:\?[\w\d=&]+)?"
        pattern_id_only = r"[\w\d]+"

        while True:

            choice = input('> ')

            if not choice and self.destination_playlist:
                return None
            if (matched_link_pattern := util.find_one(pattern_link, choice)):
                return matched_link_pattern
            elif (matched_id_pattern := util.find_one(pattern_id_only, choice)):
                return matched_id_pattern

            print(f"Invalid input: {choice}")


class PreviewQueue():

    # File names (without pkl extension)
    FN_LISTENED_ARTISTS = '../data/listened_artists'
    FN_LISTENED_TRACKS = '../data/listened_tracks'

    # Save file location for queues
    save_file_location = '../queues/'

    @classmethod
    def start(cls):
        choice = util.select_from_list(['new queue', 'load queue'])

        if choice == 'new queue':
            while True:
                name = input("Name: ").strip()
                if name: break
            return cls(name)
        elif choice == 'load queue':
            return cls.queue_load()

    def __init__(self, name:str):
        """
        > Parameters <
        --------------
        :name:
            the name of the queue
        """
        self.name = name

        # Start queue
        self.queue = list()

        # If program exits, save queue
        atexit.register(self.queue_save)
        self.save_enabled = True

        # Get settings for queue
        self.settings = Settings()
        self.settings.update()
       
        # Go to submenu_add to build queue
        self.submenu_add()

    def __len__(self) -> int:
        """ Returns the number of tracks in the queue """
        return len(self.queue)

    def __bool__(self) -> bool:
        """ Returns True if the queue is not empty """
        return len(self) > 0

    def __getstate__(self):
        
        # Make copy of the instacne
        state = self.__dict__.copy()

        # Remove lock if one exists in the instance
        # As these cannot be pickled
        if 'lock' in state:
            del state['lock']

        return state
    
    @property
    def file_path(self):
        return os.path.join(self.save_file_location, f"{self.name}.pkl")

    """
    Misc.
    """

    def clear(self):
        """ Clear the queue, so that the :self.queue: object is now an empty list """
        if not util.yn(f"Are you sure you want to clear the queue?"):
            return
        
        self.queue.clear()

    def delete(self):
        """ Delete the file associated w/ the instance and disabling saving on exit """
        
        if not util.yn(f"Are you sure you want to delete the queue?"):
            return

        # In case this the atexit signal is not overwritten
        self.save_enabled = False
        
        # Delete the queue file
        os.remove(self.file_path)

        return

    """
    ** Pickleing
    """

    @classmethod
    def queue_load(cls) -> Self:
        """
        ** Alternative constructor **

        Asks the user to select a queue:

        If they don't select one -> return None
        Otherwise -> return that queue (instance of PreviewQueue)
        """
        
        existing_queues = util.files_within(cls.save_file_location, extension='*.pkl', subdirs=True)
        print()
        choice = util.select_from_dict(existing_queues)

        if choice is None:
            # User chose not to select a queue
            return 

        # Load the appropriate instance
        with open(choice, 'rb') as pf:
            preview_queue = pickle.load(pf)
        print(f"Loaded queue {preview_queue.name}")
        atexit.register(preview_queue.queue_save)
        return preview_queue
    
    def queue_save(self):
        """ Save the queue as a pickle file """

        if not self.save_enabled:
            return
        
        with open(self.file_path, 'wb') as pf:
            pickle.dump(self, pf)
        print(f"Saved queue {self.name}")

    """
    ** Run
    """

    def __call__(self):
        """ """
        
        self.lock = threading.Lock()

        # Create copy of queue
        # This is necessary because the self.queue will be stipped as the program runs
        # And if the user saves a track (e.g. 35), we must still be able to retrieve
        # the appropriate index
        self.original_queue = copy.copy(self.queue)

        self.stop_preview = False

        # Start thread to preview tracks
        thread = threading.Thread(target=self.preview_tracks)
        thread.start()

        # Get input for liked tracks while thread is running
        self.get_user_input_likes()

        # User exited function, so exit preview_tracks on next iteration
        self.stop_preview = True


    def preview_tracks(self):
        """ Run the queue - i.e. play tracks through Selenium webdriver """

        # Ensure there are tracks in the queue
        if not self:
            print("\nNo tracks to play!")
            return

        print(f"Tracks to play: {len(self)}")

        # Start webdriver
        driver = webdriver.Chrome(options = options)

        # Play tracks
        counter = 1
        while self:
            
            track = self.queue[0]
            driver.get(str(track.preview_url))

            print(f"#{counter:4}: {track}")

            time.sleep(self.settings.listen_time)

            if self.stop_preview:
                # User exited the get_user_input_likes func
                break

            # Update pickle files
            # Do this each time to save progress in case user quits program
            self.listened_artists = self.listened_artists + track.artist_ids
            self.listened_tracks = self.listened_tracks + [track.id_]

            # Remove track from queue
            self.queue = self.queue[1:]
            
            counter += 1

    def get_user_input_likes(self):
        playlist_updater = PlaylistUpdater(self.settings.destination_playlist)

        while True:
            user_input = input('')
            if user_input == 'exit':
                break
            elif user_input.isdigit() and user_input != '0':
                # Save the selected track to playlist
                with self.lock:
                    try:
                        liked_track = self.original_queue[int(user_input)-1]
                    except IndexError:
                        print(f"Invalid number: {user_input}")
                    else:
                        playlist_updater.track_to_playlist(liked_track.uri)
                        print(f"Added to playlist: {liked_track}")
            else:
                print(f"Invalid input: {user_input}")

    def menu(self) -> None:
        """ 
        The Main Menu for the queue 

        From here you can
        1. Run the queue
        2. Append to the queue
        3. Clear the queue
        4. Delete the queue
        5. Adjust queue settings
        """

        options = {
            'Change settings': self.settings.update,
            'Queue append': self.submenu_add,
            'Queue clear': self.clear,
            'Queue delete': self.delete
        }

        while True:
            
            print(f'\n{util.title("Main Menu")}')
            print(f"\nCurrent queue: {len(self)} tracks\n")
            menu_options = {'Queue run': self} | options if self else options
            choice_func = util.select_from_dict(menu_options, zeroth='Exit')
            
            if not choice_func:
                break
                
            choice_func()

            if choice_func == self.delete:
                break

    """
    ** Add
    """

    def submenu_add(self) -> None:
        """
        Submenu for appending to the queue

        From here you can
        1. Add tracks from everynoise.com's new releases
        2. Add tracks from a playlist, artist, or album link
        """

        print(f'\n{util.title("Add tracks")}')
        while True:
            print()
            choice_func = util.select_from_dict({'Link': self.add_from_link, 'Everynoise': self.add_from_everynoise}, zeroth='Go back')
            if not choice_func:
                break
            results = choice_func()
            self.queue += results

        self.filter()

    def add_from_link(self) -> None:
        """ 
        Add to the queue given a spotify link
        """

        link_to_track = LinkToTrack()
        tracks = []

        while True:
            selection = input("\nEnter a URL or enter 'fin' to finish\n> ").strip()
            
            if selection == 'fin':
                break

            if not link_to_track.validate_link(selection):
                print(f"Invalid link: {selection}")
                continue

            results = link_to_track.link(selection)
            if results:
                tracks.extend(results)

        return tracks
        

    def add_from_everynoise(self, similar=True) -> None:
        """
        Add to queue given a everynoise new_releases and optional genre filter
        """
        genre = input("Genre: ")
        nr = NewReleases(genre=genre) if genre is not None else NewReleases()
        
        similar = util.yn("Include similar?", allow_none=True)
        return nr.tracks if not similar else nr.tracks_and_similar

    """
    ** Filters
    """

    def filter(self) -> None:
        """ Filter tracks based on self.settings """
        self.filter_has_preview_url()

        match self.settings.new:
            case 'OFF':
                pass
            case 'track':
                self.filter_track_new()
            case 'artist':
                self.filter_artist_new()

        match self.settings.unique:
            case 'OFF':
                pass
            case 'track':
                self.filter_tracks_unique()
            case 'artist':
                self.filter_artist_unique()
        
        if self.settings.shuffle:
            self.shuffle_tracks()


    def filter_has_preview_url(self) -> None:
        """ 
        Filter the queue to remove any tracks without a preview URL
        This filter must be used because tracks 
        without a preview URL are not playabale!
        """
        self.queue = [i for i in self.queue if i.preview_url]

    def filter_track_new(self) -> None:
        """ 
        Filter the queue to include only tracks that the user 
        has not listened to yet using the program
        """
        self.queue = [i for i in self.queue if i.id_ not in self.listened_tracks]

    def filter_artist_new(self) -> None:
        """
        Filter the queue to include only artists that the user
        has not listened to yet using the program
        """
        self.queue = [
            i for i in self.queue if not all([j[0] in self.listened_artists for j in i.artists])
        ]

    def filter_tracks_unique(self) -> None:
        """
        Filter the queue to include only unique tracks
        """
        self.queue = list(set(self.queue))

    def filter_artists_unique(self) -> None:
        """
        Filter to queue to include only unique artists
        """
        unique_artists = set()
        filtered_tracks = []

        def assess_track(track:dict):
            artist_ids = track.artist_ids
            if not all([i in unique_artists for i in artist_ids]):
                unique_artists.update(set(artist_ids))
                filtered_tracks.append(track)

        [assess_track(i) for i in self.queue]
        self.queue = filtered_tracks

    def shuffle(self):
        """ Shuffle the queue """
        random.shuffle(self.queue)

    """
    ** Listened to
    """

    @property
    def listened_tracks(self) -> None:
        """ Tracks the user has listened to already using this program """
        try:
            return util.load_pkl(self.FN_LISTENED_TRACKS)
        except FileNotFoundError:
            # Assume file not created yet 
            # So user has not listened to any tracks with the program
            return list()

    @listened_tracks.setter
    def listened_tracks(self, track_ids):
        """ Write to the file track_ids that the user has listened to 
        NOTE: This will override the existing contents 
        """
        util.save_pkl(self.FN_LISTENED_TRACKS, track_ids)

    @property
    def listened_artists(self) -> None:
        """ Artists the user has listened to already using this program """
        try:
            return util.load_pkl(self.FN_LISTENED_ARTISTS) 
        except FileNotFoundError:
            return list()

    @listened_artists.setter
    def listened_artists(self, artist_ids):
        """ Write to the file artist_ids that the user has listened to 
        NOTE: This will override the existing contents 
        """
        util.save_pkl(self.FN_LISTENED_ARTISTS, artist_ids)



def main():

    while True:

        # Ask the user if they want to start a new PreviewQueue or load an existing one
        pq = PreviewQueue.start()

        # Print number of unique tracks listened to using the program
        print(f"\n** You have listened to {len(pq.listened_tracks)} tracks in total! **")

        # Run the PreviewQueue's main menu
        pq.menu()


if __name__ == '__main__':
    main()
    
    

