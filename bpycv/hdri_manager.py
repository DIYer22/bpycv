#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sun Jan 12 17:06:39 2020
"""
import boxx
from boxx import *
from boxx import os, setTimeout, mapmt, timegap, sleep, pathjoin

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
        debug=False,
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
        self.category = category.lower().replace("/", "-")
        self.hdri_dir = hdri_dir
        os.makedirs(hdri_dir, exist_ok=True)
        self.downloading = download
        self.debug = debug
        if self.downloading:
            print('Starting download ".hdr" file from "hdrihaven.com" in side threads')
            if debug:
                self.prepare()
            else:
                setTimeout(self.prepare)
        self.set_hdr_paths()

    def set_hdr_paths(self):
        self.all_paths = sorted(
            sum(
                [
                    glob.glob(os.path.join(self.hdri_dir, f"*.{ext}"))
                    for ext in self.exts
                ],
                [],
            )
        )
        assert self.downloading or len(self.all_paths)
        if not len(self.all_paths):
            self.hdr_paths = []
            return
        if self.category == "all":
            self.hdr_paths = sorted(self.all_paths)
            return

        listt = []
        for path in self.all_paths:
            fname = boxx.filename(path)
            name = fname.split(".")[0]
            listt.append(
                dict(
                    name=name,
                    res=name.split("_")[-1],
                    cats=fname.split(".")[1].split("="),
                    tags=fname.split(".")[2].split("="),
                    path=path,
                )
            )
        self.df = boxx.pd.DataFrame(listt)
        hdr_paths = self.df[self.df.cats.apply(lambda cats: self.category in cats)].path
        self.hdr_paths = sorted(hdr_paths)

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
        hrefs = [a["href"] for a in html.find(id="item-grid").find_all("a")]

        names = [url2dict(href)["h"][0] for href in hrefs]

        #  'https://hdrihaven.com/files/hdris/tv_studio_4k.hdr'
        def download(name):
            t = 60
            while 1:
                try:
                    if self.debug:
                        print(name)
                    prefix = f"{name}_{resolution}"
                    paths = boxx.glob(os.path.join(hdri_dir, prefix + "*"))
                    if len(paths):
                        return paths[0]
                    url = f"https://hdrihaven.com/hdri/?h={name}"
                    html = BeautifulSoup(
                        rq.get(url, timeout=5).text, features="html.parser",
                    )
                    href = [
                        a["href"]
                        for a in html.find_all("a")
                        if f"_{resolution}." in a.get("href")
                    ][0]
                    cats = [
                        a.text
                        for a in html.find(text="Categories:").parent.parent.find_all(
                            "a"
                        )
                    ]
                    tags = [
                        a.text
                        for a in html.find(text="Tags:").parent.parent.find_all("a")
                    ]
                    name = f"{prefix}.{'='.join(cats)}.{'='.join(tags)}.{href[-3:]}"

                    path = pathjoin(hdri_dir, name)
                    r = rq.get(href, timeout=5)
                    assert r.status_code == 200
                    os.makedirs(hdri_dir, exist_ok=True)
                    with open(path, "wb") as f:
                        f.write(r.content)
                    return path
                except AssertionError:
                    print(f"r.status_code = {r.status_code}, sleep({t})")
                    sleep(t)
                    t *= 2
                except Exception as e:
                    if self.debug:
                        boxx.pred - name
                        boxx.g()
                    raise e

        _names = names[:]
        random.shuffle(_names)
        if self.debug:
            list(map(download, _names,))
        else:
            mapmt(download, _names, pool=1)
        self.set_hdr_paths()
        self.downloading = False
        print("Download hdri threads has finished!")

    @classmethod
    def test(cls):
        hdri_dir = "/tmp/hdri"
        hm = HdriManager(
            hdri_dir=hdri_dir, category="indoor", download=False, debug=True
        )
        for i in range(10):
            hdri = hm.sample()
            print(hdri)
            assert hm.category in hdri
        boxx.g()


if __name__ == "__main__":
    hdri_dir = "/tmp/hdri"
    hm = HdriManager(hdri_dir=hdri_dir, download=True, debug=True)
    hdri = hm.sample()
    print(hdri)
