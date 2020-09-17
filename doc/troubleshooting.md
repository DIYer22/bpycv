# Troubleshooting

<details>
<summary>
Python.h: No such file or directory when `pip install openexr`.
</summary>
<br/>

1. Find out the exact blender python version:
  - `/path/to/blender-2.90.0-linux64/2.90/python/bin/python3.7m -V`

2. Download and install the python header files from the official python homepage:
    - Open https://www.python.org/downloads/source/ in browser
    - download Gzipped source tarball from the exact same python version as your blender python version
    - `tar -xzf Python-3.7.9.tgz`
3. `cp Python-3.7.9/Include/* /path/to/blender-2.90.0-linux64/2.90/python/include/python3.7m/`

Reference: [Python.h missing in Blender Python?](https://blender.stackexchange.com/questions/81740/python-h-missing-in-blender-python)

</details>

<details>
<summary>
/usr/bin/ld: cannot find -lz when `pip install openexr`.
</summary>
<br/>

```
sudo apt-get install lib32z1-dev
```
Reference: [/usr/bin/ld: cannot find -lz](https://stackoverflow.com/questions/3373995/usr-bin-ld-cannot-find-lz)
</details>
