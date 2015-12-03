# -*- coding: utf-8 -*-

"""
Wrapper for the QuickPin API.

Includes a simple command line client.

Example:
    $ python qpi.py submit_names usernames.csv twitter --interval=5

    This will parse the usernames contained (1 per line) in the usernames.csv
    file and submit them 1 by one at an interval of 5 seconds.

    For more information:
        $ python qpi.py --help
        $ python qpi.py submit_names --help
        $ python qpi.py submit_ids --help

    Set the  environment variables to avoid being prompted each time:
        1. QUICKPIN_USER
        2. QUICKPIN_PASSWORD
        3. QUICKPIN_URL


    Example:
        $ export QUICKPIN_USER=guest
        $ export QUICKPIN_PASSWORD=password
        $ export QUICKPIN_URL=https://example.com
"""

import requests
import click
import os
import time
import sys


class QPIError(Exception):
   """
    Represents a human-facing exception.
   """
   def __init__(self, message):
       self.message = message


class QPI():

    def __init__(self, app_url, username, password, disable_warnings=True):
        if disable_warnings:
            requests.packages.urllib3.disable_warnings()
        self.app_url = app_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth_url = app_url + '/api/authentication/'
        self.profile_url = app_url + '/api/profile/'
        self.headers = {}
        self.authenticated = False

    def authenticate(self):
        """
        Obtain an API token with supplied credentials.
        """
        payload = {'email': self.username, 'password': self.password}
        response = requests.post(self.auth_url, json=payload, verify=False)
        response.raise_for_status()
        self.headers['X-Auth'] = response.json()['token']
        self.authenticated = True

    def submit_user_ids(self,
                        user_ids,
                        site,
                        stub=False,
                        chunk_size=1,
                        interval=5):
        """
        Submit list of user IDs to add to QuickPin.

        Args:
            user_ids (list): list of user_ids to be added.
            user_ids[n] (str): user_id of the profile.
            site (str): social of the profile
            stub (bool): whether to import profiles as stubs.
            chunk_size (int): chunk size used to batch API requests.
            interval (int): interval in seconds between API requests.

        Examples:
            user_ids = [
                '32324234',
                '234343324'
            ]
            site = 'twitter'
        """
        profiles = []
        for user_id in user_ids:
            profile = {
                'upstream_id': user_id,
                'site': site
            }
            profiles.append(profile)
        response = self.submit_profiles(profiles=profiles,
                                        stub=stub,
                                        chunk_size=chunk_size,
                                        interval=interval)
        return response

    def submit_usernames(self,
                         usernames,
                         site,
                         stub=False,
                         chunk_size=1,
                         interval=5):
        """
        Submit list of user IDs to add to QuickPin.

        Args:
            user_ids (list): list of user_ids to be added.
            user_ids[n] (str): user_id of the profile.
            site (str): social of the profile
            stub (bool): whether to import profiles as stubs.
            chunk_size (int): chunk size used to batch API requests.
            interval (int): interval in seconds between API requests.

        Examples:
            usernames = [
                'hyperiongray',
                'darpa'
            ]
            site = 'twitter'
        """
        profiles = []
        for username in usernames:
            profile = {
                'username': username,
                'site': site
            }
            profiles.append(profile)
        responses = self.submit_profiles(profiles=profiles,
                                        stub=stub,
                                        chunk_size=chunk_size,
                                        interval=interval)
        return responses

    def submit_profiles(self, profiles, stub=False, chunk_size=1, interval=5):
        """
        Submit list of profiles to added to QuickPin.

        Args:
            profiles (list): list of profiles to be added.
            profiles[n]['username'] (Optional[str]): Username of the profile.
            profiles[n]['upstream_id'] (Optional[str]): ID of the profile.
            profiles[n]['site'] (str): social site where the profile exists.
            stub (bool): whether to import profiles as stubs.

        Examples:
            profiles = [
                {
                    'upstream_id': 213213,
                    'site': 'twitter'
                },
                {
                    'username': hyperiongray,
                    'site': 'twitter'
                },
            ]
        """
        if not self.authenticated:
            raise QPIError("Please authenticate first.")

        responses = []
        for chunk_start in range(0, len(profiles), chunk_size):
            chunk_end = chunk_start + chunk_size
            chunk = profiles[chunk_start:chunk_end]
            print('Requesting {} - {}'.format(chunk_start, chunk_end))
            payload = {
                'profiles': chunk,
                'stub': stub
            }
            response = requests.post(self.profile_url,
                                     headers=self.headers,
                                     json=payload,
                                     verify=False)
            response.raise_for_status()
            responses.append(response.content)
            time.sleep(interval)

        return responses


@click.group()
def cli():
    pass


@cli.command()
@click.option('--stub',
              type=click.BOOL,
              default=False,
              help='import as stubs')
@click.option('--chunk',
              default=1,
              type=click.INT,
              help='number of profiles to submit with each request')
@click.option('--interval',
              default=5,
              help='request interval in seconds')
@click.option('--username',
              prompt=True,
              default=lambda: os.environ.get('QUICKPIN_USER', ''))
@click.option('--password',
              prompt=True,
              hide_input=True,
              default=lambda: os.environ.get('QUICKPIN_PASSWORD', ''))
@click.option('--url',
              prompt=True,
              default=lambda: os.environ.get('QUICKPIN_URL', ''))
@click.argument('input', type=click.File('rb'))
@click.argument('site', type=click.Choice(['twitter', 'instagram']))
def submit_names(input, site, stub, chunk, interval, username, password, url):
    usernames = []
    qpi = QPI(url, username, password)
    qpi.authenticate()
    usernames = input.read().splitlines()
    if len(usernames) == 0:
        click.echo('Empty file')
        sys.exit()
    responses = qpi.submit_usernames(usernames=usernames,
                                     site=site,
                                     stub=stub,
                                     chunk_size=chunk,
                                     interval=interval)
    click.echo(responses)


@cli.command()
@click.option('--stub',
              type=click.BOOL,
              default=False,
              help='import as stubs')
@click.option('--chunk',
              default=1,
              type=click.INT,
              help='number of profiles to submit with each request')
@click.option('--interval',
              default=5,
              help='request interval in seconds')
@click.option('--username',
              prompt=True,
              default=lambda: os.environ.get('QUICKPIN_USER', ''))
@click.option('--password',
              prompt=True,
              hide_input=True,
              default=lambda: os.environ.get('QUICKPIN_PASSWORD', ''))
@click.option('--url',
              prompt=True,
              default=lambda: os.environ.get('QUICKPIN_URL', ''))
@click.argument('input', type=click.File('rb'))
@click.argument('site', type=click.Choice(['twitter', 'instagram']))
def submit_ids(input, site, stub, chunk, interval, username, password, url):
    user_ids = []
    qpi = QPI(url, username, password)
    qpi.authenticate()
    user_ids = input.read().splitlines()
    if len(user_ids) == 0:
        click.echo('Empty file')
        sys.exit()
    responses = qpi.submit_user_ids(user_ids=user_ids,
                                    site=site,
                                    stub=stub,
                                    chunk_size=chunk,
                                    interval=interval)
    click.echo(responses)

if __name__ == '__main__':
    cli()
