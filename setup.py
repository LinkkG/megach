# -*- coding: utf-8 -*-
"""Setup file"""
from distutils.core import setup
import megach

url = "https://github.com/LinkkG/megach/"

setup(
        name = "megach",
        author = "Link (LinkkG) Arias Martínez",
        author_email = "supermegamaster32@gmail.com",
        description = "A library to connect to multiple Chatango rooms.",
        url = url,
        download_url = url + "/archive/master.zip",
        license = "GNU General Public License v3.0",
        py_modules = ["megach"],
        version = megach.version,
        )
