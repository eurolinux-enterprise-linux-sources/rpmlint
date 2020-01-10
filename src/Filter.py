# -*- coding: utf-8 -*-
#############################################################################
# File          : Filter.py
# Package       : rpmlint
# Author        : Frederic Lepied
# Created on    : Sat Oct 23 15:52:27 1999
# Version       : $Id: Filter.py 1686 2009-11-05 20:08:59Z scop $
# Purpose       : filter the output of rpmlint to allow exceptions.
#############################################################################

import textwrap

import Config
try:
    import Testing
except ImportError:
    Testing = None


_diagnostic = list()
_badness_score = 0
printed_messages = { "I": 0, "W": 0, "E": 0 }

def printInfo(pkg, reason, *details):
    _print("I", pkg, reason, details)

def printWarning(pkg, reason, *details):
    _print("W", pkg, reason, details)

def printError(pkg, reason, *details):
    _print("E", pkg, reason, details)

def _print(msgtype, pkg, reason, details):
    global printed_messages, _badness_score, _diagnostics

    threshold = badnessThreshold()

    badness = 0
    if threshold >= 0:
        badness = Config.badness(reason)
        msgtype = badness and "E" or "W"

    ln = ""
    if pkg.current_linenum is not None:
        ln = "%s:" % pkg.current_linenum
    arch = ""
    if pkg.arch is not None:
        arch = ".%s" % pkg.arch
    s = "%s%s:%s %s: %s" % (pkg.name, arch, ln, msgtype, reason)
    if badness:
        s = s + " (Badness: %d)" % badness
    for d in details:
        s = s + " %s" % d
    if Testing and Testing.isTest():
        Testing.addOutput(s)
    else:
        if not Config.isFiltered(s):
            printed_messages[msgtype] += 1
            _badness_score += badness
            if threshold >= 0:
                _diagnostic.append(s + "\n")
            else:
                print (s)
                if Config.info:
                    printDescriptions(reason)
            return True

    return False

def printDescriptions(reason):
    try:
        d = _details[reason]
        if d and d != '' and d != "\n":
            print (textwrap.fill(d, 78))
            print ("")
    except KeyError:
        pass

def _diag_sortkey(x):
    xs = x.split()
    return (xs[2], xs[1])

def printAllReasons():
    threshold = badnessThreshold()
    if threshold < 0:
        return False

    global _badness_score, _diagnostic
    _diagnostic.sort(key = _diag_sortkey, reverse = True)
    last_reason = ''
    for diag in _diagnostic:
        if Config.info:
            reason = diag.split()[2]
            if reason != last_reason:
                if len(last_reason):
                    printDescriptions(last_reason)
                last_reason = reason
        print (diag)
    if Config.info and len(last_reason):
        printDescriptions(last_reason)
    _diagnostic = list()
    return _badness_score > threshold


_details = {}

def addDetails(*details):
    for idx in range(len(details)/2):
        _details[details[idx*2]] = details[idx*2+1]

def badnessScore():
    global _badness_score
    return _badness_score

def badnessThreshold():
    return Config.getOption("BadnessThreshold", -1)

# Filter.py ends here

# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
