'''
Module: adif
Parse an ADIF file.

This code has been written by KB8LFA and released in the Public Domain.
@license: Public Domain
'''

import re

def readfile(filename):
    fh = open(filename, 'r')
    content = fh.read()
    fh.close()
    return content

def adifFixup(rec):
    if rec.has_key('band') and not rec.has_key('band_rx'):
        rec['band_rx'] = rec['band']
    if rec.has_key('freq') and not rec.has_key('freq_rx'):
        rec['freq_rx'] = rec['freq']

def adiParse(filename):
    raw = readfile(filename)
 
    # Find the EOH, in this simple example we are skipping
    # header parsing.
    pos = 0
    m = re.search('', raw, re.IGNORECASE)
    if m != None:
        # Start parsing our ADIF file after the  marker
        pos = m.end()
 
    recs = []
    rec = dict()
    while 1:
        # Find our next field definition <...>
        pos = raw.find('<', pos)
        if pos == -1:
            return recs
        endPos = raw.find('>', pos)
 
        # Split to get individual field elements out
        fieldDef = raw[pos + 1:endPos].split(':')
        fieldName = fieldDef[0].lower()
        if fieldName == 'eor':
            adifFixup(rec)     # fill in information from lookups
            recs.append(rec)   # append this record to our records list
            rec = dict()       # start a new record
 
            pos = endPos
        elif len(fieldDef) > 1:
            # We have a field definition with a length, get it's
            # length and then assign the value to the dictionary
            fieldLen = int(fieldDef[1])
            rec[fieldName] = raw[endPos + 1:endPos + fieldLen + 1]
        pos = endPos
    return recs

# example
#def main():
#    recs = adiParse(sys.argv[1])
#    for rec in recs:
#        print rec
#    return
#
#if __name__ == '__main__':
#    main()
