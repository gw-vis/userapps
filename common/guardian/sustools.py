#!/usr/bin/env python 
# Note: the shebang line above needs to invoke vanilla python (rather than Guardian, which is a python interpreter with stuff pre-loaded)
# so that when this module is used from the command line it can parse its own options and arguments.

## sustools.py - module for managing suspensions via EPICS/ezca, also callable from the command line (see main() at end).

# -*- mode: python -*-

## SVN $Id: sustools.py 12265 2015-12-11 01:40:50Z arnaud.pele@LIGO.ORG $

# Version history

# 8/9/13: Version 0 by Mark Barton.
# 8/10/13: Version 1.0
# 8/16/13: Version 1.1 - add magnet sign info; fix types for TMSX/Y (was HLTS!); 
#    added new helper methods genOutputSwitch etc enabling one-liner definitions for dampOutputSwitch etc;
#    fixed HLTS and separate out SR2 and SRM (to HSTS2) because they have SD OSEM on opposite side from E1100109-v2;
#    key susTypes on full prefix in case H1<>L1; fix manual mode methods to pass return value;
#    added provisions for test stands; fixed masterSwitch (had been using filter-style method);
#    defined SusError and replaced sys.exit() calls; reworked Sus.__init__() to add (SWITCH,ezca) option
# 8/27/13: Version 1.2: Changed 'chan' to 'pv' in many names; added lever arm info; 
#    added support for PV list output in Matlab cell array format and/or with a suffix and/or with full prefix;
#    added PV list functions for matrices
# 8/28/13: Version 1.3: reworked command line processing in terms of argparse rather than optparse
#    added support for more types to toMatlabString; renamed most commands to camelCase; added xxxxFilterSwitchRead commands;
#    added 'levelorder' field to each item in susTypes; made PV list methods use user-specified level order, or 'levelorder' when levels==[]
# 8/30/13: Version 1.4: added optional fakeguardian for off-line testing; fixed HTTS prefixes to have 'ASC-' not 'SUS-';
#    refactored many switch/numeric read/write methods in terms of more generic genNumWrite, genRead, genSwitch and genSwitchRead;
#    made -l etc have nargs='+' instead of '*'
# 9/4/13: Version 1.5: added support for writing lists of values to PVs; added methods for generating matrix PV lists; 
#    updated susData with default matrices for o2e, e2l, sensalign; moved ISI offload stuff into M0/M1 where it belonged;
#    extended filter block definition to have default gains; moved magnet signs into COILOUTF default gains
# 9/5/13: Version 1.6 add -x switch; rename toMatlabString to toMatlab.
# 10/4/13: Version 1.7 add -X switch; fix logic of -x, -X and command; change format of OSEM data in susData; 
#    add -k switch and data access methods.
# 10/4/13 Version 1.8 added "suspensionType" method (A.Pele)
# 11/8/13 Version 1.9 : modified HSTS/HSTSM/HSTS2/HSTS2M/HLTS dictionary : [levels][M3][test] = test3 instead of None. Modification has been tested for all of HSTS/HLTS (A.Pele)
# 11/12/13 Version 2.0 : support for WIT channels as added to Simulink by Jeff K (): added 'wit' entries and removed some 'damp' entries in susData, added new witPvs() function; updated import calls to look in susScriptDir for ezca or guardianScriptDir for guardian.ezca depending on init_thingy argument.
# 11/20/13: Version 2.1: fixed top level LOCK stuff by adding new 'lockdofs' entry with just L/P/Y (had been trying to access non-existent T/V/R). 
#    Renamed all EPICS read/write functions to have Read or Write in the name. 
#    Added new pair argument to most functions and new -pair switch to specify whether read/write functions should return PV, value, (PV,value) or nothing. 
#    Renamed RAMP=4096 bitmask to GRAMP (G=gain) and added ORAMP=8192 (O=offset). Extended genSwitchRead to accept a list of bit names (e.g., ['GRAMP','ORAMP']). 
#    Added new functions *OffsetRampingRead and *GainRampingRead (*=damp/test/lock/align). Added additional *GainRead functions for *=test/lock/align.
#    Fixed -x and -X to take multiple words of input. Allowed the keywords from -k to be applied to things in callableGlobals. Removed EUL2CART stuff.
#    Made Write functions return PV/values.
# 12/20/13: Version 2.2: Changed LHO HTTS data (but not yet LLO's) to reflect move from ASC to SUS.
# 1/9/14: Version 2.3: Added support for watchdogs: new fields in susType, new methods wdNames and trippedWDs
# 1/10/14: Version 2.4: Cleaned up and extended WD support: removed creating separate ezca object just for IOP WD chans 
#     (old one does the right thing if given a channel in form ':IOP-SUS_B123_DACKILL'); added WD info for all H1/L1;
#     improved trigger logic now ignores bypassed IOP DACKILL; 
# 1/15/14: Version 2.5 Added masterSwitchRead. Fixed bug: genRead and genGainRead should have been genNumRead.
# 1/16/14: Version 2.6 (Jamie) Fixed bug causing __TRAMP etc. Fixed prefix not set bug in initialization.
# 1/23/14: Version 2.7 Added 1 and True as synonyms for enable='ON' in genSwitchWrite and likewise for 0/False/'OFF';
#      tweaked Jamie's fix for __TRAMP (genNumWrite back to not supplying '_', calls should).
# 02/24/14 Version 2.8 Added a method for ISC block in order to turn off the output switch of length and angular control as well as (experimental) olOutputSwitchWrite for OL damping filters;
#      added alignOffsetRead(), alignOffsetSwitchRead(), fixed entry for OFFSET in cdsFiltMask (had said OUTPUT) 
# 03/14/14: Version 2.9 Changed L1 HTTS's from ASC to SUS.
# 03/17/14: Version 3. Added isc definition for TMTSs OMC and HAUX and HTTS with isc=None
# 04/21/14: Version 3.1 Deleted QUAD L3 WD from watchdog list.
# 04/29/14: Version 3.2 Revised OL stuff: changed olConfig items to distinguish 'inf' (with dofs P, Y and SUM) and 'full' (with dofs PIT, YAW and SUM). 
#      Added olSegPvs referencing SEG1/SEG2/etc. Added olRead and olSegRead. Added lots of susData entries for OLDAMP blocks, with method olDampPvs to access. 
#      Renamed Arnaud's olOutputSwitchWrite to olDampOutputSwitchWrite and got working.
# 06/27/14: Version 3.3 Stuart A, Added olDampRead for enabling capability of turning ON/OFF BS OpLev Damping.
# 07/02/14: Version 3.4 Stuart A & Joe B, Added capabiltiy to clear filter history.    
# To do:
# FIXME: Figure out how to include DRIVEALIGN.
# FIXME: Figure out how to include BIO switches.

# Import other useful modules
import os
import sys
import time

try:
    from ezca import Ezca
except ImportError:
    if susScriptDir not in sys.path:
        sys.path.append('/opt/rtcds/userapps/trunk/vis/common/scripts/')
    from fakeezca import Ezca

sleepTime = 0.0 # Time to allow after each EPICS write

# -------------------------------------------------------------------------------------------------
# Error class for SUS
class SusError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# -------------------------------------------------------------------------------------------------
# Class representing a single suspension. Can be initialized with a string, e.g., 'ITMX', or an instance of an Ezca object, or a (SYSTEM,ezca) tuple.
class Sus(object):
    '''
    A class representing suspensions to be manipulated via EPICs and the guardian.ezca module. For non-Guardian use, create an instance using the following pattern:
        itmy = Sus('ITMX')
    In a Guardian script there will be a global variable SYSTEM with a string like 'SUS-ITMX' and a global variable ezca with a Ezca instance. 
    Pick your poison:
        optic = Sus(ezca) # relies on interior details of the Ezca instance to determine what sort of SUS it refers to
    or
        optic = Sus((SYSTEM,ezca)) # blindly trusts that the SYSTEM string and the ezca object match, so don't ever not pass a matching pair!
    '''
    # -------------------------------------------------------------
    # Initialization
    def __init__(self, init_thingy, ifo=os.environ['IFO']):
        self.ifo=ifo.upper()

        if type(init_thingy) == str: # e.g., 'ITMY'
            self.name = init_thingy.upper() # e.g., 'ITMX' or 'HLTS05'
            try:
                data = susTypes[(self.ifo,self.name)]
            except:
                raise SusError('Unrecognized IFO:SUS type: '+self.ifo+':'+self.name)
            if type(data['type']) == str:
                try:
                    self.data = susData[data['type']]
                except:
                    raise SusError('Oops, value '+repr(data['type'])+' in susTypes not found as key in susData')
                self.system = 'SUS-'+self.name # e.g., 'SUS-ITMX' # FIXME allow for ASC
                self.prefix = self.ifo+':'+self.system+'_' # e.g., 'H1:SUS-ITMX_'
            elif type(data['type']) == tuple: # a tuple of (prefix, actual SUS type)
                prefix, realSusType = data['type']
                try:
                    self.data = susData[realSusType]
                except:
                    raise SusError('Oops, value '+repr(realSusType)+' in susTypes not found as key in susData')
                self.prefix = prefix # e.g., 'X1:SUS-HXTS_'
                self.system = 'SUS-'+prefix[3:-1] # e.g., 'SUS-HXTS' # FIXME allow for ASC
            # try using buildint ezca object, else create our own
            self.ezca = Ezca(self.prefix) # create our own Ezca instance with 'H1:SUS-ITMX_'-style prefix for ourselves
            self.watchdogs = data['watchdogs']

        elif True or isinstance(init_thingy, Ezca): # e.g. and i.e., ezca
            self.ezca = init_thingy # use Ezca instance passed in
            try:
                self.ezca.prefix # should exist if init_thingy is an instance of Ezca class, e.g., 'H1:SUS-ITMX_'
            except:
                raise SusError('Initializer for class Sus does not have a prefix property - not an Ezca.')
            self.prefix = self.ezca.prefix
            system, __ = self.ezca.prefix.split('_')
            __, self.name = system.split('-')  # e.g., 'ITMX'
            try:
                data = susTypes[(self.ifo,self.name)]
            except:
                raise SusError('The prefix of the ezca instance used for initialization, '+self.prefix+', does not appear to be for a recognized SUS')
            try:
                self.data = susData[data['type']]
            except:
                raise SusError('Oops, value '+repr(data['type'])+' in susTypes not found as key in susData')
            self.watchdogs = data['watchdogs']
                
        else:
            raise SusError('Unrecognized initializer for class Sus.')

    # -------------------------------------------------------------------------------------------------
    # Manual mode methods
    def switch(self, pv, setting, enable, verbose=False, pair='value', withprefix='bare', matlab=False):
        retval = self.ezca.switch(pv,setting,enable)
        time.sleep(sleepTime) # DEBUG
        result =  fmtpair(self.fmtprefix(withprefix)+pv,(setting,enable), pair)
        if matlab: return toMatlab(result)
        else: return result

    def write(self, pv, value, verbose=False, pair='none', withprefix='bare', matlab=False):
        self.ezca.write(pv,value)
        time.sleep(sleepTime) # DEBUG
        result = fmtpair(self.fmtprefix(withprefix)+pv,value, pair)
        if matlab: return toMatlab(result)
        else: return result

    def writelist(self, pvs, values, verbose=False, pair='none', withprefix='bare', matlab=False):
        if len(pvs)!=len(values):
            raise SusError('Number of values doesn\'t match number of channels')
        result = [
            fmtpair(self.fmtprefix(withprefix)+pv,self.write(pv,value, verbose=verbose), pair)
            for (pv,value) in zip(pvs,values)
        ]
        time.sleep(sleepTime) # DEBUG
        if matlab: return toMatlab(result)
        else: return result

    def read(self, pv, verbose=False, pair='value', withprefix='bare', matlab=False):
        result = self.ezca.read(pv)
        return fmtpair(self.fmtprefix(withprefix)+pv,result, pair)

    def readlist(self,pvs, verbose=False, pair='value', withprefix='bare'):
        result = [
            fmtpair(self.fmtprefix(withprefix)+pv,self.read(pv, verbose=verbose), pair)
            for pv in pvs
        ]
        if matlab: return toMatlab(result)
        else: return result

    # -------------------------------------------------------------
    # Watchdog methods

    # Return watchdog PV names
    def wdNames(self, levels=[], withprefix='bare', suffix='', verbose=False, pair='pv', matlab=False):
        allWds = self.watchdogs.keys()
        if levels==[]:
            wds = allWds
        else:
            wds = [wd.upper() for wd in levels if wd.upper() in allWds]
        result = []
        for wd in wds:
            pv = self.watchdogs[wd]
            if pv[0]==':': # fully qualified WD PV - don't try to respect withprefix setting
                pv=self.ifo+pv
                result.append(fmtwd(pv+suffix.upper(),wd,pair))
            else:
                result.append(fmtwd(self.fmtprefix(withprefix)+pv+suffix.upper(),wd,pair))
        if matlab: return toMatlab(result)
        else: return result

    # Return tripped watchdog names
    def trippedWds(self, levels=[], withprefix='full', suffix='', verbose=False, pair='value', matlab=False):
        allWds = self.watchdogs.keys()
        if levels==[]:
            wds = allWds
        else:
            wds = [wd.upper() for wd in levels if wd.upper() in allWds]
        result = []
        for wd in wds:
            pv = self.watchdogs[wd]
            trig = self.ezca.read(pv+'_STATE')
            if not ((pv[-7:]=='DACKILL' and (trig==1 or trig==2)) or (pv[-5:]=='WDMON' and trig==1)):
                if pv[0]==':': # fully qualified WD PV - don't try to respect withprefix setting
                    pv=self.ifo+pv
                    result.append(fmtwd(pv+suffix.upper(),wd,pair))
                else:
                    result.append(fmtwd(self.fmtprefix(withprefix)+pv+suffix.upper(),wd,pair))
        if matlab: return toMatlab(result)
        else: return result


    # -------------------------------------------------------------
    # Assorted informative methods
    def fmtprefix(self, withprefix):
        "Return requested version (withprefix = 'full', 'halfbare', 'bare') of PV prefix string."
        if withprefix=='full':
            return self.prefix 
        elif withprefix=='halfbare':
            return self.name+'_'
        elif withprefix=='bare':
            return ''
        else:
            return ''

    def levels(self, verbose=False, matlab=False):
        result = self.data['levelorder']
        if matlab: return toMatlab(result)
        else: return result

    def suspensionType(self, verbose=False, matlab=False):
        result = self.data['reallyis']
        if matlab: return toMatlab(result)
        else: return result

    def levelchannames(self, sensact, nametype, levels=[], chans=[], verbose=False, matlab=False):
        if levels==[]: ilevels = self.data['levelorder']
        else: ilevels = levels
        result = [
            chan
            for level in ilevels if self.data['levels'][level][sensact]
            for chan in self.data['levels'][level][sensact][nametype] if chans==[] or chan in chans
        ]
        if matlab: return toMatlab(result)
        else: return result


    def levelsensactdata(self, sensact, data, key, levels=[], verbose=False, matlab=False):
        if levels==[]: ilevels = self.data['levelorder']
        else: ilevels = levels
        if key==[]:
            result = [
                self.data['levels'][level][sensact][data]
                for level in ilevels if self.data['levels'][level][sensact]
            ]
        elif len(key)==1:
            result = [
                self.data['levels'][level][sensact][data][key[0]]
                for level in ilevels if self.data['levels'][level][sensact]
            ]
        elif len(key)==2:
            result = [
                self.data['levels'][level][sensact][data][key[0]][key[1]]
                for level in ilevels if self.data['levels'][level][sensact]
            ]
        elif len(key)==3:
            result = [
                self.data['levels'][level][sensact][data][key[0]][key[1]][key[2]]
                for level in ilevels if self.data['levels'][level][sensact]
            ]
        if matlab: return toMatlab(result)
        else: return result

    # Return osem sensitivity
    def osemData(self, key, levels=[], verbose=False, matlab=False):
	return self.levelsensactdata('osemConfig','osem',key, levels=levels, verbose=verbose, matlab=matlab)

    # Return coil driver sensitivity
    def coilDriverData(self, key, levels=[], verbose=False, matlab=False):
	return self.levelsensactdata('osemConfig','driver',key, levels=levels, verbose=verbose, matlab=matlab)

    # Return magnet sensitivity
    def magnetData(self, key, levels=[], withprefix='bare', suffix='', verbose=False, matlab=False):
	return self.levelsensactdata('osemConfig','magnet',key, levels=levels, verbose=verbose, matlab=matlab)

    # Return OSEM names
    def osemNames(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('osemConfig', 'chans', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # Return OSEM DOF names
    def osemDofs(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('osemConfig', 'dofs', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # Return OL names
    def olNames(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('olConfig', 'chans', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # Return OL DOF names
    def olDofs(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('olConfig', 'dofs', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # Return ESD names
    def esdNames(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('esdConfig', 'chans', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # Return ESD DOF names
    def esdDofs(self, levels=[], chans=[], withprefix='bare', suffix='', verbose=False, matlab=False):
        return self.levelchannames('esdConfig', 'dofs', levels=levels, chans=chans, verbose=verbose, matlab=matlab)

    # -------------------------------------------------------------
    # Generic utility methods for non-sensor/actuator specific matrix blocks such as CART2EUL

    # Return all element PVs for a non-sensor/actuator specific matrix block type such as CART2EUL 
    def levelmatrixblockpvs(self, block, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level] and self.data['levels'][level][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        result = []
        for level in ilevels:
            leveldata = self.data['levels'][level]
            ics = [ic for ic in leveldata[block]['inames'] if ichans==[] or ic in ichans] # input channels to be iterated over
            ocs = [oc for oc in leveldata[block]['onames'] if ochans==[] or oc in ochans] # input channels to be iterated over
            result+=[
                self.fmtprefix(withprefix)+level+'_'+leveldata[block]['blockname']+suffix+'_'+str(icn+1)+'_'+str(ocn+1)
                for icn in range(len(ics))
                for ocn in range(len(ocs))
            ]
        if matlab: return toMatlab(result)
        else: return result

    # Return element default values for a non-sensor/actuator specific matrix block type such as CART2EUL 
    def levelmatrixblockdefs(self, block, levels=[], ichans=[], ochans=[], verbose=False, suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level] and self.data['levels'][level][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level] and self.data['levels'][level][block]]
        result = []
        for level in ilevels:
            leveldata = self.data['levels'][level]
            ics = [ic for ic in leveldata[block]['inames'] if ichans==[] or ic in ichans] # input channels to be iterated over
            ocs = [oc for oc in leveldata[block]['onames'] if ochans==[] or oc in ochans] # input channels to be iterated over
            if leveldata[block]['default']==None: raise SusError('No defaults supplied for block '+str(block)+' at level '+str(level))
            result+=[
                float(leveldata[block]['default'][icn][ocn])
                for icn in range(len(ics))
                for ocn in range(len(ocs))
            ]
        if matlab: return toMatlab(result)
        else: return result

    # Read values for a non-sensor/actuator specific matrix block type such as CART2EUL 
    def levelmatrixblockread(self, block, levels=[], ichans=[], ochans=[], verbose=False, pair='value', withprefix='bare', suffix = '', matlab=False):
        pvs = self.levelmatrixblockpvs(block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix='bare', matlab=False)
        result = self.readlist(pvs, verbose=verbose)
        if matlab: return toMatlab(result)
        else: return result

    # Write values for a non-sensor/actuator specific matrix block type such as CART2EUL  
    def levelmatrixblockwrite(self, block, operation='none', value=0.0, array=[], levels=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', suffix = '', matlab=False):
        pvs = self.levelmatrixblockpvs(block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix='bare', matlab=False)
        if operation=='none':
            pass
        elif operation=='defaults':
            vals = self.levelmatrixblockdefs(block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, matlab=False)
        elif operation=='value':
            vals = [value for pv in pvs]
        elif operation=='array':
            if len(array)!=len(pvs): raise SusError('Length of array does not match number of channels ('+str(len(pvs))+')')
        self.writelist(pvs,vals, verbose=verbose)

    # -------------------------------------------------------------
    # Generic utility methods for sensor/actuator-specific matrix blocks such as OSEM2EUL

    # Return element PVs for a sensor/actuator specific matrix block type such as OSEM2EUL 
    def levelsensactmatrixblockpvs(self, sensact, block, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        result = []
        for level in ilevels:
            sensactdata = self.data['levels'][level][sensact]
            ics = [ic for ic in sensactdata[sensactdata[block]['inames']] if ichans==[] or ic in ichans] # input channels to be iterated over
            ocs = [oc for oc in sensactdata[sensactdata[block]['onames']] if ochans==[] or oc in ochans] # input channels to be iterated over
            result+=[
                self.fmtprefix(withprefix)+level+'_'+sensactdata[block]['blockname']+suffix+'_'+str(ocn+1)+'_'+str(icn+1)
                for icn in range(len(ics))
                for ocn in range(len(ocs))
            ]
        if matlab: return toMatlab(result)
        else: return result

    # Return element default values for a sensor/actuator specific matrix block type such as OSEM2EUL 
    def levelsensactmatrixblockdefs(self, sensact, block, levels=[], ichans=[], ochans=[], verbose=False, suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        result = []
        for level in ilevels:
            sensactdata = self.data['levels'][level][sensact]
            if sensactdata[block]['default']==None: raise SusError('No defaults supplied for block '+str(block)+' at level '+str(level))
            ics = [ic for ic in sensactdata[sensactdata[block]['inames']] if ichans==[] or ic in ichans] # input channels to be iterated over
            ocs = [oc for oc in sensactdata[sensactdata[block]['onames']] if ochans==[] or oc in ochans] # input channels to be iterated over
            result+=[
                float(sensactdata[block]['default'][ocn][icn])
                for icn in range(len(ics))
                for ocn in range(len(ocs))
            ]
        if matlab: return toMatlab(result)
        else: return result

    # Read values for a sensor/actuator specific matrix block type such as OSEM2EUL 
    def levelsensactmatrixblockread(self, sensact, block, levels=[], ichans=[], ochans=[], verbose=False, pair='value', withprefix='bare', suffix = '', matlab=False):
        pvs = self.levelsensactmatrixblockpvs(sensact,block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix='bare', matlab=False)
        result = self.readlist(pvs, verbose=verbose)
        if matlab: return toMatlab(result)
        else: return result

    # Write values for a sensor/actuator specific matrix block type such as OSEM2EUL 
    def levelsensactmatrixblockwrite(self, sensact, block, operation='none', value=0.0, array=[], levels=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', suffix = '', matlab=False):
        pvs = self.levelsensactmatrixblockpvs(sensact,block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix='bare', matlab=False)
        if operation=='none':
            pass
        elif operation=='defaults':
            vals = self.levelsensactmatrixblockdefs(sensact,block, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, matlab=False)
        elif operation=='value':
            vals = [value for pv in pvs]
        elif operation=='array':
            if len(array)!=len(pvs): raise SusError('Length of array does not match number of channels ('+str(len(pvs))+')')
        self.writelist(pvs,vals, verbose=verbose)

    # -----------------------------------------------------------------------------------------------------------
    # Generic methods for sensor/actuator-specific filter modules (OSEMINF, COILOUTF, etc)
    # (Only the PV and default values methods care whether a filter module is sensor/actuator-specific.)
    # Return all channel/DOF PVs for a sensor/actuator specific filter block type such as COILOUTF 
    def levelsensactfilterblockpvs(self, sensact, block, levels=[], chans=[], verbose=False, withprefix='bare', suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        result = [
            self.fmtprefix(withprefix)+level+'_'+self.data['levels'][level][sensact][block]['blockname']+'_'+chan+suffix
            for level in ilevels
            for chan in self.data['levels'][level][sensact][self.data['levels'][level][sensact][block]['names']] if (chans==[] or chan in chans)
        ]
        if matlab: return toMatlab(result)
        else: return result

    def levelsensactfilterblockdefs(self, sensact, block, levels=[], chans=[], verbose=False, suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        else: 
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][sensact] and self.data['levels'][level][sensact][block]]
        result = []
        for level in ilevels:
            sensactdata = self.data['levels'][level][sensact]
            cs = [c for c in sensactdata[sensactdata[block]['names']] if chans==[] or c in chans] # input channels to be iterated over
            if 'default' not in sensactdata[block].keys() or 'gains' not in sensactdata[block]['default'].keys():
                raise SusError('No defaults supplied for block '+str(block)+' at level '+str(level))
            result+=[
                float(sensactdata[block]['default']['gains'][cn])
                for cn in range(len(cs))
            ]
        if matlab: return toMatlab(result)
        else: return result

    # FIXME: add method to return defaults

    # Generic methods for non-sensor/actuator-specific filter modules (DAMP, TEST, etc)
    # (Only the PV and default values methods care whether a filter module is sensor/actuator-specific.)
    # Return all channel/DOF PVs for a non-sensor/actuator specific filter block type such as DAMP/TEST/LOCK/etc 
    def levelfilterblockpvs(self, block, levels=[], chans=[], verbose=False, withprefix='bare', suffix = '', matlab=False):
        if levels==[]: 
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level][block]]
        else:
            ilevels = [level for level in levels if level in self.data['levels'].keys() and self.data['levels'][level][block]]
        result = [ 
            self.fmtprefix(withprefix)+level+'_'+self.data['levels'][level][block]['blockname']+'_'+chan+suffix
            for level in ilevels
            for chan in self.data['levels'][level][self.data['levels'][level][block]['names']] if (chans==[] or chan in chans)
        ]
        if matlab: return toMatlab(result)
        else: return result

    # FIXME: add method to return defaults

    def witPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        if levels==[]:
            ilevels = [level for level in self.data['levelorder'] if self.data['levels'][level]['damp'] or self.data['levels'][level]['wit']]
        else:
            ilevels = [level for level in levels if level in self.data['levels'].keys() and (self.data['levels'][level]['damp'] or self.data['levels'][level]['wit'])]
        result = [] 
        for level in ilevels:
            if self.data['levels'][level]['damp']:
                for chan in self.data['levels'][level][self.data['levels'][level]['damp']['names']]:
                    if (chans==[] or chan in chans):
                        result.append(self.fmtprefix(withprefix)+level+'_'+self.data['levels'][level]['damp']['blockname']+'_'+chan+'_IN1'+suffix)
            else:
                for chan in self.data['levels'][level][self.data['levels'][level]['wit']['names']]:
                    if (chans==[] or chan in chans):
                        result.append(self.fmtprefix(withprefix)+level+'_'+self.data['levels'][level]['wit']['blockname']+'_'+chan+suffix)
        if matlab: return toMatlab(result)
        else: return result

    # -----------------------------------------------------------------------------------------------------------
    # Generic methods for all filter modules (DAMP, TEST, OSEMINF, COILOUTF)

    # Write filter numeric value (GAIN, TRAMP etc) - functions based on this should supply '_' in suffix, e.g., '_RAMP'
    def genNumWrite(self, pvfn, suffix, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        checkHaveLongVal(value)
        pvs = pvfn(levels=levels,chans=chans)
        result = [
            self.write(pv+suffix,value, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)
            for pv in pvs
        ] 
        if matlab: return toMatlab(result)
        else: return result

    # Read filter numeric value (GAIN, TRAMP etc) - functions based on this should supply '_' in suffix, e.g., '_RAMP'
    def genNumRead(self, pvfn, suffix, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        pvs = pvfn(levels=levels,chans=chans)
        result = [
            self.read(pv+suffix, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)
            for pv in pvs
        ]
        if matlab: return toMatlab(result)
        else: return result

    # Switch filter switches on or off (OUTPUT, INPUT, OFFSET etc) - functions based on this should NOT supply '_' in suffix, e.g., 'OFFSET'
    def genSwitchWrite(self, pvfn, suffix, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab = False):
        if enable==True or enable=='ON' or enable == 1:
            pvs = pvfn(levels=levels,chans=chans)
            result = [
                self.switch(pv, suffix,'ON', verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)
                for pv in pvs
        ]
        elif enable==False or enable=='OFF' or enable == 0:
            pvs = pvfn(levels=levels,chans=chans)
            result = [
                self.switch(pv, suffix,'OFF', verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)
                for pv in pvs
        ]
        else:
            pass # NC = no change
        if matlab: return toMatlab(result)
        else: return result

    # Read filter switch state (OUTPUT, INPUT, OFFSET etc) - functions based on this should NOT supply '_' in suffix, e.g., 'OFFSET'
    def genSwitchRead(self, pvfn, bits, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        if type(bits)==str:
            masks = {cdsFiltMask[bits]['swnrsuffix'] : cdsFiltMask[bits]['swnrmask']}
        else:
            masks = {}
            for bit in bits:
                if cdsFiltMask[bit]['swnrsuffix'] in masks:
                    masks[cdsFiltMask[bit]['swnrsuffix']] = masks[cdsFiltMask[bit]['swnrsuffix']]|cdsFiltMask[bit]['swnrmask'] # bitwise OR new mask into old
                else:
                    masks[cdsFiltMask[bit]['swnrsuffix']] = cdsFiltMask[bit]['swnrmask'] # create new key
        pvs = pvfn(levels=levels,chans=chans)
        result = []
        for pv in pvs:
            resultbit = 0
            resultsuffix = ''
            for suffix, mask in masks.iteritems():
                resultbit = resultbit|bool(int(self.read(pv+suffix))&mask)
                resultsuffix = resultsuffix+suffix+'.'+str(mask)
            result.append(fmtpair(self.fmtprefix(withprefix)+pv+resultsuffix,bool(resultbit), pair))          
        if matlab: return toMatlab(result)
        else: return result

    # Enable/disable filter module switches (FM1, FM2 etc)
    def genFilterModuleEnableWrite(self, pvfn, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        for filt in filters:
            checkHaveIntVal(filt)
        if enable=='ON' or enable=='OFF':
            pvs = pvfn(levels=levels,chans=chans)
            result = [
                self.switch(pv,'FM'+str(filt),enable, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)
                for filt in filters
                for pv in pvs
            ]
        else:
            pass # NC = no change
        if pair=='none': result = None
        if matlab: return toMatlab(result)
        else: return result

    # -----------------------------------------------------------------------------------------------------------
    # Generic methods for sensor/actuator-specific filter modules (OSEMINF, COILOUTF, OLINF, ESDOUTF, etc)


    # -----------------------------------------------------------------------------------------------------------
    # PV list and default value methods

    # For sensor/actuator-specific matrix blocks

    # Generate PV names for all or selected EUL2OSEM channels
    def e2oPvs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockpvs('osemConfig','eul2', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Generate default values for all or selected EUL2OSEM channels
    def e2oDefs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockdefs('osemConfig','eul2', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Generate PV names for all or selected OL2EUL block channels
    def ol2ePvs(self, levels=[], ichans=[], ochans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockpvs('olConfig','2eul', levels=levels, ichans=ichans, ochans=ochans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Generate PV names for all or selected EUL2ESD block channels
    def e2esdPvs(self, levels=[], ichans=[], ochans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockpvs('esdConfig','eul2', levels=levels, ichans=ichans, ochans=ochans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # For non-sensor/actuator-specific matrix blocks

    # Generate PV names for all or selected CART2EUL channels
    def c2ePvs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelmatrixblockpvs('cart2eul', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Generate default values for all or selected CART2EUL channels
    def c2eDefs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelmatrixblockdefs('cart2eul', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)
 
    # -----------------------------------------------------------------------------------------------------------
    # Methods for OSEM2EUL blocks

    # Generate PV names for all or selected OSEM2EUL channels
    def o2ePvs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockpvs('osemConfig','2eul', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Generate default values for all or selected OSEM2EUL channels
    def o2eDefs(self, levels=[], ichans=[], ochans=[], verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockdefs('osemConfig','2eul', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Read values for all or selected OSEM2EUL channels
    def o2eRead(self, levels=[], ichans=[], ochans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockread('osemConfig','2eul', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # Write default values for all or selected OSEM2EUL channels
    def o2eWriteDefaults(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockwrite('osemConfig','2eul','defaults', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # Write common value for all or selected OSEM2EUL channels
    def o2eWriteValue(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockwrite('osemConfig','2eul','value',value=value, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # Write array values for all or selected OSEM2EUL channels
    def o2eWriteArray(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockwrite('osemConfig','2eul','array', array=array, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # -----------------------------------------------------------------------------------------------------------
    # Methods for EUL2OSEM blocks
    # Read values for all or selected EUL2OSEM channels
    def e2oRead(self, levels=[], ichans=[], ochans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.levelsensactmatrixblockread('osemConfig','eul2', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # Write default values for all or selected EUL2OSEM channels
    def e2oWriteDefaults(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        self.levelsensactmatrixblockwrite('osemConfig','eul2','defaults', levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # Write common value for all or selected EUL2OSEM channels
    def e2oWriteValue(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        self.levelsensactmatrixblockwrite('osemConfig','eul2','value',value=value, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # Write array values for all or selected EUL2OSEM channels
    def e2oWriteArray(self, levels=[], value=0.0, array=[], ichans=[], ochans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        self.levelsensactmatrixblockwrite('osemConfig','eul2','array', array=array, levels=levels, ichans=ichans, ochans=ochans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=False)

    # FIXME: add methods for OL2EUL, EUL2ESD, CART2EUL

    # -------------------------------------------------------------
    # Methods for specific matrices, blocks, switches.
    
    # Methods for top-level items
    # Switch the Master Switch
    def masterSwitchWrite(self, enable, verbose=False):
        pv = self.data['master']
        if enable=='ON':
            if verbose: print pv
            self.write(pv,"ON")
        elif enable=='OFF':
            if verbose: print pv
            self.write(pv,"OFF")
        else:
            pass # NC = no change
        return None # FIXME return something better

    # Read the Master Switch # FIXME add standard options
    def masterSwitchRead(self, verbose=False):
        pv = self.data['master']
        return self.read(pv)==1

    # -------------------------------------------------------------
    # Methods for DAMP blocks

    def dampPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('damp', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def dampOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.dampPvs, 'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.dampPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.dampPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.dampPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.dampPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.dampPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genFilterModuleEnableWrite(self.dampPvs, enable, filters=filters, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.dampPvs, 'OUTPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.dampPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampGainRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.dampPvs, 'GRAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampOffsetRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.dampPvs, 'ORAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.dampPvs, ['GRAMP','ORAMP'], levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def dampGainRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.dampPvs, '_GAIN', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for TEST blocks
    def testPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('test', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def testOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.testPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.testPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.testPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.testPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.testPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.testPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return genFilterModuleEnableWrite(self.testPvs, enable, filters=filters, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.testPvs, 'OUTPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.testPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testGainRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.testPvs, 'GRAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testOffsetRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.testPvs, 'ORAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def testGainRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.testPvs, '_GAIN', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for LOCK blocks

    def lockPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('lock', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def lockOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.lockPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.lockPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.lockPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.lockPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.lockPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.lockPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genFilterModuleEnableWrite(self.lockPvs, filters=filters, enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.lockPvs, enable, 'OUTPUT', chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.lockPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockGainRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.lockPvs, 'GRAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockOffsetRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.lockPvs, 'ORAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def lockGainRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.lockPvs, '_GAIN', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for OPTICALIGN blocks

    def alignPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('align', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def alignOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.alignPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.alignPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.alignPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.alignPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.alignPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.alignPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genFilterModuleEnableWrite(self.alignPvs, enable, filters=filters, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.alignPvs, 'OUTPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOffsetSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.alignPvs, 'OFFSET', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.alignPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignGainRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.alignPvs, 'GRAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOffsetRampingRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.alignPvs, 'ORAMP', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignGainRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.alignPvs, '_GAIN', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def alignOffsetRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.alignPvs, '_OFFSET', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for OSEMINF blocks

    def osemPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('osemConfig','inf', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def osemOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.osemPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.osemPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.osemPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.osemPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.osemPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.osemPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genFilterModuleEnableWrite(self.osemPvs, enable, filters=filters, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.osemPvs, 'OUTPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def osemInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.osemPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for COILOUTF blocks

    def coilPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('osemConfig','outf', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def coilOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.coilPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilInputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.coilPvs, 'INPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilOffsetSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.coilPvs, 'OFFSET', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.coilPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilOffsetWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.coilPvs, '_OFFSET', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.coilPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilFilterModuleEnableWrite(self, enable, filters=[], levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genFilterModuleEnableWrite(self.coilPvs, enable, filters=filters, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def coilOutputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.coilPvs, 'OUTPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlabb)

    def coilInputSwitchRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genSwitchRead(self.coilPvs, 'INPUT', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for ESDOUTF blocks
    def esdPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('esdConfig','outf', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # FIXME: more stuff here
    # -------------------------------------------------------------
    # Methods for ISIINF blocks
    def isiPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('isi', levels=levels,chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # FIXME: more stuff here

    # -------------------------------------------------------------
    # Methods for OFFLOAD blocks
    def offloadPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('offload', levels=levels,chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    # FIXME: more stuff here

    # -------------------------------------------------------------
    # Methods for ISCINF blocks
    def iscPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('isc', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def iscOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.iscPvs,'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def iscRampWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.iscPvs, '_TRAMP', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def iscGainWrite(self, value, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.iscPvs, '_GAIN', value=value, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for OPLEV blocks
    def olPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('olConfig','full', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def olSegPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('olConfig','inf', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def olRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.olPvs, suffix='_OUTMON', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def olSegRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.olSegPvs, suffix='_OUTMON', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # -------------------------------------------------------------
    # Methods for OLDAMP blocks
    def olDampPvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelfilterblockpvs('oldamp', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

    def olDampRead(self, levels=[], chans=[], verbose=False, pair='value', withprefix='bare', matlab=False):
        return self.genNumRead(self.olDampPvs, suffix='_OUTMON', levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def olDampOutputSwitchWrite(self, enable, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genSwitchWrite(self.olDampPvs, 'OUTPUT', enable=enable, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    def olDampResetSwitchWrite(self, levels=[], chans=[], verbose=False, pair='none', withprefix='bare', matlab=False):
        return self.genNumWrite(self.olDampPvs,'_RSET', value=2, levels=levels, chans=chans, verbose=verbose, pair=pair, withprefix=withprefix, matlab=matlab)

    # Methods for NOISEMON
    def noisePvs(self, levels=[], chans=[], suffix='', verbose=False, withprefix='bare', matlab=False):
        return self.levelsensactfilterblockpvs('osemConfig','noise', levels=levels, chans=chans, suffix=suffix, verbose=verbose, withprefix=withprefix, matlab=matlab)

# End of Sus() class definition

# --------------------------------------------------------------------------------------
# Stuff for command line use

# Function to convert a Python result into a Matlab-friendly string. 
# Lists and tuples are converted to cell arrays and booleans are converted to 0 or 1.
def toMatlab(thing, separator=' '):
    if thing==None:
        return 'None'
    if type(thing)==str:
        return repr(thing)
    elif type(thing)==int or type(thing)==float:
        return str(thing)
    elif type(thing)==bool:
        if thing: return '1'
        else: return '0'
    elif type(thing)==list or type(thing)==tuple:
        if len(thing)==0:
            return '{}'
        elif len(thing)==1:
            return '{'+toMatlab(thing[0])+'}'
        else:
            result = '{'
            for item in thing[0:-1]:
                 result += toMatlab(item)+separator
            return result+toMatlab(thing[-1])+'}'
    elif type(thing)==dict:
        return toMatlab(list(thing.items()))
    else:
        raise SusError('Object of unsupported type: '+str(thing))

# Functions to validate data

def checkHaveLongVal(value):
    try: float(value)
    except:
        raise SusError('Non-numeric value: '+value)

def checkHaveIntVal(value):
    try: int(value)
    except:
        raise SusError('Non-integer value: '+value)

def fmtpair(pv,val, pair='value'):
    "Return requested combination of PV, value or both as tuple."
    if pair=='pv':
        return pv 
    elif pair=='value':
        return val
    elif pair=='both':
        return (pv,val)
    elif pair=='none':
        return None
    else:
        return pair

def fmtwd(pv,wd, pair='value'):
    "Return requested combination of PV, watchdog label (e.g., 'IOP'/'USER'/'M0') or both as tuple."
    if pair=='pv':
        return pv 
    elif pair=='value':
        return wd
    elif pair=='both':
        return (wd,pv)
    elif pair=='none':
        return None
    else:
        return pair

def printifnotnone(v):
    if v!=None:
        print v

# Things that are allowed to be called from the command line
callableGlobals = ['susTypes','susData']
callableSusFunctions = ['levels','suspensionType']
callableLevelNameFunctions = [
    'testPvs', 'dampPvs','witPvs','lockPvs','alignPvs','coilPvs','osemPvs','olSegPvs','olPvs','esdPvs',
    'osemNames','osemDofs','olNames','olDofs','esdNames','esdDofs','iscPvs','olDampPvs','noisePvs',
]
callableLevelDataFunctions = ['coilDriverData','magnetData','osemData']
callableLevelMatrixFunctions = ['o2ePvs','o2eDefs','e2oPvs','e2oVals','ol2ePvs','e2esdPvs','c2ePvs','c2eDefs']
callableLevelMatrixReadCommands = ['o2eRead','e2oRead']
callableLevelMatrixWriteCommands = ['o2eWriteDefaults','o2eWriteValue','o2eWriteArray','e2oWriteDefaults','e2oWriteValue','e2oWriteArray']
callableOpticSwitchWriteCommands = [
    'masterSwitchWrite'
]
callableLevelFilterModuleEnableWriteCommands = [
    'dampOutputSwitchWrite','dampInputSwitchWrite','dampOffsetSwitchWrite',
    'testOutputSwitchWrite','testInputSwitchWrite','testOffsetSwitchWrite',
    'lockOutputSwitchWrite','lockInputSwitchWrite','lockOffsetSwitchWrite',
    'alignOutputSwitchWrite','alignInputSwitchWrite','alignOffsetSwitchWrite',
    'osemOutputSwitchWrite','osemInputSwitchWrite','osemOffsetSwitchWrite',
    'coilOutputSwitchWrite','coilInputSwitchWrite','coilOffsetSwitchWrite',
    'olDampOutputSwitchWrite'
]

callableLevelFilterSwitchReadCommands = [
    'dampOutputSwitchRead','dampOffsetRampingRead',
    'testOutputSwitchRead','testOffsetRampingRead',
    'lockOutputSwitchRead','lockOffsetRampingRead',
    'alignOutputSwitchRead','alignOffsetRampingRead',
    'osemOutputSwitchRead','coilOutputSwitchRead',
    'dampInputSwitchRead','testInputSwitchRead','lockInputSwitchRead','alignInputSwitchRead',
    'osemInputSwitchRead','coilInputSwitchRead',
    'dampGainRead','dampGainRampingRead','dampRampingRead',
    'testGainRead','testGainRampingRead',
    'lockGainRead','lockGainRampingRead',
    'alignGainRead','alignGainRampingRead',
    'osemGainRead',
    'coilGainRead'
]
callableLevelFilterEnableCommands = [
    'dampFilterModuleEnableWrite','testFilterModuleEnableWrite','lockFilterModuleEnableWrite','alignFilterModuleEnableWrite',
    'coilFilterModuleEnableWrite','osemFilterModuleEnableWrite'
]
callableLevelFilterWriteCommands = [
    'dampRampWrite','dampOffsetWrite','dampGainWrite',
    'testRampWrite','testOffsetWrite','testGainWrite',
    'lockRampWrite','lockOffsetWrite','lockGainWrite',
    'alignRampWrite','alignOffsetWrite','alignGainWrite',
    'osemRampWrite','osemOffsetWrite','osemGainWrite',
    'coilRampWrite','coilOffsetWrite','coilGainWrite'
]

callableLevelFilterOutputReadCommands = ['olRead','olSegRead']

allCallables = (
    callableGlobals+callableSusFunctions+callableLevelNameFunctions+callableLevelDataFunctions+callableOpticSwitchWriteCommands
    +callableLevelMatrixFunctions+callableLevelMatrixWriteCommands
    +callableLevelNameFunctions+callableLevelFilterModuleEnableWriteCommands+callableLevelFilterSwitchReadCommands
    +callableLevelFilterEnableCommands+callableLevelFilterWriteCommands+callableLevelFilterOutputReadCommands
)

usage = '''%(prog)s [command] [options]
The -x and -X switches allow arbitrary Python code to be executed before or after the main command.
The -o switch is required for all optic-specific commands.
The -l, -c, -f and -a switches accept multiple arguments, e.g., -l M0 R0.
Commands: '''+str(allCallables)

# A main() function which will parse the command line arguments 
def main():
    import argparse
    prog = os.path.basename(sys.argv[0])
    
    parser = argparse.ArgumentParser(prog=prog,usage=usage)
    parser.add_argument('command', action='store', default='', type=str, nargs= '?', help='Command')
    parser.add_argument('-o', '--optic', dest='optic', action='store', default='', type=str, help='Optic')
    parser.add_argument('-i', '--ifo', dest='ifo', action='store', default=os.environ['IFO'], type=str, help='IFO (default local)')
    parser.add_argument('-l', '--level', dest='levels', metavar='LEVEL', action='store', default=[], type=str, nargs='*', help='SAG level (M0/R0/etc; default all)')
    parser.add_argument('-c', '--chan', '--inchans', dest='chans', metavar="CHAN",action='store', default=[], type=str, nargs='*', help='Channels/DOFs (F1/F2/F3/etc, L/T/V/etc; default all)')
    parser.add_argument('-C', '--outchans', dest='ochans', metavar="CHAN",action='store', default=[], type=str, nargs='*', help='Output channels/DOFs (F1/F2/F3/etc, L/T/V/etc; default all) for commands that work with arrays')
    parser.add_argument('-f', '--filter', dest='filters', metavar='FM#', action='store', default=[], type=str, nargs='*', help='Filters (1/2/.../10; default none)')
    parser.add_argument('-k', '--key', dest='key', metavar='KEYLIST', action='store', default=[], type=str, nargs='*', help='List of dictionary keys (for data lookup)')
    parser.set_defaults(enable='NC')
    parser.add_argument('-e', '--true', '--enable', '--on', dest='enable', action='store_const', const = 'ON',  help='On (for switch commands)')
    parser.add_argument('-d', '--false', '--disable', '--off', dest='enable', action='store_const', const = 'OFF', help='Off (for switch commands)')
    parser.add_argument('-n', '--nochange', dest='enable', action='store_const', const = 'NC', help='No change (for switch commands)')
    parser.add_argument('-v', '--value', dest='value', metavar='VAL', action='store', default=0, type=float, help='Numeric value (for setting commands)')
    parser.add_argument('-a', '--array', dest='array', metavar='VAL', action='store', default=[], type=float, nargs='*',help='Numeric array (for setting commands)')
    parser.add_argument('--verbose', dest='verbose', action='store_const', const = True, default=False, help='Turns on -t and additional debugging output')
    parser.set_defaults(pair='value')
    parser.add_argument('-p', '--pair', dest='pair', metavar='pv/value/tuple', action='store', default='', type=str,  help='Whether read/write commands return PV, value (default), or (PV,value) tuple')
    parser.set_defaults(withprefix='full')
    parser.add_argument('-b','--bare', dest='withprefix', action='store_const', const = 'bare', help="With commands that return PV lists, omit the 'H1:SUS-ITMX_' or similar prefix")
    parser.add_argument('-B','--halfbare', dest='withprefix', action='store_const', const = 'halfbare', help="With commands that return PV lists, omit the 'H1:SUS-' or similar prefix")
    parser.add_argument('-m','--matlab', dest='matlab', action='store_const', const = True, default=False, help="With commands that return lists, format as a Matlab cell array of strings")
    parser.add_argument('-s','--suffix', dest='suffix', action='store', default='', type=str, help="With commands that return PV lists, add a suffix. e.g., _EXC, to all PVs")
    parser.add_argument('-x','--executebefore', dest='bcode', metavar='PYTHONCODE', action='store', default=[], type=str, nargs='*', help='Execute the code before the main command')
    parser.add_argument('-X','--executeafter', dest='acode', metavar='PYTHONCODE', action='store', default=[], type=str, nargs='*', help='Execute the code after the main command')
    options = parser.parse_args()
#    print options
#    print '----'

    if options.bcode=='' and options.command=='' and options.acode=='':
        raise SusError('Nothing to execute: no command and no -x or -X - see -h for help')

    optic=None
    opticname=options.optic.upper()
    ifoname=options.ifo.upper()
    fullname = ifoname+':'+opticname
    if opticname!='':
        if (ifoname,opticname) not in susTypes:
            raise SusError('Unrecognized optic: '+fullname)
        optic = Sus(opticname)
        if options.verbose: print 'Optic: '+optic.name

    if options.bcode!='':
        if options.bcode:
            bcode = ''
            for word in options.bcode:
                bcode += word+' '
            print 'Before code: '+bcode
            exec bcode

    if options.command=='':
        pass

    elif options.command in callableGlobals:
        keywords = ''
        for keyword in options.key:
            keywords += '['+repr(eval(keyword))+']'
        if options.matlab:
            cmd = 'result = toMatlab('+options.command+')'+keywords+'; print result'
        else:
            cmd = 'result = '+options.command+keywords+'; print result'
        if options.verbose: print cmd
        exec cmd

    else: # all remaining command types require an optic
        if optic==None:
            raise SusError('Optic not specified')

        if options.command in callableSusFunctions:
            cmd = 'result = optic.'+options.command+'('\
            +'verbose='+str(options.verbose)\
            +', matlab='+str(options.matlab)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableLevelNameFunctions:
            cmd = 'result = optic.'+options.command+'('\
            +'levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +', suffix="'+str(options.suffix)+'"'\
            +', matlab='+str(options.matlab)\
            +', withprefix='+repr(options.withprefix)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableLevelDataFunctions:
            cmd = 'result = optic.'+options.command+'('\
            +str(options.key)\
            +', levels='+str(options.levels)\
            +', verbose='+str(options.verbose)\
            +', matlab='+str(options.matlab)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableLevelMatrixFunctions:
            cmd = 'result = optic.'+options.command+'('\
            +'levels='+str(options.levels)\
            +', ichans='+str(options.chans)\
            +', ochans='+str(options.ochans)\
            +', verbose='+str(options.verbose)\
            +', matlab='+str(options.matlab)\
            +', withprefix='+repr(options.withprefix)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableLevelMatrixReadCommands:
            if options.pair=='': options.pair='value'
            cmd = 'result = optic.'+options.command+'('\
            +'levels='+str(options.levels)\
            +', ichans='+str(options.chans)+', ochans='+str(options.ochans)\
            +', verbose='+str(options.verbose)+', matlab='+str(options.matlab)\
            +', pair='+repr(options.pair)+', withprefix='+repr(options.withprefix)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableLevelMatrixWriteCommands:
            if options.pair=='': options.pair='none'
            cmd = 'result = optic.'+options.command+'('\
            +'value='+str(options.value)\
            +', array='+str(options.array)\
            +', levels='+str(options.levels)\
            +', ichans='+str(options.chans)\
            +', ochans='+str(options.ochans)\
            +', verbose='+str(options.verbose)\
            +', matlab='+str(options.matlab)\
            +', pair='+repr(options.pair)\
            +', withprefix='+repr(options.withprefix)\
            +'); print result'
            if options.verbose: print cmd
            exec cmd

        elif options.command in callableOpticSwitchWriteCommands:
            if options.pair=='': options.pair='none'
            cmd = 'result = optic.'+options.command\
            +'(enable="'+options.enable+'"'\
            +', verbose='+str(options.verbose)\
            +', pair='+repr(options.pair)\
            +', withprefix='+repr(options.withprefix)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
 
        elif options.command in callableLevelFilterModuleEnableWriteCommands:
            if options.pair=='': options.pair='none'
            cmd = 'result = optic.'+options.command+'(enable="'+options.enable+'"'\
            +', levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
 
        elif options.command in callableLevelFilterSwitchReadCommands:
            if options.pair=='': options.pair='value'
            cmd = 'result = optic.'+options.command+'('\
            +'levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +', pair="'+str(options.pair)+'"'\
            +', matlab='+str(options.matlab)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
 
        elif options.command in callableLevelFilterEnableCommands:
            if options.pair=='': options.pair='none'
            cmd = 'result = optic.'+options.command+'('\
            +"'"+str(options.enable)+"'"\
            +', filters='+repr(options.filters)\
            +', levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +', pair='+repr(options.pair)\
            +', withprefix='+repr(options.withprefix)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
 
        elif options.command in callableLevelFilterWriteCommands:
            if options.pair=='': options.pair='none'
            cmd = 'result = optic.'+options.command+'('\
            +'value="'+str(options.value)+'"'\
            +', levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +', pair='+repr(options.pair)\
            +', withprefix='+repr(options.withprefix)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
  
        elif options.command in callableLevelFilterOutputReadCommands:
            if options.pair=='': options.pair='value'
            cmd = 'result = optic.'+options.command+'('\
            +'levels='+str(options.levels)\
            +', chans='+str(options.chans)\
            +', verbose='+str(options.verbose)\
            +', pair="'+str(options.pair)+'"'\
            +', matlab='+str(options.matlab)\
            +'); printifnotnone(result)'
            if options.verbose: print cmd
            exec cmd
 
        else:
            raise SusError('Unrecognized variable/function/command: '+options.command)

    if options.acode!='':
        if options.acode:
            acode = ''
            for word in options.acode:
                acode += word+' '
            print 'After code: '+acode
            exec acode

# --------------------------------------------------------------------------------------
# Data section

# Random EPICS stuff
# Bit mask combos for reading back cdsFilt block settings via _SW1R and _SW2R, or _SWSTAT from T080135 (& T1300494)
cdsFiltMask = {
    'INPUT' : {'swnrsuffix':'_SW1R','swnrmask':4,'swstatmask':1024},
    'OFFSET' : {'swnrsuffix':'_SW1R','swnrmask':8,'swstatmask':2048},
    'FM1' : {'swnrsuffix':'_SW1R','swnrmask':16,'swstatmask':1},     'FM1S' : {'swnrsuffix':'_SW1R','swnrmask':32}, # R=request; S=actual state
    'FM2' : {'swnrsuffix':'_SW1R','swnrmask':64,'swstatmask':2},     'FM2S' : {'swnrsuffix':'_SW1R','swnrmask':128},
    'FM3' : {'swnrsuffix':'_SW1R','swnrmask':256,'swstatmask':4},    'FM3S' : {'swnrsuffix':'_SW1R','swnrmask':512},
    'FM4' : {'swnrsuffix':'_SW1R','swnrmask':1024,'swstatmask':8},   'FM4S' : {'swnrsuffix':'_SW1R','swnrmask':2048},
    'FM5' : {'swnrsuffix':'_SW1R','swnrmask':4096,'swstatmask':16},  'FM5S' : {'swnrsuffix':'_SW1R','swnrmask':8192},
    'FM6' : {'swnrsuffix':'_SW1R','swnrmask':16384,'swstatmask':32}, 'FM6S' : {'swnrsuffix':'_SW1R','swnrmask':32768},
    'FM7' : {'swnrsuffix':'_SW2R','swnrmask':1,'swstatmask':64},     'FM7S' : {'swnrsuffix':'_SW2R','swnrmask':2},
    'FM8' : {'swnrsuffix':'_SW2R','swnrmask':4,'swstatmask':128},    'FM8S' : {'swnrsuffix':'_SW2R','swnrmask':8},
    'FM9' : {'swnrsuffix':'_SW2R','swnrmask':16,'swstatmask':256},   'FM9S' : {'swnrsuffix':'_SW2R','swnrmask':32},
    'FM10' : {'swnrsuffix':'_SW2R','swnrmask':64,'swstatmask':512},  'FM10S' : {'swnrsuffix':'_SW2R','swnrmask':128},
    'LIMIT' : {'swnrsuffix':'_SW2R','swnrmask':256,'swstatmask':8192},
    'DECIMATION' : {'swnrsuffix':'_SW2R','swnrmask':512},
    'OUTPUT' : {'swnrsuffix':'_SW2R','swnrmask':1024,'swstatmask':4096},
    'HOLD' : {'swnrsuffix':'_SW2R','swnrmask':2048},
    'GRAMP' : {'swnrsuffix':'_SW2R','swnrmask':4096},
    'ORAMP' : {'swnrsuffix':'_SW2R','swnrmask':8192} # GRAMP or ORAMP
}


# -------------------------------------------------------------------------------------------------
# Watchdog definitions for use in susTypes below
#b123wd = {'IOP':':IOP-SUS_B123_DACKILL'}
#h2awd = {'IOP':':IOP-SUS_H2A_DACKILL'}
#h2bwd = {} # not 'IOP':':IOP-SUS_H2B_DACKILL'
#h34wd = {'IOP':':IOP-SUS_H34_DACKILL'}
#h56wd = {'IOP':':IOP-SUS_H56_DACKILL'}
#exwd = {'IOP':':IOP-SUS_EX_DACKILL'}
#eywd = {'IOP':':IOP-SUS_EY_DACKILL'}
#ascwd = {}
#ascwdllo = {} # FIXME - need to check immediately, update when appropriate
# -----  no this function in KAGRA

# Lists of WD type

typecwd = {'USER':'DACKILL','IM':'IM_WDMON','TM':'TM_WDMON'}

mcewd = dict(typecwd)

# -------------------------------------------------------------------------------------------------
# Lists of specific suspensions by type
susTypes = {
    ('K1','MCE ') : {'type': 'TYPEC','watchdogs': typecwd}
    }

typec =  [sus for (sus,data) in susTypes.items() if data['type']=='TYPEC']

# -----------------------------------------------------------------------------------------
# Standard info
# Lists of input and/or output names
bscToplevelOsemNames = ['H1','H2','H3','V1','V2','V3']
hamToplevelOsemNames = ['H1','H2','H3','V1','V2','V3']
genericlevelOsemNames = ['H1','H2','H3','H4']
olSegNames = ['SEG1','SEG2','SEG3','SEG4']
esdSegNames = ['H1','H2','H3','H4','DC']
isiNames = ['X','Y','RZ','Z','RX','RY']

# Lists of DOF names used in filter banks
sixDofNames = ['L','T','V','R','P','Y']
threeDofNames = ['L','P','Y']
threeDofMonNames = ['LMON','PMON','YMON']
olDofNames = ['P','Y','SUM']
olFullDofNames = ['PIT','YAW','SUM']
olDampDofNames = ['P','Y']
esdDofNames = ['L','P','Y','BIAS']
alignDofNames = ['P','Y']

# Shadow sensor stuff
aosem = {'type':'AOSEM','imax':95.0, 'sensitivity': 1/0.7, 'coilturns' : 400, 'coillen' : 0.16*25.4, 'coilrad1' : 0.304*25.4, 'coilrad2' : 0.498*25.4} # T1000164-v3

# OSEM readback # FIXME finish this section
stdosemrdbck = { 
    'osem':76.29/0.7, # uA/mm
    'white':[('zpk',[0.4],[10,1000],'1','n')],
    'aa':[('zpk',[],[],1,'n')], # FIXME fill in exact hardware AA filter
    'iop':[('zpk',[],[],1,'n')], # FIXME fill in exact software IOP downsampling filter
    'adc':2**16/40
}

# Identity matrices
i6 = [[1.,0.,0.,0.,0.,0.],[0.,1.,0.,0.,0.,0.],[0.,0.,1.,0.,0.,0.],[0.,0.,0.,1.,0.,0.],[0.,0.,0.,0.,1.,0.],[0.,0.,0.,0.,0.,1.]]
i3 = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]

# Magnet signs
signsM0 = [1,-1,1,-1,1,-1] # E1000617-v5
signsR0 = [1,1,-1,1,-1,-1] # E1000617-v5
signsM1HAM = [-1,-1,1,1,-1,-1] # E1100109-v2
signsM1HAM2 = [-1,-1,1,1,-1,1] # E1100109-v2, but with SD OSEM on opposite end as for HLTS (PR3 and SR3), SRM and PRM
signs4B = [-1,1,1,-1] # standard UL/LL/UR/LR array for BOSEMs # E1000617-v5 (QUAD), E1100108-v3 (BSFM),
signs4A = [1,-1,-1,1] # standard UL/LL/UR/LR array for AOSEMs

# Standard filter bank definitions
test6 = {'blockname':'TEST', 'names':'dofs','default':{'gains':[1.,1.,1.,1.,1.,1.]}}
test3 = {'blockname':'TEST', 'names':'dofs','default':{'gains':[1.,1.,1.]}}
testEsd = {'blockname':'TEST', 'names':'esddofs','default':{'gains':[1.,1.,1.,1.]}}
isc3 = {'blockname':'ISCINF', 'names':'iscdofs'}
damp6 = {'blockname':'DAMP', 'names':'dofs','default':{'gains':[-1.,-1.,-1.,-1.,-1.,-1.]}}
damp3 = {'blockname':'DAMP', 'names':'dofs','default':{'gains':[-1.,-1.,-1.,-1.,-1.,-1.]}}
wit3 = {'blockname':'WIT', 'names':'dofs'}
lock3top = {'blockname':'LOCK', 'names':'lockdofs'}
lock3 = {'blockname':'LOCK', 'names':'dofs'}
lockEsd = {'blockname':'LOCK', 'names':'esddofs'}
isi6 =  {'blockname':'ISIINF', 'names':'isidofs'}
offload = {'blockname':'OFFLOAD', 'names':'isidofs'}

# Standard matrix block definitions
sa6 = {'blockname':'SENSALIGN', 'inames':'dofs',  'onames':'dofs',  'default':i6}
sa3 = {'blockname':'SENSALIGN', 'inames':'dofs',  'onames':'dofs',  'default':i3}
c2e = {'blockname':'CART2EUL', 'inames':'isichans', 'onames':'dofs'}

# Driver types - Jeff K's names, plus strengths in mA/V
qtop = {'name':'QTOP', 'strength':9.9}
uim = {'name':'UIM', 'strength':0.15}
pum = {'name':'PUM', 'strength':0.26}
tacq = {'name':'TACQ', 'strength':0.33}
tacq2 = {'name':'TACQ*', 'strength':2.8}
otop = {'name':'OTOP', 'strength':0.2}
ttop = {'name':'TTOP', 'strength':11.9}
mtop = {'name':'MTOP', 'strength':11.9}
hama = {'name':'HAMA', 'strength':9.6}

# -----------------------------------------------------------------------------------------
# Lever arm info

haux_m1_PitchArm  = 0.05818; # [m]
haux_m1_YawArm   = 0.05818; # [m]

#    UL    LL    UR    LR
haux_o2e_m1 = [
    [0.25, 0.25, 0.25, 0.25],                # L
    [x/haux_m1_PitchArm for x in [0.50, -0.50, 0.50, -0.50]],    # P
    [x/haux_m1_YawArm for x in [-0.50, -0.50, 0.50, 0.50]]        # Y            
]

# HTTS
htts_m1_PitchArm = 0.048225; # [m]
htts_m1_YawArm   = 0.048225; # [m]

#    UL    LL    UR    LR
htts_o2e_m1 = [
    [0.25, 0.25, 0.25, 0.25],              # L
    [x/htts_m1_PitchArm for x in [0.50, -0.50, 0.50, -0.50]],  # P
    [x/htts_m1_YawArm for x in [-0.50, -0.50, 0.50, 0.50]]      # Y            
]

# -----------------------------------------------------------------------------------------
# Master dictionary of data for all suspension types
# G1100968-v2 (Controls overview)
# T1000618-v3 (Magnets)
# E1000617-v5 (QUAD)
# E1100109-v2 (HxTS, OMCS)
# E1200045-v2 (TMTS)
susData = {
    'HAUX' : {
	'reallyis' : 'HAUX',
        'levelorder' : ['M1'],
        'master' : 'MASTERSWITCH',
        'levels' : {
            'M1' : {
                'dofs' : threeDofNames,
                'osemConfig' : {
                    'chans' : genericlevelOsemNames,
                    'dofs' : threeDofNames,
                    'osem' : aosem,
                    'magnet' : {'diameter':1.9,'length':3.2,'material':'SmCo??','force':0.0158},
                    'driver' : hama,
                    'sensalign' : sa3,
                    'inf' : {'blockname':'OSEMINF', 'names':'chans'},
                    'noise' : {'blockname':'VOLTMON', 'names':'chans'},
                    '2eul' : {'blockname':'OSEM2EUL','inames':'chans', 'onames':'dofs', 'default':haux_o2e_m1},
                    'eul2' : {'blockname':'EUL2OSEM','inames':'dofs', 'onames':'chans', 'default':map(list,zip(*haux_o2e_m1))},
                    'outf' : {'blockname':'COILOUTF', 'names':'chans', 'default':{'gains':signs4A}}
                },
                'oldamp' : None,
                'olConfig' : None,
                'esdConfig' : None,
                'isi' : None,
		'isc' : None,
                'cart2eul' : None,
                'eul2cart' : None,
                'offload' : None,
                'damp' : damp6,
                'wit' : None,
                'lock' : lock3,
                'test' : test3,
                'aligndofs' : alignDofNames,
                'align' : {'blockname':'OPTICALIGN', 'names':'aligndofs'},
                'watchdog' : 'watchdogs'
            }
        }
    }
}

# --------------------------------------------------------------------------------------
# This needs to be last.
# Run the main() function if the file is run as a script from the command line.
if __name__ == "__main__":
    main()
