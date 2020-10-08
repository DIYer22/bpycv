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
    exts = ["hdr", "exr"]

    def __init__(
        self,
        hdri_dir="./bpycv_hdri_cache",
        resolution="4k",
        category="all",
        download=False,
    ):
        """
        Download and manage hdri file from https://hdrihaven.com/hdris/

        Parameters
        ----------
        hdri_dir : str, optional
            hdri dir. The default is "./bpycv_hdri_cache".
        resolution : str, optional
            choice [1k, 2k, 4k, 8k, 16k, 19k]. The default is "4k".
        category : str, optional
            refer to https://hdrihaven.com/hdris/ side bar
            choice one [All, Outdoor, Architecture, Building, Europe, 
                        Field, Forest, Grass, Hill, Park, Path, River, 
                        Road, Rock, Sun1, Tree, View, Skies, Indoor, 
                        Studio, Nature, Urban, Night, Sunrise/Sunset, 
                        Morning/Afternoon, Midday, Clear, Partly Cloudy, 
                        Overcast, High Contrast, Medium Contrast, 
                        Low Contrast, Natural Light, Artificial Light]. 
            The default is "all".
        download : bool, optional
            If True, auto download from https://hdrihaven.com/hdris/ 
            by another threading using requesets.
            The default is False.
        """
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
        self.hdr_paths = sorted(
            sum(
                [
                    glob.glob(os.path.join(self.hdri_dir, f"*.{ext}"))
                    for ext in self.exts
                ],
                [],
            )
        )

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
        html = BeautifulSoup(page.text, features="html.parser")
        # '/hdri/?c=indoor&h=colorful_studio'
        hrefs = [a["href"] for a in html.find(id="item-grid").find_all("a")]

        names = [url2dict(href)["h"][0] for href in hrefs]

        #  'https://hdrihaven.com/files/hdris/tv_studio_4k.hdr'
        download_urls = [
            f"https://hdrihaven.com/files/hdris/{name}_{resolution}"  # + .hdr or .exr
            for name in names
        ]

        def download(url):
            fname = os.path.basename(url)
            file_path = os.path.join(hdri_dir, fname)
            for ext in self.exts:
                path = f"{file_path}.{ext}"
                if os.path.isfile(path):
                    return path
            for ext in self.exts:
                path = f"{file_path}.{ext}"
                downlaod_url = f"{url}.{ext}"
                r = rq.get(downlaod_url, timeout=5)
                if r.status_code != 200:
                    continue
                os.makedirs(hdri_dir, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(r.content)
                return path
            raise Exception(f"Con't download {file_path}")

        _urls = download_urls[:]
        random.shuffle(_urls)
        mapmt(download, _urls, pool=2)
        self.set_hdr_paths()
        self.downloading = False
        print("Download hdri threads has finished!")


if __name__ == "__main__":
    hdri_dir = "/tmp/hdri"
    hdri_dr = HdriManager(hdri_dir=hdri_dir, download=True)
    hdri = hdri_dr.sample()
    print(hdri)
