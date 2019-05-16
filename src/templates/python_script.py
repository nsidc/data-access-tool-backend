# ------------------------------------------------------------------------------
# NSIDC Data Download Script
# Tested in Python 2.7 and Python 3.7
#
# To run the script at a Linux, macOS, or Cygwin command-line terminal:
#   $ python nsidc-data-download.py
#
# On Windows, open Start menu -> Run and type cmd. Then type:
#     python nsidc-data-download.py
#
# The script will first search Earthdata for all matching files.
# You will then be prompted for your Earthdata username/password
# and the script will download the matching files.
#
# If you wish, you may store your Earthdata username/password in a .netrc
# file in your $HOME directory and the script will automatically attempt to
# read this file. The .netrc file should have the following format:
#    machine cmr.earthdata.nasa.gov login myusername password mypassword
# where 'myusername' and 'mypassword' are your Earthdata credentials.

from __future__ import print_function

import base64
import itertools
import json
import netrc
import ssl
import sys
from getpass import getpass

try:
    from urllib.parse import urlparse
    from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
    from urllib.error import HTTPError, URLError
except ImportError:
    from urlparse import urlparse
    from urllib2 import urlopen, Request, HTTPError, URLError, build_opener, HTTPCookieProcessor

short_name = '{short_name}'
version = '{version}'
time_start = '{time_start}'
time_end = '{time_end}'
polygon = '{polygon}'
filename_filter = '{filename_filter}'

CMR_URL = 'https://cmr.earthdata.nasa.gov'
CMR_PAGE_SIZE = 2000
CMR_FILE_URL = ('{}/search/granules.json?provider=NSIDC_ECS&sort_key=short_name'
                '&scroll=true&page_size={}'.format(CMR_URL, CMR_PAGE_SIZE))


def get_username():
    username = ''

    # For Python 2/3 compatibility:
    try:
        do_input = raw_input  # noqa
    except NameError:
        do_input = input

    while not username:
        try:
            username = do_input('Earthdata username: ')
        except KeyboardInterrupt:
            quit()
    return username


def get_password():
    password = ''
    while not password:
        try:
            password = getpass('password: ')
        except KeyboardInterrupt:
            quit()
    return password


def get_credentials(url):
    """If the user has a .netrc file set up, use that. Otherwise, prompt for
    creds.
    """
    credentials = None
    try:
        info = netrc.netrc()
        username, account, password = info.authenticators(urlparse(CMR_URL).hostname)
    except Exception:
        username = None
        password = None

    while not credentials:
        if not username:
            username = get_username()
            password = get_password()
        credentials = '{}:{}'.format(username, password)
        credentials = base64.b64encode(credentials.encode('ascii')).decode('ascii')

        if url:
            try:
                req = Request(url)
                req.add_header('Authorization', 'Basic {}'.format(credentials))
                opener = build_opener(HTTPCookieProcessor())
                opener.open(req)
            except HTTPError:
                print('Incorrect username or password')
                credentials = None
                username = None
                password = None

    return credentials


def build_cmr_query_url(short_name, version, time_start, time_end, polygon, filename_filter):
    params = '&short_name={}'.format(short_name)
    desired_pad_length = 3
    padding = ''
    while len(version) <= desired_pad_length:
        padded_version = '{}{}'.format(padding, version)
        params += '&version={}'.format(padded_version)
        desired_pad_length -= 1
        padding += '0'
    params += '&temporal[]={},{}'.format(time_start, time_end)
    if polygon:
        params += '&polygon={}'.format(polygon)
    if filename_filter:
        params += '&producer_granule_id[]={}&options[producer_granule_id][pattern]=true'.format(filename_filter)
    return CMR_FILE_URL + params


def cmr_download(urls):
    """Download files from list of urls."""
    if not urls:
        return

    print('Downloading {} files...'.format(len(urls)))
    credentials = None

    for index, url in enumerate(urls, start=1):
        if not credentials and urlparse(url).scheme == 'https':
            credentials = get_credentials(url)

        filename = url.split('/')[-1]
        print('{}/{}: {}'.format(index, len(urls), filename))

        try:
            # In Python 3 we could eliminate the opener and just do 2 lines:
            # resp = requests.get(url, auth=(username, password))
            # open(filename, 'wb').write(resp.content)
            req = Request(url)
            if credentials:
                req.add_header('Authorization', 'Basic {}'.format(credentials))
            opener = build_opener(HTTPCookieProcessor())
            data = opener.open(req).read()
            open(filename, 'wb').write(data)
        except HTTPError as e:
            print('HTTP error {}, {}'.format(e.code, e.reason))
        except URLError as e:
            print('URL error: {}'.format(e.reason))
        except IOError:
            raise
        except KeyboardInterrupt:
            quit()


def cmr_filter_urls(search_results):
    """Select only the desired data files from CMR response."""
    if 'feed' not in search_results or 'entry' not in search_results['feed']:
        return []

    entries = [e['links']
               for e in search_results['feed']['entry']
               if 'links' in e]
    # Flatten "entries" to a simple list of links
    links = list(itertools.chain(*entries))

    urls = []
    unique_filenames = set()
    for link in links:
        if 'href' not in link:
            # Exclude links with nothing to download
            continue
        if 'inherited' in link and link['inherited'] is True:
            # Why are we excluding these links?
            continue
        if 'rel' in link and 'data#' not in link['rel']:
            # Exclude links which are not classified by CMR as "data" or "metadata"
            continue

        if 'title' in link and 'opendap' in link['title'].lower():
            # Exclude OPeNDAP links--they are responsible for many duplicates
            # This is a hack; when the metadata is updated to properly identify
            # non-datapool links, we should be able to do this in a non-hack way
            continue

        filename = link['href'].split('/')[-1]
        if filename in unique_filenames:
            # Exclude links with duplicate filenames (they would overwrite)
            continue
        unique_filenames.add(filename)

        urls.append(link['href'])

    return urls


def cmr_search(short_name, version, time_start, time_end,
               polygon='', filename_filter=''):
    """Initiate a scrolling CMR query for files matching input criteria."""

    cmr_query_url = build_cmr_query_url(short_name=short_name, version=version,
                                        time_start=time_start, time_end=time_end,
                                        polygon=polygon, filename_filter=filename_filter)
    print('Querying for data:\n\t{}\n'.format(cmr_query_url))

    cmr_scroll_id = None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urls = []
        while True:
            req = Request(cmr_query_url)
            if cmr_scroll_id:
                # TODO: is consistent capitalization possible here?
                req.add_header('CMR-Scroll-Id', cmr_scroll_id)
            response = urlopen(req, context=ctx)
            if not cmr_scroll_id:
                # Python 2 and 3 have different case for the http headers
                headers = {k.lower(): v for k, v in dict(response.info()).items()}
                cmr_scroll_id = headers['cmr-scroll-id']
                hits = int(headers['cmr-hits'])
                if hits > 0:
                    print('Found {} matches.'.format(hits))
                else:
                    print('Found no matches.')
            search_page = response.read()
            search_page = json.loads(search_page)
            url_scroll_results = cmr_filter_urls(search_page)
            if not url_scroll_results:
                break
            if hits > CMR_PAGE_SIZE:
                print('.', end='')
                sys.stdout.flush()
            urls += url_scroll_results

        if hits > CMR_PAGE_SIZE:
            print()
        return urls
    except KeyboardInterrupt:
        quit()


def main():

    # Supply some default search parameters, just for testing purposes.
    # These are only used if the parameters aren't filled in up above.
    global short_name, version, time_start, time_end, polygon, filename_filter
    if 'short_name' in short_name:
        short_name = 'MOD10A2'
        version = '6'
        time_start = '2001-01-01T00:00:00Z'
        time_end = '2019-03-07T22:09:38Z'
        polygon = '-109,37,-102,37,-102,41,-109,41,-109,37'
        filename_filter = '*A2019*'  # '*2019010204*'

    urls = cmr_search(short_name, version, time_start, time_end,
                      polygon=polygon, filename_filter=filename_filter)

    cmr_download(urls)


if __name__ == '__main__':
    main()
