
import os
import time
import glob
import pickle
import re


def title(text: str, divider='=') -> str:
    """ Returns a pretty title """
    length = len(text)
    divider *= length
    return '\n'.join((divider, text, divider))

def find_one(pattern:str, string:str) -> str|None:
    results = re.findall(pattern, string)
    return results[0] if results else None

def load_pkl(file_name:str):
    with open(f"{file_name}.pkl", 'rb') as pf:
        content = pickle.load(pf)
    return content


def save_pkl(file_name:str, content):
    with open(f"{file_name}.pkl", 'wb') as pf:
        pickle.dump(content, pf) 


def file_last_modified_today(file_path: str) -> bool:

    # Get the modification time of the file
    modification_time = os.stat(file_path).st_mtime

    # Get the current time
    current_time = time.time()

    # Convert the modification time and current time to dates
    modification_date = time.gmtime(modification_time).tm_yday
    current_date = time.gmtime(current_time).tm_yday

    # Return True if the modification date is the same as the current date, else False
    return modification_date == current_date
    

def yn(prompt:str, allow_none:bool = False) -> bool:
    """
    Get a Yes/No response from the user

    > Returns <
    -----------
    True if response == 'y' else False
    """
    response_values = {'y': True, 'n': False}
    if allow_none: response_values.update({'': None})

    user_response = None
    while True:
        user_response = input(f"{prompt}\n: [y/n]: ").lower().strip()
        if user_response in response_values:
            break
        print(f"Invalid value: {user_response}. Please enter one of the following: {list(response_values.keys())}")
    
    return response_values[user_response]


def files_within(path: str, extension: str, subdirs: bool) -> dict:
    """ 
    Get all files contained within a given directory 

    Returned in the following format:
    {file_name: file_path, ...}
    """
    file_paths = glob.glob(path + '/**/' + extension, recursive=subdirs)
    return {os.path.basename(file): file for file in file_paths}
    
    
def select_from_list(items:list, allow_none:bool = False) -> str | None:

    for i, item in enumerate(items):
        print(f"{i+1}: {item}")

    while True:
        selection = input('> ')

        if allow_none and not selection:
            return None

        if not selection.isdigit() or not (selection := int(selection)) in range(1, len(items)+1):       
            print(f"Invalid input: {selection}")
            continue

        return items[selection-1]


def select_from_dict(items:dict, zeroth='Cancel') -> str | None:

    # Get a list of the items' keys
    keys = list(items)
    
    # Print options to user
    print(f"0: {zeroth}")
    for i, key in enumerate(keys):
        print(f"{i+1}: {key}")

    print()
    # Get user selection
    while True:
        selection = input('> ')

        if not selection.isdigit() or not (selection := int(selection)) in range(0, len(keys)+1):
            print(f"Invalid input: {selection}")
            continue
        
        # If 0 -> None
        # Else -> get the dictionary value that corresponds to the selected key
        return None if not selection else items[keys[selection-1]]


