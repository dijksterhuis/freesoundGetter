#!/usr/bin/env python3

import freesound
import requests
import argparse
#import toml
import sys
import os
import datetime
import string

from .secrets import CLIENT_ID
from .secrets import CLIENT_SECRET

from .API import OAuth
from .API import FreesoundWrapper
from .API import Throttling

from .Query import Query
from .Query import Arguments

def main():
    args = Arguments()
    query = Query(args.build())
    auth = OAuth(CLIENT_ID, CLIENT_SECRET)
    fs = FreesoundWrapper(auth.oauth())
    fs.search(query).get_all(os.path.join(os.getenv("HOME"), "Downloads/freesound/"))
    
if __name__ == '__main__':
    main()
