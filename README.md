regaudio
========

regaudio is a python project to rate songs

It uses SQLite to store the data and QT as GUI. It's a Python 3 project.

I created this tool, because I listen to a lot of mix radio shows and I needed to note down the good tracks and know the bad ones too, not to be bothered by them again.

Features
--------

* tracks and groups
    * tracks are represented by an artist, a name, a rating and a new flag
    * groups group tracks as the user desires
    * each track can be in multiple groups
    * tracks in a group also have a number, a start time (from) and a length, all of them are optional, but number is recommended
    * groups can be marked as favorite in which case they appear at the top of the group list
* most of the operations are straightforward and pretty common (add, remove, rename etc.), but some might need an explanation
    * merge: merge is intended to solve duplicities - it takes the given tracks, lets user select one of them and replaces all their occurences in groups with the one selected
    * detach copy: this function only works in group mode - a copy of the track from the selected grouptrack is made and that grouptrack is linked to it (the original is detached and a copy is  used instead)
    * relink: works in group mode only - the track selected from the submenu is used as a track for the grouptrack selected in table
* for convenience tracks and groups can be filtered
    * tracks support simple filter and advanced filters
    * simple filter looks for the given term in both artist and name and displays any match
    * advanced filter filters the tracks part by part
        * !a: specifies artist,
        * !n: specifies name,
        * !r: specifies exact rating, use !r:< for rating lower than the given value and !r:> for rating higher than the given value,
        * !g: specifes the group, it can be used along with the group selector to find an intersection between groups
        * !\*: specifes the new flag
        * for example the advanced filter rule '!a:Beatles !n:Jane !*: !r:>9' will match any track that has "Beatles" as part of the artist name, "Jane" as part of the track name, has rating higher than 9 and is new
    * groups only support a simple filter
* configuration is stored in the file ~/.regaudio
    * it contains the location of the database and some values that configure the behavior of searching and import
    * default configuration is created if not present in which case a warning is also displayed
* groups can be imported, which is the easiest option to get started
    * supported inputs:
        * freemind mindmap .mm file (probably useless for anybody but the author)
        * cue files,
        * directories of mp3 files (ID3 tags are read)
        * support for m4a files and flac files is limited to filenames
    * importing is done in a separate import window which resembles the appearance of the main window to some extent
    * every imported track must be either
        * selected from already existing track (use the context menu)
        * or marked to be created as new (the new flag has nothing to do with that, its just up to the user what that flag means)
    * the match of imported track against any found existing track is indicated by two characters (\*,+,\_) next to the found track and the best match is indicated in a column next to the number of tracks found
        * there are two characters for each match, one for the artist and one for the track name
        * \* means verbatim (absolute) match
        * \+ means search match (both are first converted to the search strings and then compared)
        * \_ doesn't match at all
    * recommended import procedure
        1. suppose the import window has just appeared (the user has already picked the source - a directory or a cue file)
        1. press **Ctrl+A** select all the tracks
        1. press **"** key ie. name to searchkey (cut the parenthesis) - therefore the search will be done only on the raw track name without any additional information like remix etc.
        1. press **Q** ie. quick resolve - select the best track if there is a \*\*, \*+, +\*, ++ match or create as new if there were no tracks found or leave the imported track as it is
        1. resolve the rest of the tracks manually using context menu and keyboard shortcuts from it
        1. cleanup the group name by clicking button **Change...** and using some of the provided functions there
        1. if there's a problem with numbering (indicated in the status line by a string **!!NUMBERS!!**), try to use the function **Sanitize all track numbers** or fix them manually

Requirements
------------

* Linux (Unix) (might work on Windows though)
* Python 3
* PyQt5
* SQLAlchemy
* SQLite
* numpy (for diff)
* python-sip (for some tweaking some sip setting)

Licence
-------

see the LICENCE file
