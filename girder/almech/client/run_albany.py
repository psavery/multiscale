#!/usr/bin/env python

import girder_client

API_URL = 'http://localhost:8080/api/v1'

if __name__ == '__main__':

    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser()

    parser.add_argument('-k', '--api-key',
                        help='A valid api key for accessing girder. '
                             'Alternatively, the environment variable '
                             '"GIRDER_API_KEY" may be set instead.')
    args = parser.parse_args()

    apiKey = args.api_key
    if not apiKey:
        apiKey = os.getenv('GIRDER_API_KEY')
        if not apiKey:
            sys.exit('An api key is required to run this script. '
                     'See --help for more info')

    gc = girder_client.GirderClient(apiUrl=API_URL)
    gc.authenticate(apiKey=apiKey)
