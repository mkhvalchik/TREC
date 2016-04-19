#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line example for Custom Search.
Command-line application that does a search.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pprint

from googleapiclient.discovery import build


def main():
  # Build a service object for interacting with the API. Visit
  # the Google APIs Console <http://code.google.com/apis/console>
  # to get an API key for your own application.
  service = build("customsearch", "v1",
            developerKey="AIzaSyDBh9qkTpuXSWbsjCfnCTQJFuFGKOYCElM")

  res = service.cse().list(
      q='(hamburger OR "ground beef") AND (cold) AND (heat OR inflame) AND (What) AND (manner OR means OR direction)',
      cx='000504779742960611072:dpmv5fihhu8',
    ).execute()
  #pprint.pprint(res)

  print [item['link'] for item in res['items']][:10]

if __name__ == '__main__':
  main()
