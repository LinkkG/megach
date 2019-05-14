#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: update_servers.py
Title: servers updater for megach
Original Author: milton797 http://milton797.chatango.com
"""
import json
import re
import urllib.request as urlreq
import zlib


class Updater:
    def __init__(self):
        print("-_-_-Updating Servers-_-_-\n")
        self.id_ = self.take_id()
        print("ID: {}\n".format(self.id_))
        self.servers = self.take_servers()
        print("Servers: {}\n".format(self.servers))
        print("\n-_-_-Finish-_-_-")

    @staticmethod
    def take_id():
        """
        Search ID for open servers url.
        """
        print("Getting ID")
        url = "http://st.chatango.com/cfg/nc/r.json"
        with urlreq.urlopen(url) as open_url:
            decode = open_url.read().decode("utf-8")
            data = json.loads(decode)
            key_name = list(data.keys())
            final_id = "{}{}".format(key_name[0], data[key_name[0]])
            return final_id or False

    def take_servers(self):
        """
        Search servers from link.
        """
        print("Getting Servers")
        if self.id_ is not False:
            url = "http://st.chatango.com/h5/gz/{}/id.html".format(self.id_)
            with urlreq.urlopen(url) as open_url:
                decode = open_url.read()
                if open_url.getheader("Content-Encoding") == "gzip":
                    data = zlib.decompress(decode, 47)
                else:
                    data = decode
                decompressed_data = data.decode("utf-8", "ignore")
                string_decompressed = str(decompressed_data)
                pattern = r"chatangoTagserver.*?({.+]}).*"
                string_re = re.findall(pattern, string_decompressed)[0]
                json_data = json.loads(string_re)
                tsweights = list()
                specials = list()
                for x, c in json_data["sm"]:
                    info_ws = json_data["sw"][c]
                    tsweights.append((x, info_ws))
                for x, c in dict(json_data["ex"]).items():
                    specials.append((x, c))
                return {"tsweights": tsweights, "specials": specials}
        else:
            return False


if __name__ == "__main__":
    Updater()
