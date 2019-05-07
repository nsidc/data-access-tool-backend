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
# Ignore mypy and flake8 warnings for this file
# type: ignore
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
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib2 import urlopen, Request, HTTPError, build_opener, HTTPCookieProcessor

collectionAuthId = '{collectionAuthId}'
collectionVersionId = '{collectionVersionId}'
temporalLowerBound = '{temporalLowerBound}'
temporalUpperBound = '{temporalUpperBound}'
boundingBox = '{boundingBox}'
polygon = '{polygon}'
granuleFilter = '{granuleFilter}'

CMR_URL = 'https://cmr.earthdata.nasa.gov'
CMR_PAGE_SIZE = 2000
CMR_FILE_URL = CMR_URL + '/search/granules.json?provider=NSIDC_ECS&sort_key=short_name' + \
    '&page_size=' + str(CMR_PAGE_SIZE)


def get_credentials():
    try:
        info = netrc.netrc()
        username, account, password = info.authenticators(urlparse(CMR_URL).hostname)
    except:
        try:
            username = raw_input("Earthdata username: ")
        except:
            username = input("Earthdata username: ")
        password = getpass("password: ")
    credentials = ('%s:%s' % (username, password))
    credentials = base64.b64encode(credentials.encode('ascii')).decode("ascii")
    return credentials


def cmr_download(urls):
    try:
        if not isinstance(urls, list) or len(urls) == 0:
            return
    except:
        return

    print(('Downloading %d files' % (len(urls), )))
    credentials = None

    for url in urls:
        if credentials == None and urlparse(url).scheme == 'https':
            credentials = get_credentials()

        filename = url.split('/')[-1]
        print('Downloading ' + filename)

        try:
            # In Python 3 we could eliminate the opener and just do 2 lines:
            # resp = requests.get(url, auth=(username, password))
            # open(filename, 'wb').write(resp.content)
            req = Request(url)
            if credentials != None:
                req.add_header('Authorization', 'Basic %s' % credentials)
            opener = build_opener(HTTPCookieProcessor())
            data = opener.open(req).read()
            open(filename, "wb").write(data)
        except IOError as e:
            if hasattr(e, 'code'):  # HTTPError
                print(('HTTP error code: %d' % e.code))
            elif hasattr(e, 'reason'):  # URLError
                print('HTTP cannot connect: ' + e.reason)
            else:
                raise
        except KeyboardInterrupt:
            return


def cmr_filter_urls(searchResults):
    if 'feed' not in searchResults or 'entry' not in searchResults['feed']:
        return None
    
    entries = searchResults['feed']['entry']
    if len(entries) == 0:
        return None

    urls = []
    # Filter out filename duplicates (use a dict for O(1) lookups)
    urlDup = dict()

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
            if filename not in urlDup:
                urls.append(link['href'])
                urlDup[filename] = True

    return urls


def cmr_search(collectionAuthId, collectionVersionId, temporalLowerBound, temporalUpperBound,
               boundingBox='', polygon='',
               granuleFilter=''):
    params = "&short_name=" + collectionAuthId
    desiredPadLength = 3
    padding = ""
    while len(collectionVersionId) <= desiredPadLength:
        params += "&version=" + padding + collectionVersionId
        desiredPadLength -= 1
        padding += "0"
    params += "&temporal[]=" + temporalLowerBound + "," + temporalUpperBound
    if polygon is not '':
        params += "&polygon=" + polygon
    elif boundingBox is not '':
        params += "&bounding_box=" + boundingBox
    if granuleFilter is not '':
        params += "&producer_granule_id[]=" + granuleFilter + \
            "&options[producer_granule_id][pattern]=true"
    print(CMR_FILE_URL + params)
    scroll = '&scroll=true'
    cmrScrollID = None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urls = []
        while True:
            req = Request(CMR_FILE_URL + params + scroll)
            if cmrScrollID != None:
                req.add_header('CMR-Scroll-Id', cmrScrollID)
            response = urlopen(req, context=ctx)
            if cmrScrollID == None:
                # Python 2 and 3 have different case for the http headers
                headers = dict()
                for k, v in dict(response.info()).items():
                    headers[k.lower()] = v
                cmrScrollID = headers['cmr-scroll-id']
                hits = int(headers['cmr-hits'])
                if hits > 0:
                    print(('Found %d matches, retrieving URLs' % (hits, )))
                else:
                    print('Found no matches')
            searchResults = response.read()
            searchResults = json.loads(searchResults)
            urlScrollResults = cmr_filter_urls(searchResults)
            if urlScrollResults == None:
                break
            if hits > CMR_PAGE_SIZE:
                print('.', end='')
                sys.stdout.flush()
            urls += urlScrollResults

        if hits > CMR_PAGE_SIZE:
            print()
        return urls
    except IOError as e:
        print(e)
        return None
    except KeyboardInterrupt:
        return


# Supply some default search parameters, just for testing purposes.
# These are only used if the parameters aren't filled in up above.
if 'collectionAuthId' in collectionAuthId:
    collectionAuthId = 'MOD10A2'
    collectionVersionId = '6'
    temporalLowerBound = '2001-01-01T00:00:00Z'
    temporalUpperBound = '2019-03-07T22:09:38Z'
    boundingBox = '-180,-90,180,90'
    polygon = '-109,37,-102,37,-102,41,-109,41,-109,37'
    granuleFilter = '*A2019*'  # '*2019010204*'

def main():

    urls = cmr_search(collectionAuthId, collectionVersionId, temporalLowerBound, temporalUpperBound,
                      boundingBox=boundingBox, polygon=polygon, granuleFilter=granuleFilter)

    cmr_download(urls)


if __name__ == '__main__':
    main()
