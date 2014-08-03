#!/usr/bin/env python
# coding=utf-8
import os
import sys
import sh
from sh import mediainfo, avconv, grep

WORKDIR = ''
FILE_EXT = '.MOV'
PID_PATH = '/var/run/iphone-video-rotate.pid'

def main():
    check_running()
    files = get_match_files()    
    for file in files:
        path = os.path.join(WORKDIR, file)
        if check_if_needed(path):
            convert(path)

def get_match_files():
    files = os.listdir(WORKDIR)
    match_files = []
    for file in files:
        if file[-4:] == FILE_EXT:
            match_files.append(file)
    return match_files

def check_if_needed(path):
    if path[-6:] == '_r.MOV':
        return False

    file_name, ext = os.path.splitext(path)

    conv_name = os.path.join(WORKDIR, file_name + '_r' + ext)

    if os.path.isfile(conv_name):
        return False

    try:
        result = grep(grep(mediainfo(path), i='Rotation'), '180')
    except sh.ErrorReturnCode_1 as e:
        return False

    return True

def convert( path ):
    path_dir = os.path.dirname(path)
    file_name, ext = os.path.splitext(path)
    
    print path
    avconv( '-i', path, '-vf', 'hflip,vflip', '-strict', 'experimental', os.path.join(path_dir, file_name + '_r' + ext))

def check_running():
    pid = str(os.getpid())
    if os.path.isfile(PID_PATH):
        test_pid = int(file(PID_PATH, 'r').read())
        try:
            os.kill(test_pid, 0)
        except OSError:
            file(PID_PATH, 'w').write(pid)
        else:
            print "%s already exists, exiting" % PID_PATH
            sys.exit()
    else:
        file(PID_PATH, 'w').write(pid)

if __name__ == '__main__':
    main()
