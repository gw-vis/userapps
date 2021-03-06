# This file was created by Terrence in order to test new Guardian states without having to use the suspensions.
# It uses a fake ezca package in order to simulate ezca channels, so we can develop Guardian code without having
# to use the suspensions.
# The fake ezca is not imported in this file but in a fake vistools.
# Fake ezca is not expected to modify the real suspension Guardian but be careful, please.
# Date: 2019-11-15
# 2020-01-23: Stopped by YamaT

from guardian import GuardState
from guardian import GuardStateDecorator
from guardian import NodeManager
from vistools_fake import *
visObj=None
# initial REQUEST state
request = 'INIT'

# NOMINAL state, which determines when node is OK
nominal = 'ALIGNED'

def checkvis():
    global visObj
    if visObj == None:
        #import fakeezca as ezca
        #notify('It didnt create visObj')
        visObj=Vis('VIS_SR2')

# This is the function which engages the OBSERVATION state




class INIT(GuardState):
    index=0
    def main(self):
        global visObj
        checkvis()
        notify('Fabian was here')
        return(True)


class PRE_ALIGNED(GuardState): # This state provides some information about the state of the system
    index=10
    def main(self):
        global visObj
        checkvis()
        notify('It doesnt go through')
        levels=visObj.levels()
        notify(levels)
        val=visObj.dampOffsetRead()        
        notify('Val:%f'%val[0])
        #notify('It went through')
        return(True)

class ALIGNED(GuardState):
    index=20
    def main(self):
        global visObj
        checkvis()
        notify('This is the fake ALIGNED state')
        return(True)

class CALM_DOWN(GuardState):
    index = 30
    def main(self):
        global visObj
        checkvis()
        notify('This is the fake CALM_DOWN state')
        return(True)

class ENGAGING_CALM_DOWN(GuardState):
    index=40
    request = False
    def main(self):
        global visObj
        checkvis()
        notify('Transitioning to CALM-DOWN state')
        return(True)

class DISENGAGING_CALM_DOWN(GuardState):
    index=50
    request = False
    def main(self):
        global visObj
        checkvis()
        notify('Transitioning to CALM-DOWN state')
        return(True)

class ENGAGING_OBSERVATION(GuardState):
    """
    In the real Guardian the configuration of the OBSERVATION state must be loaded from a snapshot.
    This typically happens in a nested call of functions:
    beginControlSequence(stateObj,level) -->
    rampSetpoint(level) -->
    val=valFromSnap(level,'SET',DOF,setSnapDict[level],'OFFSET')
    """
    index=60
    request = False
    def main(self):
        global visObj
        checkvis()
        notify('Transitioning to OBSERVATION state')
        # return beginControlSequence(self, level=['TM','IM','GAS'])
        return(True)

class DISENGAGING_OBSERVATION(GuardState):
    index=70
    request = False
    def main(self):
        global visObj
        checkvis()
        notify('Transitioning to OBSERVATION state')
        return(True)

class OBSERVATION(GuardState):
    index=80
    def main(self):
        global visObj
        checkvis()
        notify('We are in OBSERVATION state, let us detect gravitational waves!')
        return(True)

edges=[
('INIT','PRE_ALIGNED'),
('PRE_ALIGNED','ALIGNED'),('ALIGNED','PRE_ALIGNED'),
('ALIGNED','ENGAGING_CALM_DOWN'),('ENGAGING_CALM_DOWN','CALM_DOWN'),('CALM_DOWN','DISENGAGING_CALM_DOWN'),('DISENGAGING_CALM_DOWN','ALIGNED'),
('ALIGNED','ENGAGING_OBSERVATION'),('ENGAGING_OBSERVATION','OBSERVATION'),('OBSERVATION','DISENGAGING_OBSERVATION'),('DISENGAGING_OBSERVATION','ALIGNED')
]

# ('ENGAGING_CALM_DOWN','ALIGNED')



