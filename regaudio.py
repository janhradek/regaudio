#!/usr/bin/env python
'''
Created on Mar 8, 2012

@author: Jan Hradek, jan.hradek@gmx.com

Requirements
- Python 3
- PyQt4
- SQLAlchemy
- SQLite
- numpy (diff)

Features
- filter tracks case insensitive, advanced filetring: !a:artist !n:name !r:rating
- groups, group selector, favorites (first in the selector)
- filter with groups
- advanced sorting - resorting sorted (remember previous sort and apply it after the new sort)
- context menu on tracks (the same as tracks menu)
- detele tracks (or group tracks)
- group management - add group (manually), rename group, remove group
- merge tracks (and retain links to groups)
- NOTE: merging tracks in the same group leads to duplicate grouptracks that share the same underlying track; in short, multiple tracks with the same name
- add track to group
- import group name
- import context menu: delete, reset, select existing, as new, sk -> a,n, a,n -> sk
- import delete row(s)
- import search key -> artist & name (and vice versa)
- import real searchkey
- import mm
- import should have some status containing number of tracks that are not yet selected or as new
- import window shouldnt continue  after enter is pressed (a problem with the groupname)
- ok button must be disabled if there are any tracks that arent selected or marked as new
- column sizes for importwindow
- import cue (gruop)
- time units
    - cuesheet has frames, everywhere else are seconds which themselves are inaccurate
    - it would be nice to have exact data type before moving on, datetime.time looks promising (immutable though)
    - datetime.time sucks for our purposes, store ms and convert them to and from string as needed (done?)
    - implement for import too
- import directory (group)
- stars for rating (it should support tracks in groups too)
- star for new (star vs circle?, there must be visible difference with rating)
- add new tracks to group
- delete tracks from group (not just grouptracks)
- ikona
- configuration file ~/.regaudio : currently only one configuration value: location of the db
- total number of pages
- import window - disable enter and esc to close the window
- automatically change groupname of import or provide an option to do so
- striping certain parts from names like "original mix"
- support flac, m4a (basic)
- tidy up the menus and shortcuts
- (any replacement to cfg)

v0.1.1:
+ import: nameCutToSearchKey - make new search key from track name, but remove any parenthesis and their contents (shortcut ")
+ import: found tracks now marks verbatim matches with a star **, ++ if search strings match
- import: fixed, cue files are expected to be in utf-8 but if they are not (on UnicodeDecodeError) latin1 is used
- merge: fixed, now the links between groups and tracks dont disappear

v0.1.2:
- import: fixed importing mp3 without track number
+ addtogroup: now supported for grouptracks (group mode) too
+ import: tracks column now displays best match indicators
+ track rating in tooltip is now displayed as a set of stars, plus and dashes
+ track and import tables now both have smaller row height and alternating row colors
+ import: it is now possible to directly select multiple cuesheets
+ import: select best ('B' key)
+ import: quick resolve (select best track for **, ++, create new for no match, the rest is left as is)
- tables: columns are now resized properly tanks to wordWrap=False
- both tables: removed grid
+ filter: now doesn't reset automatically, theres a button and menu entry for it
+ filter: a history of last 20 filter rules is now available
+ filter: new advanced filter option !g: allow query groups (by names), note that its also possible to use it with groups and therefore it is possible to query and intersection of groups
+ import: * + _ indicators now work by parts, artist and name are evaluated separately
- both tables: fixed context menu position

v0.1.3:
+ all tracks: pressing all tracks again will return to previous group
- delete: fixed the dialog message when deleting a track (not a group track)
- group filter: enabling group filter now focuses the filter editline
- in groups menu: groups are now listed alphabetically
- id3v1: id3v1 reader fixed
+ merge: now allowed in groupmode (maybe it's confusing)
+ group delete: deleting a group doesn't reset the group filter
+ sort: sorting grouptracks by number is remembered between all tracks/groups switches (so switching back and forth between groups and all tracks doesn't screw up the ordering)
+ status: reworked the status line, now it provides some basic statistics about the tracks (counts and ratings)
- adding tracks to a group with the same tracks already present didn't work (it was impossible to make duplicities except through import)
+ detachcopy: make a copy of a track in a group (grouptrack) and replace the current link in the group with it
+ relink: change the grouptrack to link to some other similar track

v0.1.4:
- migration to PyQt5

FIXME:
- import: import file/directory selection crashes the application
- import: saying no to name cleanup, cleans up the name anyway

TODO:
- (artist translator to help fix some issues with names)
- (import should do some things automaticaly - cleanup group name, cleanup track names)
- safe delete (introduce a new flag and set it instead of deletion, filter by it)
'''

import sys
import os
from PyQt5 import QtWidgets

from ui import mainWindow
import model.config # this will read the config

VERSION = 0.1.4

def main():
    app = QtWidgets.QApplication(sys.argv)
    window=mainWindow.MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
