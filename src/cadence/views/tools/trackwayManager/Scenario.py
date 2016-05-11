# Scenario.py
# (C)2016
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

import os

from llist import dllist
import csv

from cadence.analysis.shared.CsvWriter import CsvWriter

#_______________________________________________________________________________
class Scenario(object):
    """ This class supports reading, editing, and writing of CSV-format
        simulation files. A given sceneario is created and visualized in
        conjunction with the TrackwayManagerWidget. A data structure is
        composed of entries, each a dictionary representing a track's position,
        positional uncertainty, name, and UID.  New entries can be introduced,
        hypothetical tracks called proxies, and any entry can be individually
        modified (in position, etc.) or even removed to create a new specific
        scenario. The Scenario thus allows creating any sequence of
        quadrupedal tracks, either from actual trackway data or from scratch.
        This class has no dependence on either the Cadence database or Maya.
        However, a track-naming convention is a useful means to detect missing
        tracks that can be used to advantage here.  While it is not necessary
        that tracks have a non-empty name field, a sequential track-naming
        convention is useful to infer apparent missing tracks, e.g., given the
        sequence LP2, LP3, and LP5 for the left pes, LP4 is apparently missing.
        Without such an explicit sequence, missing tracks would only be
        apparent in the trackway spacing (either by visual inspection or by
        computation).  Since manus tracks are frequently missing, and presumably
        overprinted by a subsequently placed pes track, explicit track numbering
        allows proxy manus tracks to be placed under the corresponding pes
        tracks. Track sequence numbers are extracted from the name field, which
        corresponds to either the full fingerprint (a string consisting of the
        trackway 'CRO-500-2004-1-S-6' concatenated with '-' + 'L-M-5') or the
        simpler format 'LM5').  The UID is either that assigned earlier to the
        track or in the case of a proxy, the name with suffix '_proxy'.

        Sequential track numbering associates each pes track within a track
        sequence with its corresponding manus track in the vicinity (often found
        just ahead of that pes track, or partly (or completely) overprinted.
        This standard convention makes no assumption of where the left pes was
        when RM3 was laid down; LM3 might have occurred several complete step
        cycles after RM3 was created.  The numbers are simply a convention for
        defining a specific stride, or pace, etc.  For an extended trackway, one
        with multiple step cycles of left and right pes tracks, the numbering
        within a scenario will be consecutive within each the sequence for each
        limb (LM4, LM5, etc., as well as LP4, LP5, etc.).  The sequences for the
        four limbs may differ in length due to some tracks at the beginning or
        end of the trackway not being represented by either real or proxy
        tracks.  Moreover, a trackway scenario does not necessarily start on any
        given limb:  it may start on either the left or the right side, and with
        either a pes or a manus.  Finally, the "first" track would generally,
        but not necessarily be given the number 1. """

#===============================================================================
#                                                                     C L A S S
#

    PROXY_UNCERTAINTY_LOW      = 0.10
    PROXY_UNCERTAINTY_MODERATE = 0.25
    PROXY_UNCERTAINTY_HIGH     = 0.50

#_______________________________________________________________________________
    def __init__(self, trackway, path):
        """ A Scenario is built around the dictionary entries, which
            consists of four keys corresponding to the four limbs ('lp', 'rp',
            'lm', and 'rm').  The value associated with each key is a doubly-
            linked list (dllist) of entries, which comprise an ordered sequence
            of tracks.  Each entry is a dictionary of six key-value pairs:
            the name, uid, x, y, dx, and dy for a given track.  Each of the four
            sequences represents an an hypothesized sequence of tracks created
            by one limb ('lp', say).  Each track sequence can be edited to
            modify the contents of any entry, or to add/remove entries. """

        self.entries = dict(
            lp=dllist(),
            rp=dllist(),
            lm=dllist(),
            rm=dllist())

        self.trackway = trackway

        self.load(trackway, path)


#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def load(self, trackway, path):
        """ This reads a (CSV-format) scenario file, and builds self.scenario,
            a data structure that represents the four track sequences of a
            quadrupedal trackway (the left limb, etc.). During reading, each
            incoming row is a list of 24 strings, with the first 6 corresponding
            to the attributes name, uid, x, dx, y, and dy for the left pes, the
            next 6 to the right pes, and so forth.  Completely empty entries (6
            empty strings) are used to pad out a row if the corresponding limb
            had fewer tracks in that sequence than others. Since an non-empty
            entry might noneless have empty name and uid attributes, rely on
            x, dx, y, and dy to be non-empty strings for a valid entry. """

        # keep track of the current trackway (so that, even if it changes name
        # mid-sequence, it will be known with the trackway name with which it
        # starts
        self.trackway = trackway

        reader = csv.reader(open(os.path.expanduser(path)))

        # get the header row
        header = reader.next()

        # determine the number k of columns per each track (lp, rp, lm, rm)
        k = int((len(header) - 1)/4)

        # get the keys by splitting off the prefix for the first (lp) set
        keys = header[1:k+1]
        for i in range(k):
            keys[i] = keys[i].split('_')[1]

        for row in reader:
            for (limb, s) in [
                ['lp', row[1:k+1]],
                ['rp', row[k+1:2*k+1]],
                ['lm', row[2*k+1:3*k+1]],
                ['rm', row[3*k+1:4*k+1]]]:
                props = dict(zip(keys, s))
                # if not a filler, create an entry (an instance of dllistnode)
                # with links to next and prev, and value being the dictionary
                # containing the properties for that entry
                if props['x'] and props['dx'] and props['y'] and props['dy']:
                    # provide a suffix if it doesn't already have one
                    uid = props['uid']
                    if not (uid.endswith('_token') or uid.endswith('_proxy')):
                        props['uid'] = uid + '_token'
                    # turn the string numbers into floats
                    props['x']  = float(props['x'])
                    props['dx'] = float(props['dx'])
                    props['y']  = float(props['y'])
                    props['dy'] = float(props['dy'])
                    self.entries[limb].append(props)

#_______________________________________________________________________________
    def createPesProxies(self):
        """ This goes systematically filling gaps through the sequences of pes
            entries.  The new proxies are placed beside the first track by
            default, if they cannot be placed within the sequence.  The proxy's
            UID is the name with suffix '_proxy'. First, the beginning of the
            trackway has a first track number, called nMin.  At the end of the
            sequence there is a last track number, called nMax.  A complication
            is that the linked sequence might actually shift from one trackway
            to another, such as BEB-515-2009-1-S-21 becoming BEB-515-2006-1-S-3
            between LP34 of S21 and LP1 of S3.  To make matters worse, there is
            room for more tracks between these two.  We will start to repair
            this sequence by first trusting that the first track number, nMin,
            is to be filled for all limbs.  So, e.g., if nMin is 2 (due to some
            other limb starting at 2) and the first right manus track is RM4, a
            proxy will be created for RM2 and for RM3. Any gap repairs inside
            the sequence will be given the same trackway name as the last track
            before the gap. Next, at the other end of the sequence, any missing
            last tracks for any given limb (compared to nMax) wil be filled in
            with proxies so that each sequence reaches nMax. """

        nMin = self.getFirstTrackNumber()
        nMax = max(
            self.entries['lp'].size,
            self.entries['rp'].size,
            self.entries['lm'].size,
            self.entries['rm'].size)

        # find a default place to locate proxies
        (x0, y0) = self.firstTrackCoordinates()

        for limb in ['lp', 'rp']:
            left = limb[0] == 'l'

            # take note of the trackway; it might change name mid-sequence
            trackway = self.trackway

            # create proxies to fill any missing entries up to firstNode
            sequence = self.entries[limb]
            firstNode = sequence.first

            # If there is no first pes entry, create a whole sequence of
            # proxies from nMin to nMax.
            if not firstNode:
                for n in range(nMin, nMax + 1):
                    name = self.composeName(
                        n, left=left, pes=True, trackway=trackway)
                    props = {
                        'name'   :name,
                        'uid'    :name + '_proxy',
                        'x'      :x0,
                        'dx'     :self.PROXY_UNCERTAINTY_MODERATE,
                        'y'      :y0,
                        'dy'     :self.PROXY_UNCERTAINTY_MODERATE,
                        'assumed':True }
                    sequence.insert(props)
                continue

            # but since there is a first node, fill with proxies up to it
            for n in range(nMin, self.numberFromNode(firstNode)):
                name = self.composeName(
                    n, left=left, pes=True, trackway=trackway)
                props = {
                    'name':name,
                    'uid':name + '_proxy',
                    'x':x0,
                    'dx':self.PROXY_UNCERTAINTY_MODERATE,
                    'y':y0,
                    'dy':self.PROXY_UNCERTAINTY_MODERATE,
                    'assumed':True }
                sequence.insert(props, firstNode)

            # having added any necessary proxies up to firstNode, continue into
            # the sequence, looking for gaps to fill with proxies.
            thisNode  = firstNode
            nameParts = self.decomposeName(thisNode.value['name'])
            n         = nameParts['number']
            trackway  = nameParts['trackway']

            while thisNode.next:
                nextNode     = thisNode.next
                nameParts    = self.decomposeName(nextNode.value['name'])
                nextNumber   = nameParts['number']
                nextTrackway = nameParts['trackway']

                # if the next entry is actually a different trackway, just
                # continue on into it and don't try to find and fill gaps (they
                # they can be repaired later manually as necessary).
                if trackway != nextTrackway:
                    thisNode, n, trackway = nextNode, nextNumber, nextTrackway
                    continue

                # check to see if the next entry is consecutive
                if n == nextNumber - 1:
                    thisNode, n = nextNode, nextNumber
                    continue

                # so fill with proxies the gap of at least one in the sequence
                while n < nextNumber - 1:
                    n += 1
                    name = self.composeName(
                        n, left=left, pes=True, trackway=trackway)

                    # now compute its location (interpolate if a gap of one)
                    if nextNumber == n + 2:
                        x = 0.5*(thisNode.value['x'] + nextNode.value['x'])
                        y = 0.5*(thisNode.value['y'] + thisNode.value['y'])
                    else:
                        x = thisNode.value['x']
                        y = thisNode.value['y']
                    props = {
                        'name':name,
                        'uid':name + '_proxy',
                        'x':x,
                        'dx':self.PROXY_UNCERTAINTY_MODERATE,
                        'y':y,
                        'dy':self.PROXY_UNCERTAINTY_MODERATE,
                        'assumed':True }
                    thisNode = sequence.insert(props, nextNode)

#_______________________________________________________________________________
    def createManusProxies(self):
        """ This goes systematically through the manus entries filling gaps.
            The (x, y) coordinates are assigned based on the first track.  It
            fills proxies from nMin (the first track number in the trackway) to
            the first manus track (in either the left or right sequence), then
            any gaps in the sequence are filled, and any additional proxies are
            added after the last, up to nMax. """

        defaultUncertainty = self.PROXY_UNCERTAINTY_MODERATE

        nMin = self.getFirstTrackNumber()
        nMax = max(
            self.entries['lp'].size,
            self.entries['rp'].size,
            self.entries['lm'].size,
            self.entries['rm'].size)

        # find a default place to locate proxies
        x0, y0 = self.firstTrackCoordinates()

        for limb in ['lm', 'rm']:
            left = limb[0] == 'l'

            # take note of the trackway; it might change name mid-sequence
            trackway = self.trackway

            # create proxies to fill any missing entries up to firstNode, each
            # proxy to be placed under the corresponding pes (which requires
            # determining that pes name and getting its props, if it exists).
            sequence  = self.entries[limb]
            firstNode = sequence.first

            # If there is no first manus entry, create a whole sequence of
            # proxies from nMin to nMax.
            if not firstNode:
                for n in range(nMin, nMax + 1):
                    p = self.getProps(
                        # get the name of the presumed overprinting pes
                        self.composeName(n,
                                         left=left,
                                         pes=True,
                                         trackway=trackway))
                    name = self.composeName(
                        n, left=left, pes=False, trackway=trackway)
                    props = {
                        'name':name,
                        'uid':name + '_proxy',
                        'x':p['x'] if p else x0,
                        'dx':p['dx'] if p else defaultUncertainty,
                        'y':p['y'] if p else y0,
                        'dy':p['dy'] if p else defaultUncertainty,
                        'assumed':True}
                    sequence.append(props)
                continue

            # but since there is a first node, fill with proxies up to it
            for n in range(nMin, self.numberFromNode(firstNode)):
                p = self.getProps(
                self.composeName(n, left=left, pes=True, trackway=trackway))

                name = self.composeName(
                    n, left=left, pes=False, trackway=trackway)
                props = {
                    'name':name,
                    'uid':name + '_proxy',
                    'x':p['x'] if p else x0,
                    'dx':defaultUncertainty,
                    'y':p['y'] if p else y0,
                    'dy':defaultUncertainty,
                    'assumed':True }
                sequence.insert(props, firstNode)

            # having added any necessary proxies up to firstNode, continue down
            # the sequence, looking for gaps to fill with proxies.
            thisNode  = firstNode
            nameParts = self.decomposeName(thisNode.value['name'])
            n         = nameParts['number']
            trackway  = nameParts['trackway']

            while thisNode.next:
                nextNode     = thisNode.next
                nameParts    = self.decomposeName(nextNode.value['name'])
                nextNumber   = nameParts['number']
                nextTrackway = nameParts['trackway']

                # if the next entry is actually a different trackway, just
                # continue on into it and don't try to find and fill gaps (they
                # they can be repaired later manually as necessary).
                if trackway != nextTrackway:
                    thisNode = nextNode
                    n        = nextNumber
                    trackway = nextTrackway
                    continue
                # check to see if the next entry is consecutive
                if n == nextNumber - 1:
                    thisNode = nextNode
                    n        = nextNumber
                    continue

                # there is apparently a gap of at least one in the sequence
                while n < nextNumber - 1:
                    n += 1
                    name = self.composeName(
                        n, left=left, pes=False, trackway=trackway)

                    # find the position of the overprinting pes
                    pesName = self.composeName(
                        n,
                        left=left,
                        pes=True,
                        trackway=trackway)
                    p = self.getProps(pesName)
                    props = {'name':name,
                             'uid':name + '_proxy',
                             'x':p['x']  if p else x0,
                             'dx':defaultUncertainty,
                             'y':p['y']  if p else y0,
                             'dy':defaultUncertainty,
                             'assumed':True }
                    thisNode = sequence.insert(props, nextNode)

#_______________________________________________________________________________
    def completeSequences(self):
        """ When all sequences are finished, pad any that need additional
            entries so that they all have equal length. """

        nMax= max(
            self.numberFromNode(self.entries['lp'].last),
            self.numberFromNode(self.entries['rp'].last),
            self.numberFromNode(self.entries['lm'].last),
            self.numberFromNode(self.entries['rm'].last))

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            # determine where to start in completing this sequence

            entry    = sequence.last.value
            n        = int(self.decomposeName(entry['name'])['number'])
            left     = limb[0] == 'l'
            pes      = limb[1] == 'p'
            x        = entry['x']
            y        = entry['y']
            while n < nMax:
                n += 1
                name = self.composeName(n, left=left, pes=pes)
                props = {
                    'name':name,
                    'uid':name + '_proxy',
                    'x':x,
                    'dx':self.PROXY_UNCERTAINTY_MODERATE,
                    'y':y,
                    'dy':self.PROXY_UNCERTAINTY_MODERATE,
                    'assumed':True }
                sequence.append(props)

#_______________________________________________________________________________
    def getProps(self, name =None, uid =None):
        """ Either return the props corresponding to an entry of given name, or
            given uid, or None. """

        if name:
            for limb in ['lp', 'rp', 'lm', 'rm']:
                for entry in self.entries[limb]:
                    if entry['name'] == name:
                        return entry
        elif uid:
            for limb in ['lp', 'rp', 'lm', 'rm']:
                for entry in self.entries[limb]:
                    if entry['uid'] == uid:
                        return entry
        return None

#_______________________________________________________________________________
    def setProps(self, uid, props):
        """ All four sequences are searched until an entry is found matching the
            sought-after uid.  If none found, returns None.  Otherwise it
            replaces that entry with the dictionary props and returns True.  """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if not node:
                    print('setProps: node for limb=%s%s is null' % (limb, i))
                try:
                    if node.value['uid'] == uid:
                        sequence[i] = props
                        return True
                except:
                    self.printScenario()
                    print('screwed up')
        return None

#_______________________________________________________________________________
    def getFirst(self, uid):
        """ Given a UID, returns the first entry in that sequence, or None. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    return sequence.first
        return None

#_______________________________________________________________________________
    def getLast(self, uid):
        """ Given a UID, returns the last entry in that sequence, or None. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    return sequence.last
        return None

#_______________________________________________________________________________
    def getNode(self, uid):
        """ Given a UID, returns the Dllistnode for that entry, or None. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    return node
        return None

#_______________________________________________________________________________
    def getNextNode(self, uid):
        """ Given a UID, returns the next entry, or None. """

        node = self.getNode(uid)


        return node.next if node.value['uid'] == uid else None


#_______________________________________________________________________________
    def getPrevNode(self, uid):
        """ Given a UID, returns the previous entry, or None. """

        node = self.getNode(uid)

        return node.prev if node.value['uid'] == uid else None

#_______________________________________________________________________________
    def getFirstTrackNumber(self):
        """ Find the first track number in this trackway. """

        nMin = 1000
        lp0  = self.entries['lp'].first
        nMin = min(nMin, self.extractNumber(lp0.value['name'])) if lp0 else nMin

        rp0  = self.entries['rp'].first
        nMin = min(nMin, self.extractNumber(rp0.value['name'])) if rp0 else nMin

        lm0 = self.entries['lm'].first
        nMin = min(nMin, self.extractNumber(lm0.value['name'])) if lm0 else nMin

        rm0 = self.entries['rm'].first
        nMin = min(nMin, self.extractNumber(rm0.value['name'])) if rm0 else nMin

        return nMin

#_______________________________________________________________________________
    def firstTrackCoordinates(self):
        """ Find the location of the first track (in order of preference: LP,
            RP, LM, and finally RM).  Returns its pair of coordinates. """

        lp0 = self.entries['lp'].first
        if lp0:
            return lp0.value['x'], lp0.value['y']

        rp0 = self.entries['rp'].first
        if rp0:
            return rp0.value['x'], rp0.value['y']

        lm0 = self.entries['lm'].first
        if lm0:
            return lm0.value['x'], lm0.value['y']

        rm0 = self.entries['rm'].first
        if rm0:
            return rm0.value['x'], rm0.value['y']
        return 0.0, 0.0

#_______________________________________________________________________________
    def getEntries(self, tracks =True, proxies =True):
        """ Returns a list of entries, each a dictionary with keys name, uid, x,
            dx, y, and dy.  Tracks and/or proxies can be returned. """

        entries = list()

        for limb in ['lp', 'rp', 'lm', 'rm']:
            for entry in self.entries[limb]:
                if self.isProxy(entry) and proxies:
                    entries.append(entry)
                elif not self.isProxy(entry) and tracks:
                    entries.append(entry)
        return entries

#_______________________________________________________________________________
    def isProxy(self, entry):
        """ A proxy is an entry that has been explicitly added as such.  It is
            distinguished by either the uid ending in '_proxy' or because it
            is explicitly'assumed' """

        if entry and entry.has_key('uid'):
            return entry['uid'].endswith('_proxy')
        elif 'assumed' in entry and entry['assumed'] is not '':
            return True
        return False

#_______________________________________________________________________________
    def isToken(self, entry):
        """ A token is a scene object that represents a 'real' track (as opposed
            to a proxy). """

        return not self.isProxy(entry)

#_______________________________________________________________________________
    def printScenario(self):
        """ Prints all four track sequences. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            print('%s:' % limb)
            for entry in self.entries[limb]:
                print(entry)
            print()

#_______________________________________________________________________________
    def composeName(self, number, left =True, pes =True, trackway =None):
        """ For, e.g., pes=True, left=True and trackway='CRO-500-2004-1-S-6'),
            this returns 'CRO-500-2004-1-S-6-L-P-2'. Note that trackway defaults
            to the string for which the scenario was opened (a fine point, since
            some trackways change name mid-sequence.  If trackway is None, the
            simpler name 'L-P-2' is returned. To support consecutive numbering
            of proxies that are injected between integers, sometimes the number
            will be a floating point value.  In this case, format it with a
            decimal and one decimal place, otherwise format the number as an
            integer. """

        trackway = trackway if trackway else self.trackway

        # sometimes the number is a float; just deal with it
        if number - int(number) > 0.0:
            numberString = format('%.1f' % number)
        else:
            numberString = str(int(number))

        name = format('%s%s-%s-%s' % (
            trackway + '-' if trackway else '',
            'L' if left else 'R',
            'P' if pes else 'M',
            numberString))
        return name.upper()

#_______________________________________________________________________________
    def decomposeName(cls, name):
        """ Given, for example, 'CRO-500-2004-1-S-6-L-P-2', this returns a
            dictionary with the keys: pes, left, number, and trackway. In this
            example, trackway = CRO-500-2004-1-S-6, left = True, Pes = T, and
            number is the string '2'. """

        out = { 'number':None, 'pes':None, 'left':None, 'trackway':None }
        parts = name.split('-')
        if len(parts) == 9:
            out['trackway'] = format('%s-%s-%s-%s-%s-%s' % tuple(parts[0:6]))
            out['left']     = True if parts[6] == 'L' else False
            out['pes']      = True if parts[7] == 'P' else False
            out['number']   = float(parts[8].split('_')[0])
            return out
        elif len(parts) == 3:
            out['left']     = True if parts[0] == 'L' else False
            out['pes']      = True if parts[1] == 'P' else False
            out['number']   = float(parts[2].split('_')[0])
            return out
        else:
            print('decomposeName:  unrecognized format for name string')
            return None

#_______________________________________________________________________________
    def extractNumber(self, name):
        """ Extracts the track number from a name, such as the integer 2 in RP2.
            The name may either be a full fingerprint (e.g., the string
            CRO-500-2004-1-S-6-R-P-2) or the simpler string RP2. """

        if not name:
            return None

        parts = name.split('-')
        if len(parts) == 9:
            return int(parts[-1])
        if len(parts) == 1 and len(parts[0]) > 2:
            s = parts[0]
            side = s[0].upper()
            limb = s[1].upper()
            if (side == 'L' or side == 'R') and (limb == 'P' or limb == 'M'):
                return s[2:]

        return None

#_______________________________________________________________________________
    def numberFromNode(self, node):
        """ Given a node, this returns the integer number from its name.  Note
            that the number field is actually a one decimal space float, to
            allow for consecutive numbering of introduced proxies.  Here the
            number is returned as an int. """

        return int(self.decomposeName(node.value['name'])['number'])

#_______________________________________________________________________________
    def write(self, path):
        """ Writes the trackway scenario to csv format using CsvWriter.  Modeled
            after SimulationExporterStage. """
        fields = [
            'lp_name', 'lp_uid', 'lp_x', 'lp_dx', 'lp_y', 'lp_dy', 'lp_assumed',
            'rp_name', 'rp_uid', 'rp_x', 'rp_dx', 'rp_y', 'rp_dy', 'rp_assumed',
            'lm_name', 'lm_uid', 'lm_x', 'lm_dx', 'lm_y', 'lm_dy', 'lm_assumed',
            'rm_name', 'rm_uid', 'rm_x', 'rm_dx', 'rm_y', 'rm_dy', 'rm_assumed']
        csv = CsvWriter(autoIndexFieldName='Index', fields=fields)

        # pad out any sequences as necessary with empty entries.  There might
        # be fewer right manus tracks than left pes tracks, for instance.  In
        # the end, there will be as many rows created as the length of the
        # longest sequence.
        length = max(
            len(self.entries['lp']),
            len(self.entries['rp']),
            len(self.entries['lm']),
            len(self.entries['rm']))

        for index in range(length):
            items = []
            # for each of the four limbs ('lp', 'rp', 'lm', and 'rm') get the
            # sequence (list of dictionaries)
            for limb, sequence in self.entries.items():
                if index < len(sequence):
                    items += self.createEntry(
                        limb, props=sequence[index]).items()
                else:
                    items += self.createEntry(limb).items()
            csv.addRow(dict(items))

        if csv.save((os.path.expanduser(path))):
            print('writeSimFile:  Successfully wrote:', path)
        else:
            print('writeSimFile:  Unable to save CSV at "{}"'.format(path))


#_______________________________________________________________________________
    def createEntry(self, limb_id, props =None):
        """ Converts a scenario entry (a dictionary with keys 'name', 'url', 'x'
            'dx', 'y', and 'dy') into a simulation entry (a similar dictionary
            with the same keys but for particular 'limb_id' suffix, such as
            'lm_name' or 'rp_url'). """

        if props and 'assumed' not in props:
            props['assumed'] = True if props['uid'].endswith('_proxy') else ''
        return dict([
                (limb_id + '_x',       props['x'] if props else ''),
                (limb_id + '_dx',      props['dx'] if props else ''),
                (limb_id + '_y',       props['y'] if props else ''),
                (limb_id + '_dy',      props['dy'] if props else ''),
                (limb_id + '_name',    props['name'] if props else ''),
                (limb_id + '_uid',     props['uid'] if props else ''),
                (limb_id + '_assumed', props['assumed'] if props else '')])

#_______________________________________________________________________________
    def insertEntryBefore(self, uid, props):
        """ A new entry is created based on props, and inserted before the entry
            of given uid. First search for the entry for the given uid.  This
            approximates random access because any token might be selected. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    sequence.insert(props, node)
                    return True
        return None

#_______________________________________________________________________________
    def insertEntryAfter(self, uid, props):
        """ A new entry is created based on props, and inserted after the entry
            of given uid. First search for the entry for the given uid.  This
            approximates random access because any token might be selected. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    if node.next:
                        next = node.next
                        sequence.insert(props, next)
                    else:
                        sequence.append(props)
                    return True
        return None

#_______________________________________________________________________________
    def deleteEntry(self, uid):
        """ The entry whose uid is specified is deleted from the scenario,
            and returned, else None. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            sequence = self.entries[limb]
            length = len(sequence)
            for i in range(length):
                node = sequence.nodeat(i)
                if node.value['uid'] == uid:
                    return sequence.remove(node)

        return None

#_______________________________________________________________________________
    def setUncertainties(self, value, uidList =None, ):
        """ This sets the uncertainties dx and dy to the given value.  If
            uidlist is None, then all entries are set. """

        # if no uidList given, then set uncertainties for all entries
        if not uidList:
            for limb in ['lp', 'rp', 'lm', 'rm']:
                sequence = self.entries[limb]
                length = len(sequence)
                for i in range(length):
                    node = sequence.nodeat(i)
                    if node.value['uid'].endswith('_proxy'):
                        node.value['dx'] = value
                        node.value['dy'] = value
            return True
        # take each uid in the list and set the uncertainties for that entry
        for uid in uidList:
            node = self.getNode(uid)
            if node and node.value['uid'].endswith('_proxy'):
                node.value['dx'] = value
                node.value['dy'] = value
