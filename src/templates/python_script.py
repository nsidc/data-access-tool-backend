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
#
# ------------------------------------------------------------------------------
# Ignore flake8 warnings for this file
# flake8: noqa
#
from __future__ import print_function
import sys
import base64
import json
import netrc
import ssl
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
CMR_FILE_URL = CMR_URL + '/search/granules.json?provider=NSIDC_ECS&sort_key=short_name' + \
    '&scroll=true&page_size=' + str(CMR_PAGE_SIZE)


def get_username():
    username = ''
    try:
        do_input = raw_input
    except:
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
    except:
        username = ''
        password = ''

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
            except HTTPError as e:
                print("Incorrect username or password")
                credentials = None
                username = ''
                password = ''

    return credentials


def cmr_download(urls):
    """Download files from list of urls."""
    try:
        if not isinstance(urls, list) or not urls:
            return
    except:
        return

    print('Downloading {} files'.format(len(urls)))
    credentials = None

    for url in urls:
        if not credentials and urlparse(url).scheme == 'https':
            credentials = get_credentials(url)

        filename = url.split('/')[-1]
        print('Downloading ' + filename)

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
        except IOError as e:
            raise
        except KeyboardInterrupt:
            quit()


def cmr_filter_urls(search_results):
    """Select only the desired data files from CMR response."""
    if 'feed' not in search_results or 'entry' not in search_results['feed']:
        return []

    entries = search_results['feed']['entry']
    if not entries:
        return []

    urls = []
    # Filter out filename duplicates (use a dict for O(1) lookups)
    url_dups = dict()

    for entry in entries:
        if 'links' not in entry:
            continue
        for link in entry['links']:
            if 'href' not in link:
                continue
            if 'inherited' in link and link['inherited']:
                continue
            # Note: This will allow both data# and metadata# to go thru
            if 'rel' in link and 'data#' not in link['rel']:
                continue
            filename = link['href'].split('/')[-1]
            if filename not in url_dups:
                urls.append(link['href'])
                url_dups[filename] = True

    return urls


def cmr_search(short_name, version, time_start, time_end,
               polygon='', filename_filter=''):
    """Initiate a scrolling CMR query for files matching input criteria."""

    params = '&short_name=' + short_name
    desiredPadLength = 3
    padding = ''
    while len(version) <= desiredPadLength:
        params += '&version=' + padding + version
        desiredPadLength -= 1
        padding += '0'
    params += '&temporal[]=' + time_start + ',' + time_end
    if polygon is not '':
        params += '&polygon=' + polygon
    if filename_filter is not '':
        params += '&producer_granule_id[]=' + filename_filter + \
            '&options[producer_granule_id][pattern]=true'
    print(CMR_FILE_URL + params)
    cmr_scroll_id = None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urls = []
        while True:
            req = Request(CMR_FILE_URL + params)
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
                    print('Found {} matches, retrieving URLs'.format(hits))
                else:
                    print('Found no matches')
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
