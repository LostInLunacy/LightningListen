Application for quickly previewing tracks (with music discovery in mind), using Spotify's WebAPI.

## How it works

- Uses Selenium to play a few seconds of a track before moving onto the next in the list
- While doing so prints the name of that track and allows the user to save it to a Spotify playlist

## How to use

Firstly, you'll need to run main.py

You will then be greeted with a menu asking you if you want to start a new queue or load an existing one.

Since you have not used the porgram before, you will need to create a new queue

Queues are essentially a list of tracks which you can listen to or add to at any time.


### Queue Settings

1. Destination Playlist
    The Spotify playlist to which you can save tracks as you're previewing them
2. Listen time
    Number of seconds you wish to preview each track for (max 30 seconds)
3. New
    1. OFF
    2. Track - filters tracks to exclude any you've already listened to using the app
    3. Artist - filters tracks to exclude any by artists you've already listened to using the app
4. Unique
    1. OFF
    2. Track - only includes unique tracks
    3. Artist - inly includes unique artists
5. Shuffle
    Will shuffle the tracks


### Adding the Queue

1. Everynoise
    Add tracks from this week's Spotify releases catalogued by everynoise.com
2. Links
    Add all tracks from a given playlist, album or artist


### Saving tracks to destination playlist

While the webdriver runs, the track names will be printed to you along with their number in the queue

To save a track, simply type that number to the console, and they will be added to the playlist


## Feedback welcome

Thanks for checking out my program!