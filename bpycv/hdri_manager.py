#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sun Jan 12 17:06:39 2020
"""

from boxx import *
from boxx import os, setTimeout, mapmt, timegap, sleep

import random
import glob

from bs4 import BeautifulSoup
import requests
import urllib.parse as urlparse

bs = BeautifulSoup
rq = requests


def url2dict(url):
    parsed = urlparse.urlparse(url)
    return urlparse.parse_qs(parsed.query)


class HdriManager:
    def __init__(
        self,
        hdri_dir="./bpycv_hdri_cache",
        resolution="4k",
        category="all",
        download=False,
    ):
        self.resolution = resolution
        self.category = category
        self.hdri_dir = hdri_dir
        os.makedirs(hdri_dir, exist_ok=True)
        self.downloading = download
        if self.downloading:
            print('Starting download ".hdr" file from "hdrihaven.com" in side threads')
            setTimeout(self.prepare)
        self.set_hdr_paths()

    def set_hdr_paths(self):
        self.hdr_paths = sorted(glob.glob(os.path.join(self.hdri_dir, "*.hdr")))

    def __len__(self):
        if self.downloading:
            self.set_hdr_paths()
        return len(self.hdr_paths)

    def __getitem__(self, i):
        if self.downloading:
            self.set_hdr_paths()
        return self.hdr_paths[i]

    def sample(self):
        if self.downloading:
            self.set_hdr_paths()
        while not len(self.hdr_paths):
            assert (
                self.downloading
            ), f'No hdri file in "{self.hdri_dir}", make sure HdriManager(download=True)'
            self.set_hdr_paths()
            if timegap(5, 'waiting for download ".hdr" file'):
                print('Waiting for download first ".hdr" file....')
            sleep(0.1)
        return random.choice(self.hdr_paths)

    def prepare(self,):
        resolution = self.resolution
        category = self.category
        hdri_dir = self.hdri_dir
        url = f"https://hdrihaven.com/hdris/category/?c={category}"
        page = rq.get(url, timeout=5)
        html = BeautifulSoup(page.text)
        # '/hdri/?c=indoor&h=colorful_studio'
        hrefs = [a["href"] for a in html.find(id="item-grid").find_all("a")]

        names = [url2dict(href)["h"][0] for href in hrefs]

        #  'https://hdrihaven.com/files/hdris/tv_studio_4k.hdr'
        download_urls = [
            f"https://hdrihaven.com/files/hdris/{name}_{resolution}.hdr"
            for name in names
        ]

        def download(url):
            fname = os.path.basename(url)
            path = os.path.join(hdri_dir, fname)
            if not os.path.isfile(path):
                content = rq.get(url, timeout=5).content
                os.makedirs(hdri_dir, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(content)
            return path

        _urls = download_urls[:]
        random.shuffle(_urls)
        mapmt(download, _urls, pool=2)
        self.set_hdr_paths()
        self.downloading = False
        print("Download hdri threads has finished!")


if __name__ == "__main__":
    hdri_dir = "/tmp/hdri"
    hdri_dr = HdriManager(hdri_dir=hdri_dir, category="indoor", download=True)
    hdri = hdri_dr.sample()
    print(hdri)
