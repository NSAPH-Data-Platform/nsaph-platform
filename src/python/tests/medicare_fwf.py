# -*- coding: utf-8 -*-
# Code to read file character by character, toss out bad chars/restructure line
import string as s

def get_next_character(f):
    """Reads one character at a time from a given text file"""
    c = f.read(1)
    while c:
        yield c
        c = f.read(1)


def clean_fwf_file(path, line_length, out_name='test.dat'):
    """
    Read a fixed width file that has bad line lengths character by character,
    remove new line characters, and output the result as
    a new fixed width file
    """
    f = open(path, 'r')
    out_file = open(out_name, 'w')
    remove = "\n`"
    out = ""
    weird = {}
    expected = s.ascii_letters + "0123456789" + " "

    for c in get_next_character(f):
        if c not in expected:
            if c in weird.keys():
                weird[c] += 1
            else:
                weird[c] = 0
        if c in remove:
            continue
        else:
            out = out + c

        if len(out) == line_length:
            out = out + "\n"
            out_file.write(out)
            out = ""
    try:
        assert out == ""
    except AssertionError as a:
        print(a)
        print("Finished iterating the file with leftover data, cleaning didn't work.")
        print(out)
    finally:
        f.close()
        out_file.close()
        print(weird)

