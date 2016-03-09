# ScenarioManager.py
# (C)2018
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

import os

from llist import dllist
import csv

from cadence.analysis.shared.CsvWriter import CsvWriter

#_______________________________________________________________________________
class ScenarioManager(object):
    """ This class supports reading, editing, and writing of CSV-format
        simulation files. A given sceneario is created and visualized in
        conjunction with the TrackwayManagerWidget. A data structure is
        composed of entries, each representing a track's position, positional
        uncertainty, and some supplemental properties.  New entries can be
        introduced (hypothetical tracks called proxies), and any entry can be
        individually edited (in position, etc.) or even removed to create a new
        specific scenario. The ScenarioManager allows creating any sequence of
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
        track, or in the case of a proxy, the name with suffix '_proxy'.

        Sequential track numbering associates each pes track within a track
        sequence with a "corresponding" manus track in the vicinity (often found
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
# RESOURCE_FOLDER_PREFIX = ['tools']
#
#_______________________________________________________________________________
    def __init__(self):
        """ A ScenarioManager is built around the dictionary entries, which
            consists of four keys corresponding to the four limbs ('lp', 'rp',
            'lm', and 'rm').  The value associated with each key is a doubly-
            linked list (dllist) of entries, which comprise an ordered sequence
            of tracks.  Each entry is a dictionary of six key-value pairs:
            the name, uid, x, y, dx, and dy for a given track.  Each of the four
            sequences represents an an hypothesized sequence of tracks created
            by one limb ('lp', say).  Each track sequence can be edited to
            modify the contents of any entry, or to add/remove entries. """

        self.scenario = dict(
            lp=dllist(),
            rp=dllist(),
            lm=dllist(),
            rm=dllist())

        self.trackway = None

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def loadScenario(self, trackway, path):
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

        self.trackway = trackway

        reader = csv.reader(open(os.path.expanduser(path)))
        reader.next() # skip over the header row

        for row in reader:
            for (limb, s) in [
                ['lp', row[1:7]],
                ['rp', row[7:13]],
                ['lm', row[13:19]],
                ['rm', row[19:25]]]:
                (name, uid, x, dx, y, dy) = s
                # if not a filler, create an entry (an instance of dllistnode)
                if x and dx and y and dy:
                    props = dict(
                        [('name', name),
                         ('uid',  uid),
                         ('x',    float(x)),
                         ('dx',   float(dx)),
                         ('y',    float(y)),
                         ('dy',   float(dy))])
                    self.scenario[limb].append(props)

#_______________________________________________________________________________
    def extractNumber(self, name):
        """ extracts the track number from a name, such as the integer 2 in RP2.
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
                return int(s[2:])

        return None

#_______________________________________________________________________________
    def createPesProxies(self):
        """ This goes systematically filling gaps through the sequences of pes
            entries.  The new proxies are placed beside the first track by
            default, if they cannot be placed within the sequence.  The proxy's
            UID is the name with suffix '_proxy'. """

        (nMin, nMax) = self.getNumberRange()
        (x0, y0)     = self.firstTrackPosition()

        for limb in ['lp', 'rp']:
            sequence = self.scenario[limb]
            left = limb[0] == 'l'
            for n in range(nMin, nMax + 1):
                inSequence = False
                for i in range(sequence.size):
                    node   = sequence.nodeat(i)
                    number = self.extractNumber(node.value['name'])
                    if number == n:
                        inSequence = True
                        break
                    if number > n:
                        (pNode, nNode) = (node.prev, node.next)
                        if pNode and nNode:
                            x = 0.5*(pNode.value['x'] + nNode.value['x'])
                            y = 0.5*(pNode.value['y'] + nNode.value['y'])
                        elif pNode:
                            (x, y) = (pNode.value['x'], pNode.value['y'])
                        elif nNode:
                            (x, y) = (nNode.value['x'], nNode.value['y'])
                        else:
                            (x, y) = (x0, y0 + n*0.1)
                        name = self.composeName(n, left=left, pes=True)
                        props = {
                            'name':name,
                            'uid':name + '_proxy',
                            'x':x,
                            'dx':0.1,
                            'y':y,
                            'dy':0.1 }
                        sequence.insert(props, node)
                        inSequence = True
                        break
                if not inSequence: # then add to the end of the sequence
                    name = self.composeName(n, left=left, pes=True)
                    props = {
                        'name':name,
                        'uid':name + '_proxy',
                        'x':x0,
                        'dx':0.1,
                        'y':y0,
                        'dy':0.1 }
                    sequence.append(props)

    #_______________________________________________________________________________
    def createManusProxies(self):
        """ This goes systematically through the manus entries filling gaps.
            The (x, y) coordinates are assigned based on the first track. """

        (nMin, nMax) = self.getNumberRange()
        (x0, y0)     = self.firstTrackPosition()

        for limb in ['lm', 'rm']:
            sequence = self.scenario[limb]
            left = limb[0] == 'l'
            for n in range(nMin, nMax + 1):
                inSequence = False
                for i in range(sequence.size):
                    node   = sequence.nodeat(i)
                    number = self.extractNumber(node.value['name'])
                    if number == n:
                        inSequence = True
                        break
                    if number > n:
                        pes   = self.composeName(n,pes=True, left=left)
                        p     = self.getProps(pes)
                        name  = self.composeName(n, pes=False, left=left)
                        props = {'name': name,
                                 'uid':  name + '_proxy',
                                 'x':    p['x']  if p else x0,
                                 'dx':   p['dx'] if p else 0.1,
                                 'y':    p['y']  if p else y0,
                                 'dy':   p['dy'] if p else 0.1 }
                        sequence.insert(props, node)
                        inSequence = True
                        break
                if not inSequence:
                        pes   = self.composeName(n, pes=True, left=left)
                        p     = self.getProps(pes)
                        name  = self.composeName(n, pes=False, left=left)
                        props = {
                            'name': name,
                            'uid':  name + '_proxy',
                            'x':    p['x'] if p else x0,
                            'dx':   0.1,
                            'y':    p['y'] if p else y0,
                            'dy':   0.1 }
                        sequence.append(props)

#_______________________________________________________________________________
    def getProps(self, name =None, uid =None):
        """ Either return the props corresponding to an entry of given name, or
            given uid, or None. """

        if name:
            for limb in ['lp', 'rp', 'lm', 'rm']:
                for entry in self.scenario[limb]:
                    if entry['name'] == name:
                        return entry
        elif uid:
            for limb in ['lp', 'rp', 'lm', 'rm']:
                for entry in self.scenario[limb]:
                    if entry['uid'] == uid:
                        return entry
        return None

#_______________________________________________________________________________
    def setProps(self, uid, props):
        """ All four sequences are searched until an entry is found matching the
            sought-after uid.  If none found, returns None.  Otherwise it
            replaces that entry with the dictionary props.  """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            for entry in self.scenario[limb]:
                if entry['uid'] == uid:
                    entry = props
                    return entry
        return None

#_______________________________________________________________________________
    def getNumberRange(self):
        """ Find the range of track numbers over which the trackway in this
            scenario varies, and over which proxies might be required to fill
            in for missing tracks. """

        nMin = 1000
        lp0  = self.scenario['lp'].first
        nMin = min(nMin, self.extractNumber(lp0.value['name'])) if lp0 else nMin

        rp0  = self.scenario['rp'].first
        nMin = min(nMin, self.extractNumber(rp0.value['name'])) if rp0 else nMin

        lm0 = self.scenario['lm'].first
        nMin = min(nMin, self.extractNumber(lm0.value['name'])) if lm0 else nMin

        rm0 = self.scenario['rm'].first
        nMin = min(nMin, self.extractNumber(rm0.value['name'])) if rm0 else nMin

        nMax = -1000
        e = self.scenario['lp'].last
        nMax = max(nMax, self.extractNumber(e.value['name'])) if e else nMax

        e = self.scenario['rp'].last
        nMax = max(nMax, self.extractNumber(e.value['name'])) if e else nMax

        e = self.scenario['lm'].last
        nMax = max(nMax, self.extractNumber(e.value['name'])) if e else nMax

        e = self.scenario['rm'].last
        nMax = max(nMax, self.extractNumber(e.value['name'])) if e else nMax

        return nMin, nMax

#_______________________________________________________________________________
    def firstTrackPosition(self):
        """ Find the location of the first track (in order of preference, LP,
            RP, LM, and RM).  Returns the pair of coordinates. """

        lp0 = self.scenario['lp'].first
        if lp0:
            return lp0.value['x'], lp0.value['y']

        rp0 = self.scenario['rp'].first
        if rp0:
            return rp0.value['x'], rp0.value['y']

        lm0 = self.scenario['lm'].first
        if lm0:
            return lm0.value['x'], lm0.value['y']

        rm0 = self.scenario['rm'].first
        return rm0.value['x'], rm0.value['y']

#_______________________________________________________________________________
    def getEntries(self, tracks =True, proxies =True):
        """ Returns a list of entries, each a dictionary with keys name, uid, x,
            dx, y, and dy.  Tracks and/or proxies can be returned. """

        entries = list()

        for limb in ['lp', 'rp', 'lm', 'rm']:
            for entry in self.scenario[limb]:
                if self.isProxy(entry) and proxies:
                    entries.append(entry)
                elif not self.isProxy(entry) and tracks:
                    entries.append(entry)
        return entries

#_______________________________________________________________________________
    def isProxy(self, entry):
        """ A proxy is an entry that has been explicitly added as such.  It is
            distinguished by the UID ending in '_proxy'. """

        if entry and entry.has_key('uid'):
            return entry['uid'].endswith('_proxy')

#_______________________________________________________________________________
    def printTrackwayScenario(self):
        """ Prints all four track sequences. """

        for limb in ['lp', 'rp', 'lm', 'rm']:
            print('%s:' % limb)
            for entry in self.scenario[limb]:
                print(entry)
            print()

#_______________________________________________________________________________
    def composeName(self, number, pes =True, left=True, trackway =None):
        """ For, e.g., pes=True, left=True and trackway='CRO-500-2004-1-S-6'),
            this returns 'CRO-500-2004-1-S-6-L-P-2'. Note that trackway defaults
            to the string or which the scenario was opened.  If trackway is
            None, the simpler name 'L-P-2' is returned. """

        if not trackway:
            trackway = self.trackway

        name = format('%s%s-%s-%s' % (
            trackway + '-' if trackway else '',
            'L' if left else 'R',
            'P' if pes else 'M',
            number))
        return name.upper()

#_______________________________________________________________________________
    def decomposeName(self, name):
        """ Given, for example, 'CRO-500-2004-1-S-6-L-P-2', this returns a
            dictionary with keys pes, left, number, and trackway. """

        out = { 'number':None, 'pes':None, 'left':None, 'trackway':None }
        parts = name.split('-')
        if len(parts) == 9:
            out['trackway'] = format('%s-%s-%s-%s-%s-%s' % tuple(parts[0:6]))
            out['left']     = True if parts[6] == 'L' else False
            out['pes']      = True if parts[7] == 'P' else False
            out['number']   = parts[8].split['_'][0]
            return out
        elif len(parts) == 3:
            out['left']     = True if parts[0] == 'L' else False
            out['pes']      = True if parts[1] == 'P' else False
            out['number']   = parts[2].split['_'][0]
            return out
        else:
            print('decomposeName:  unrecognized format for name string')
            return None

#_______________________________________________________________________________
    def writeScenarioFile(self, path =None):
        """ Writes the trackway scenario to csv format using CsvWriter.  Modeled
            after SimulationExporterStage. """

        csv = CsvWriter(
            autoIndexFieldName='Index',
            fields=[
                'lp_name', 'lp_uid', 'lp_x', 'lp_dx', 'lp_y', 'lp_dy',
                'rp_name', 'rp_uid', 'rp_x', 'rp_dx', 'rp_y', 'rp_dy',
                'lm_name', 'lm_uid', 'lm_x', 'lm_dx', 'lm_y', 'lm_dy',
                'rm_name', 'rm_uid', 'rm_x', 'rm_dx', 'rm_y', 'rm_dy'])

        # pad out any sequences as necessary with empty entries.  There might
        # be fewer right manus tracks than left pes tracks, for instance.  In
        # the end, there will be as many rows created as the length of the
        # longest sequence.
        length = max(
            len(self.scenario['lp']),
            len(self.scenario['rp']),
            len(self.scenario['lm']),
            len(self.scenario['rm']))

        for index in range(length):
            items = []
            # for each of the four limbs ('lp', 'rp', 'lm', and 'rm') get the
            # sequence (list of dictionaries)
            for limb, sequence in self.scenario.items():
                if index < len(sequence):
                    items += self.createEntry(limb, props=sequence[index]).items()
                else:
                    items += self.createEntry(limb).items()
            csv.addRow(dict(items))

        # now
        if not path:
            path = (
                '~/Dropbox/A16/Simulation/data/' +
                self.trackway +
                '/modified.csv')

        if csv.save((os.path.expanduser(path))):
            print('writeSimFile:  Successfully wrote:', path)
        else:
            print('writeSimFile:  Unable to save CSV at "{}"'.format(path))


#_______________________________________________________________________________
    def createEntry(cls, limb_id, props =None):
        """ Converts a scenario entry (a dictionary with keys 'name', 'url', x
            dx, y, and dy) into a simulation entry (a similar dictionary with
            the same keys but for particular 'limb_id' suffix, such as 'lm_name'
            or 'rp_url'). """

        return dict([
            (limb_id + '_x',    props['x']    if props else ''),
            (limb_id + '_dx',   props['dx']   if props else ''),
            (limb_id + '_y',    props['y']    if props else ''),
            (limb_id + '_dy',   props['dy']   if props else ''),
            (limb_id + '_name', props['name'] if props else ''),
            (limb_id + '_uid',  props['uid']  if props else '')])


        # path2  = '~/Dropbox/A16/Simulation/data/' + fileName + '/modified.csv'
        # file2  = open(os.path.expanduser(path2),'w')
        # writer = csv.writer(file2)
        #
        # for row in rows:
        #     writer.writerow(row)
        #
        # file2.close()
        #
        # reader2 = csv.reader(file2)
        # print('now reading back again')
        # for row in reader2:
        #     print(row)
