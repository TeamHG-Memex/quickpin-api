# -*- coding: utf-8 -*-
"""
Wrapper for the QuickPin API.

Includes a simple command line client.
"""

import requests
import click
import os
import time
import sys
from pprint import pprint


class QPIError(Exception):
    """
    Represents a human-facing exception.
    """
    def __init__(self, message):
        self.message = message


class QPI():

    def __init__(self,
                 app_url,
                 token=None,
                 username=None,
                 password=None,
                 disable_warnings=True):

        if disable_warnings:
            requests.packages.urllib3.disable_warnings()

        self.app_url = app_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth_url = app_url + '/api/authentication/'
        self.profile_url = app_url + '/api/profile/'
        self.search_url = app_url + '/api/search/'
        self.headers = {}
        self.token = token

        if self.token is None or self.token == '':
            self.token = self.get_token(username, password)

        self.headers['X-Auth'] = self.token
        self.authenticated = True

    def get_token(self, username, password):
        """
        Obtain an API token with supplied credentials.
        If token is passed as a parameter, sets the auth header and
        authenticated status.
        """
        payload = {'email': username, 'password': password}
        response = requests.post(self.auth_url, json=payload, verify=False)
        response.raise_for_status()
        try:
            token = response.json()['token']
        except KeyError:
            raise QPIError('Authentication failed.')

        return token

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
        with click.progressbar(
            length=len(profiles),
            label='Submitting profiles to QuickPin'
        ) as bar:
            for chunk_start in range(0, len(profiles), chunk_size):
                chunk_end = chunk_start + chunk_size
                chunk = profiles[chunk_start:chunk_end]
                bar.update(len(chunk))
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

    def search(self, query, type_=None, facets=None, rpp=100,
               page=1, sort=None):
        """
        Obtain QuickPin search results for query.

        Args:
            query (str): the search query.
            type_ (str): the type, e.g. profile, post.
            rpp (int): results per page
            page (int): results page index.
            sort (str): facet to search by.

        Example:
            >> qpi = QPI()
            >> qpi.search('', '', '')

        """
        if not self.authenticated:
            raise QPIError("Please authenticate first.")

        params = {
            'query': query,
            'rpp': rpp,
            'page': page,
        }
        param_str = "&".join("%s=%s" % (k, v) for k, v in params.items())
        if type_ is not None:
            params['type'] = type_
        if facets is not None:
            params['facets'] = facets
        if sort is not None:
            params['sort'] = sort

        response = requests.get(self.search_url,
                                headers=self.headers,
                                params=param_str,
                                verify=False)
        response.raise_for_status()

        return response


class Config(object):
    """
    Base configuration class.
    """
    def __init__(self):
        self.app_url = None
        self.token = None


# Create decorator allowing configuration to be passed between commands.
pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--username',
              type=click.STRING,
              help='Quickpin username.',
              required=False)
@click.option('--password',
              help='Quickpin password.',
              type=click.STRING,
              required=False)
@click.option('--token',
              help='Quickpin API token.',
              envvar='QUICKPIN_TOKEN',
              type=click.STRING,
              required=False)
@click.option('--url',
              help='Quickpin URL.',
              prompt=True,
              envvar='QUICKPIN_URL')
@pass_config
def cli(config, username, password, token, url):
    """
    \b
    QuickPin API command line client.
    =================================

    \b
    Examples:
        $ python qpi.py submit_names usernames.txt twitter --interval=5
        or
        $ python qpi.py --username=username --password=password submit_names usernames.txt twitter --interval=5
        or
        $ python qpi.py --token=token submit_names usernames.txt twitter --interal=5

    This will parse the usernames contained (1 per line) in the usernames.txt
    file and submit them 1 by one at an interval of 5 seconds.

    \b
    For more information:
        $ python qpi.py --help
        $ python qpi.py submit_names --help
        $ python qpi.py submit_ids --help

    \b
    Set the  environment variables to avoid being prompted each time:
        1. QUICKPIN_URL
        1. QUICKPIN_TOKEN

    \b
    Example:
        $ export QUICKPIN_URL="https://example.com"
        $ export QUICKPIN_TOKEN="1|2015-12-09T16:50:59.057635.Y5pm9qB_naw6FkOekcksiFRyMlY"
    =====================================================================================
    """
    config.app_url = url

    if token:
        config.token = token
    else:
        if not username:
            username = input('Username:')
        if not password:
            password = input('Password:')

        qpi = QPI(app_url=url, username=username, password=password)

        if qpi.authenticated:
            config.token = qpi.token
        else:
            raise QPIError('Authenication failure')

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
@click.argument('input', type=click.File('r'))
@click.argument('site', type=click.Choice(['twitter', 'instagram']))
@pass_config
def submit_names(config, input, site, stub, chunk, interval):
    """
    Submit profiles by username.
    """
    usernames = []
    qpi = QPI(app_url=config.app_url, token=config.token)
    usernames = input.read().splitlines()
    usernames = [username for username in usernames if username != '']
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
@click.option('--url',
              prompt=True,
              default=lambda: os.environ.get('QUICKPIN_URL', ''))
@click.argument('input', type=click.File('r'))
@click.argument('site', type=click.Choice(['twitter', 'instagram']))
@pass_config
def submit_ids(config, input, site, stub, chunk, interval):
    """
    Submit profiles by ID.
    """
    user_ids = []
    qpi = QPI(app_url=config.app_url, token=config.token)
    qpi.authenticate()
    user_ids = input.read().splitlines()
    user_ids = [user_id for user_id in user_ids if user_id != '']

    if len(user_ids) == 0:
        click.echo('Empty file')
        sys.exit()

    responses = qpi.submit_user_ids(user_ids=user_ids,
                                    site=site,
                                    stub=stub,
                                    chunk_size=chunk,
                                    interval=interval)
    click.echo(responses)


@cli.command()
@click.option('--type',
              type=click.STRING,
              help='The type, e.g. profile, stub.')
@click.option('--facets',
              type=click.STRING,
              help='Facet filters.')
@click.option('--page',
              default=1,
              type=click.INT,
              help='Result page index.')
@click.option('--rpp',
              default=100,
              type=click.INT,
              help='Results per page.')
@click.option('--sort',
              type=click.STRING,
              help='Column to sort by.')
@click.argument('query', type=click.STRING)
@pass_config
def search(config, query, type, facets, page, rpp, sort):
    """
    Search profiles.
    """
    qpi = QPI(app_url=config.app_url, token=config.token)
    response = qpi.search(query=query,
                          type_=type,
                          facets=facets,
                          page=page,
                          rpp=rpp,
                          sort=sort)
    pprint(response.json())


@cli.command()
@pass_config
def token(config):
    """
    Get API token.
    """
    click.echo('Token obtained, now set `QUICKPIN_TOKEN` environment '
               'variable as "{}"'.format(config.token))
    click.echo('e.g. export QUICKPIN_TOKEN="{}"'.format(config.token))


if __name__ == '__main__':
    cli()
