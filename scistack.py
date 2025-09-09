#!/home/pconstant/venv/base/bin/python3
"""
scistack.py
A command-line interface (CLI) tool for managing and searching scientific documents stored in a JSON file.
Author: pconstantinidis
Version: 0.1.0
Functions:
    load_data(path):
        Load the data from the given path.
    sudo_required(func):
        Decorator to prompt for sudo password before executing a command.
Classes:
    SciStackCLI(cmd.Cmd):
        A command-line interface for managing and searching scientific papers.
        Methods:
            do_load(args):
                Load data from a JSON file: load <path>
            do_search(args):
                Search documents: search -t <title> -d <doi>
            search_documents(args):
                Search documents by title or DOI.
            do_get(args):
                Get a specific entry by number: get <number>
            do_remove(args):
                Delete a specific entry by number: delete <number>
            do_info(args):
                Display information about the dataset.
            do_quit(args):
                Quit the application.
"""

import  os
from sys import argv
import cmd
import argparse
import json
import getpass
import shlex
import re
import pandas as pd
import webbrowser

_DATAFRAME = None
_SUDO_PASSWORD = r"itsme"
_PATH = os.path.abspath(os.path.expanduser("~/Dev/qtech/SciStack/scientificDocs.json"))


def load_data(path):
    '''
    Load the data from the given path
    '''
    if not os.path.exists(path):
        print(f"\n{path}\nThere is not such file")
        return -1
    try:
        global DATAFRAME
        DATAFRAME = pd.read_json(path)
        print(f"**Data loaded successfully**")
    except Exception as e:
        print(20*'-'+f"\nException raised while loading dataframe\n\nError: {e}")
        return None    

def sudo_required(func):
    def wrapper(self, args):
        password = getpass.getpass("Enter sudo password: ")
        if password == _SUDO_PASSWORD:
            return func(self, args)
        else:
            print("Incorrect password. Command not executed.")
    return wrapper


class SciStackCLI(cmd.Cmd):
    _prompt = "SciStack>"
    _classes = set(("paper", "book", "thesis", "notes"))
    #_dags = set(("ADAPT-VQE", "computational physics", "quantum chemistry"))

    def __init__(self):
        super().__init__()
        self.prompt = self._prompt

    @sudo_required
    def do_load(self, args):
        """Load data from a JSON file: load <path>"""
        try:
            load_data(args)
        except Exception as e:
            print(f"Failed to load data: {e}")

    def do_search(self, args):
        """Search documents: search -t <title> -d <doi>"""
        parser = argparse.ArgumentParser(prog='search')
        parser.add_argument("-t", "--title", type=str, help="Search for a paper by title")
        parser.add_argument("-d", "--doi", type=str, help="Search for a paper by DOI")
        
        try:
            args = parser.parse_args(shlex.split(args))
            self.search_documents(args)
        except SystemExit:
            pass  # argparse throws a SystemExit exception if parsing fails

    def search_documents(self, args):
        """Search documents by title or DOI."""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return

        if args.title:
            result = DATAFRAME[DATAFRAME['title'].str.contains(args.title, case=False)]
            print("\nSearch results by title:")
            print(result)
        if args.doi:
            result = DATAFRAME[DATAFRAME['doi'] == args.doi]
            print("\nSearch results by DOI:")
            print(result)


    def get_newentry(self):
        """Prompt the user to enter a new entry."""
        # title_pattern =
        # doi_pattern =

        while True:
            _title = input("Title: ")
            #if title_pattern.match(_title):
            break
            #print("Invalid title format. Please try again.")

        while True:
            _doi = input("DOI: ")
            #if doi_pattern.match(_doi):
            break
            #print("Invalid DOI format. Please try again.")

        while True:
            _class = input("Class: ")
            if _class in self._classes:
                break
            print("Invalid class. Please try again.")

        _note = input("Note [pass]: ")
        if _note.casefold() == 'pass'.casefold():
            _note = None

        # Check for duplicates
        if not DATAFRAME[(DATAFRAME['title'] == _title)].empty:
            print("Duplicate entry found.")
            return None

        entry = {'title': _title, 'doi': _doi, 'class': _class, 'note': _note}
        print(20*'-'+f"\nReview entry:\n{entry}")
        confirm = input("Add entry? [Y/n]: ")
        if confirm.casefold() == 'n'.casefold():
            return None

        return entry

    def do_add(self, args):
        """Add a new entry to the dataset."""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return 1

        try:
            new_entry = self.get_newentry()
            if not new_entry:
                print("Entry not added.")
                return

            # Save the updated dataframe back to the JSON file
            with open(_PATH, 'r+') as file:
                data = json.load(file)
                data.append(new_entry)
                file.seek(0)
                json.dump(data, file, indent=4)

            DATAFRAME = pd.concat([DATAFRAME, pd.DataFrame([new_entry])], ignore_index=True)
            print("Entry added successfully.")
        except Exception as e:
            print(f"Failed to add entry: {e}")

    def do_get(self, args):
        """Get a specific entry by number: get <number>"""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return 1
        try:
            index = int(args)
            if index < 0 or index >= len(DATAFRAME):
                print(f"Index out of bounds")
                return -1
                
            entry = DATAFRAME.iloc[index]
            print(f"Entry {index}:")
            print(entry+'\n')
        except ValueError:
            print("Please provide a valid number.")
        except Exception as e:
            print(f"Failed to get entry: {e}")

    def do_websearch(self, args):
        """Search the web for a specific entry by number: websearch <number>"""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return 1
        try:
            index = int(args)
            if index < 0 or index >= len(DATAFRAME):
                print(f"Index out of bounds")
                return -1
            
            entry = DATAFRAME.iloc[index]
            doi = entry.get('doi')
            if not doi:
                print(f"No DOI found for entry {index}")
                return -1
            
            # url = f"https://doi.org/{doi}"
            url = f"https://www.google.com/search?q={doi}"
            webbrowser.open(url)
            print(f"Opened web browser for DOI: {doi}")
        except ValueError:
            print("Please provide a valid number.")
        except Exception as e:
            print(f"Failed to perform web search: {e}")

    @sudo_required
    def do_remove(self, args):
        """Delete a specific entry by number: delete <number>"""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return 1
        try:
            index = int(args)
            if index < 0 or index >= len(DATAFRAME):
                print(f"Index {index} is out of range.")
                return -1
            DATAFRAME = DATAFRAME.drop(index).reset_index(drop=True)

            # Save the updated dataframe back to the JSON file
            with open(_PATH, 'w') as file:
                json.dump(DATAFRAME.to_dict(orient='records'), file, indent=4)
            print(f"Entry {index} deleted successfully.\n")
        except ValueError:
            print("Please provide a valid number.")
        except Exception as e:
            print(f"Failed to delete entry: {e}")

    def do_info(self, args):
        """Display information about the dataset."""
        global DATAFRAME
        if DATAFRAME is None:
            print("No data loaded. Use the 'load' command to load data first.")
            return

        print(f"\n{DATAFRAME["class"].value_counts().to_string(index=True, header=False)}")
        print(f"\nColumns: {', '.join(DATAFRAME.columns)}\n")

    def do_clear(self, args):
        """Clear the screen."""
        os.system('clear')

    def do_quit(self, args):
        """Quit the application."""
        return True


if __name__ == '__main__':
    if len(argv) != 1:
        print("No support for command line arguments")
        os._exit(1)
    
    load_data(_PATH)
    SciStackCLI().cmdloop()
