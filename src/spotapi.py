import base64
from dotenv import load_dotenv
import os
import pendulum
import pickle
import requests
from typing import Callable


# Load environmental variables from root directory's .env file
load_dotenv()


class Token:
    
    URL_TOKEN = "https://accounts.spotify.com/api/token"
    FN_TOKEN = "../data/token.pkl"

    def __init__(self):

        # Access env variables
        self.client_id = os.environ['CLIENT_ID']
        self.client_secret = os.environ['CLIENT_SECRET']
        self.refresh_token = os.environ['refresh_token']

        # Refresh token
        self.refresh()

    @property
    def base64_credentials(self) -> str:
        """ Return the base64-ecoded client ID and client SECRET """
        creds = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(creds.encode()).decode()

    """
    ** Pickleing
    """

    @classmethod
    def load(cls):
        """
        ** Alternative Constructor ** 
        Load the token from the pickle save file if one is available 
        """
        try:
            with open(cls.FN_TOKEN, 'rb') as pf:
                return pickle.load(pf)
        except (FileNotFoundError, EOFError):
            return cls()

    def save(self) -> None:
        """ Pickle self to pickle save file """
        with open(self.FN_TOKEN, 'wb') as pf:
            pickle.dump(self, pf)

    """
    ** Autorefresh 
    """

    @property
    def access_token(self) -> str:
        """ 
        When getting the access_token (i.e. my_instance.access_token) 
            first check if token has expired.
        If it has, refresh it
        """
        if self.has_expired:
            self.refresh()
        return self._access_token

    """
    ** Refresh
    """

    @property
    def _refresh_headers(self) -> dict:
        return {'Authorization': f'Basic {self.base64_credentials}'}

    @property
    def _refresh_data(self) -> dict:
        return {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}

    def refresh(self):
        """ 
        Make a request to the refresh_token url to get a new access_token 

        > Modifies <
        ------------
        :self._access_token: 
            -> new access_token
        :self.expires_in: 
            -> time the new token expires

        > Calls <
        ---------
        self.save()
            saves the new token to pickle file
        """

        # Request for new access_token
        response = requests.post(
            self.URL_TOKEN,
            headers = self._refresh_headers,
            data = self._refresh_data
        )

        response_data = response.json()

        # Update instance vars
        self._access_token = response_data['access_token']
        self.expires_in = self.get_expiry_time(response_data['expires_in'])

        # Save self to pickle file
        self.save()

    """
    ** Expiry time
    """

    @staticmethod
    def get_expiry_time(seconds) -> pendulum.datetime:
        """ Get the time at which the token will expire """
        return pendulum.now() + pendulum.duration(seconds=seconds)

    @property
    def has_expired(self) -> bool:
        """ Returns True if the token has expired, else False """
        return pendulum.now() > self.expires_in


def _base_request(request_func:Callable):
    """
    Executes the request_func with 
        - URL_MAIN prefix for the request url
        - default headers
    
    > Parameters <
    --------------
    :request_func:
        method that makes a request using the requests module
    """

    def wrapper(api, url, *args, **kwargs):

        # Set full url
        if not url.startswith(api.URL_MAIN):
            url = f"{api.URL_MAIN}{url}"

        # Return response
        return request_func(api, url, *args, headers=api.headers_postauth, **kwargs)        

    return wrapper


class SpotApi():

    # Base URL for requests
    URL_MAIN = 'https://api.spotify.com/v1/'

    def __init__(self) -> None:
        # Get token object required for requests
        self.token = Token.load()

    @property
    def headers_postauth(self) -> dict:
        """ Headers used for all subsequent requests after initial authorisation """
        return {'Authorization': f"Bearer {self.token.access_token}", 'Content-Type': "application/json"}

    @_base_request
    def request(self, url:str, method:str, *args, **kwargs) -> requests.Response:
        return requests.request(url, method, *args, **kwargs)

    @_base_request
    def get(self, url:str, *args, **kwargs) -> requests.Response:
        return requests.get(url, *args, **kwargs)

    @_base_request
    def post(self, url:str, *args, **kwargs) -> requests.Response:
        return requests.post(url, *args, **kwargs)
    
    @_base_request
    def put(self, url:str, *args, **kwargs) -> requests.Response:
        return requests.put(url, *args, **kwargs)

    @_base_request
    def delete(self, url:str, *args, **kwargs) -> requests.Response:
        return requests.delete(url, *args, **kwargs)
    

