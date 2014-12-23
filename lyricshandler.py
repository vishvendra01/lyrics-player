"""This module all stuff related to lyrics or lrc"""
import re

def parse_lrc(data):
    tag_regex = R"(\[\d+\:\d+\.\d*\])"
    match = re.search(tag_regex, data)

    # no tags 
    if match is None:
        return (data, None)

    data = data  [match.start():]
    splitted = re.split(tag_regex, data)[1:]

    tags = []
    lyrics = ''
    for i in range(len(splitted)):
        if i % 2 ==  0:
            # tag
            tags.append( (time_to_seconds(splitted[i]),  splitted[i+1]) )
        else:
            # lyrics
            lyrics += splitted[i]
    return (lyrics, tags)


def time_to_seconds(time):
    time = time[1:-1].replace(":", ".")
    t = time.split(".")
    return 60 * int(t[0]) + int(t[1])