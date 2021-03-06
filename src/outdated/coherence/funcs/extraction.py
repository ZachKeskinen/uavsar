"""
Command line functions to download and unzip files from url
"""

import os
from os.path import join, basename, exists
from os import makedirs, linesep
import subprocess
from subprocess import PIPE, Popen
from glob import glob
import logging

def downloading(file, directory, ASF_USER, ASF_PASS):
    _log = logging.getLogger(basename(__file__))

    _log.info(f'Downloading {file}...')
    process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',directory], stderr=PIPE)
    started = False
    for line in process.stderr:
        line = line.decode("utf-8", "replace")
        if started:
            splited = line.split()
            if len(splited) == 9:
                percentage = splited[6]
                speed = splited[7]
                remaining = splited[8]
                print("Downloaded {} with {} per second and {} left.".format(percentage, speed, remaining), end='\r')
        elif line == os.linesep:
            started = True