'''
Created on May 7, 2012

@author: twider
'''

# set to True to debug
#_dd = False

def re_range(lst):
    '''
    turns a sorted list into a list of tuples - start, end, step     
    '''
    from numpy import diff
        
    #lst = [ 1, 3, 5, 7, 8, 9, 10, 11, 13, 15, 17 ]
    onediff, twodiff = diff(lst), diff(diff(lst))
    increments, breakingindices = [], []
    for i in range(len(twodiff)):
        if twodiff[i] != 0:
            breakingindices.append(i+2) # Correct index because of the two diffs
            increments.append(onediff[i]) # Record the increment for this section
    
    # Increments and breakingindices should be the same size
    tuples = []
    start = lst[0]
    for i in range(len(breakingindices)):
        tuples.append((start, lst[breakingindices[i]-1], increments[i]))
        start = lst[breakingindices[i]]
    tuples.append((start, lst[len(lst)-1], onediff[len(onediff)-1]))
    return tuples

def re_rangebyone(lst, count=False):
    '''
    turns a sorted list into a list of tuples - start, end where step is one
    if count is true return number of values instead of end     
    '''
    from numpy import diff

    onediff = diff(lst)
    breakingindices = []    
    for i in range(len(onediff)):
        if onediff[i] != 1:
            breakingindices.append(i+1) # Correct index because of the two diffs            
    
    # Increments and breakingindices should be the same size
    tuples = []
    start = lst[0]
    for i in range(len(breakingindices)):
        end = lst[breakingindices[i]-1]
        if count:
            end = end + 1 - start
        tuples.append((start, end))
        start = lst[breakingindices[i]]
    end = lst[len(lst)-1]
    if count:
        end = end + 1 - start
    tuples.append((start, end))
    return tuples

# to be filled from CFG
FILENAMEEXCEPTIONS = None

def filenametoinfo(fn, exceptionscfg=None, stripext=".mp3"):
    """
    reads [no, artist, name] information just from mp3 filename

    to be used for tracks where id3 doesn't have the required information
    returns a list - trackno, artist, name and sometimes a warez group at the end
    """

    import glob
    import os.path
    import re 

    #global _dd

    def processgroups(grps):
        """
        tidying up the strings
        """
        return [gr.replace("_", " ").strip() for gr in [no] + list(grps) if not gr is None]

    # WHERES NO ORDER, THERES NO HOPE, JUST STUMBLING ON STUPIDITY
    # yes its ugly, it works by dashes and the following list contains string to look for
    # and remove dashes of all such substrings. It may be somewhat dangerous but since
    # this whole thing is a fallback function I hope it will not backfire at me.
    # ... as you can see the list is somewhat long and shouldn't be processed in the way it is below
    # TODO it would probably be nice not tu run this first and see what we get and then use this only in 
    # "not very nice" cases
    global FILENAMEEXCEPTIONS
    if not FILENAMEEXCEPTIONS and exceptionscfg:
        from model.config import cfgvaltolistlist
        FILENAMEEXCEPTIONS = cfgvaltolistlist(exceptionscfg, extend=True)

    # fn may be absolute, get just the filename
    fn = fn.strip()
    dn = os.path.basename(os.path.dirname(fn))
    fn = os.path.basename(fn)

    # strip .mp3
    if fn.lower().endswith(stripext.lower()):#".mp3"):
        fn = fn[:-len(stripext)]#-4]

    # get (and strip) number at the beginning
    res = re.match(r"^(\d+)([-_. ]+)", fn)
    no = ""
    if res:
        no = res.group(1)
        fn = fn[len(res.group(0))]

    # the underscore is never a separator but a space replacement
    # the separator is mostly the dash (there may be two dashes)
    # some keywords may appear like ost, va

    # some dark magic (replace all known dash cases with underscores)
    fnl = fn.lower()
    for sunas in FILENAMEEXCEPTIONS: 
        if sunas in fnl:
            #fn = fn.replace(sunas, sunas.replace("-", "_"))
            fn = re.sub('(?i)' + re.escape(sunas), sunas.replace("-", "_"), fn)

    # the best case, everything by the scene rules [trackno]-[name]_-_[track]
    # (sadly this happens only in about 15% of all the cases :/ )
    # note: (?: means that the group is not part of groups 
    res = re.match(r"^(.+)_-_(.+?)(?:-([a-z0-9A-Z]+)|)$", fn)
    if res:
        return processgroups(res.groups())

    # the usual pattern is [trackno][sep][artist][sep][trackname]
    res = re.match(r"^(?:va-|ost-|)([^-]+?)[-_ ]+([^-]+)$", fn)
    if res:
        return processgroups(res.groups())

    # warez group might be last and separated by dash, (one word after dash at the end)
    res = re.match(r"^(?:va-|ost-|)([^-]+?)[-_ ]+([^-]+)[-]+([a-z0-9A-Z]+)$", fn)
    if res:
        return processgroups(res.groups())

    # in case of albums (ie. not compilation) the artist name could be missing
    # the track no in this case is always group of numbers followed by space or dot or dash etc.
    if no:
        res = re.match(r"^(?:va-|ost-|)([^-]+)$", fn)
        if res:
            return processgroups((dn ,res.group(1)))

        return processgroups((dn ,fn))

    # simple case: just one dash - [artist]-[track] no number
    res = re.match(r"^([^-]+?)-([^-]+)$", fn)
    if res:
        return processgroups(("", res.group(1), res.group(2)))

    # this is a fallback, dn - artist, fn - track
    return ["", dn, fn]

if __name__ == "__main__":
    with open("importmp3.testdata.txt", "r") as ft:
        for ll in ft:
            rr = filenameto(ll)
            if rr and len(rr) == 3:
                continue
            if rr:
                print(len(rr), list(reversed(rr)), os.path.basename(ll).strip(), os.path.basename(os.path.dirname(ll)))
            else:
                print(rr, os.path.basename(ll).strip(), os.path.basename(os.path.dirname(ll)))
