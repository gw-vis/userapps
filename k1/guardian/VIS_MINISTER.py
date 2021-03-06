from guardian import GuardState,GuardStateDecorator, NodeManager
import kagralib
import iscparams

# Parameters
TMOLRMSThreshold = {
    'ITMX':{'P': 1000, 'Y': 1000},
    'ITMY':{'P': 1000, 'Y': 1000},
    'ETMX':{'P': 1000, 'Y': 1000},
    'ETMY':{'P': 1000, 'Y': 1000}
    }

MNOLRMSThreshold = {
    'ITMX':{'P': 1000, 'Y': 1000},
    'ITMY':{'P': 1000, 'Y': 1000},
    'ETMX':{'P': 1000, 'Y': 1000},
    'ETMY':{'P': 1000, 'Y': 1000}
    }


# Helper functions
def is_TM_OpLev_insane(optic):
  #Function to check TM OpLevRMS
  status = False
  for dof in ['P', 'Y']:
    status |= ezca['VIS-' + optic + '_TM_OPLEV_TILT_BLRMS_' + dof + '_300M_1'] > TMOLRMSThreshold[optic][dof]
  return status

def is_MN_OpLev_insane(optic):
  #Function to check MN OpLevRMS
  status = False
  for dof in ['P', 'Y']:
    status |= ezca['VIS-' + optic + '_MM_OPLEV_TILT_BLRMS_' + dof + '_300M_1'] > MNOLRMSThreshold[optic][dof]
  return status


# Decorators

# Class definitions
class INIT(GuardState):
  index = 0
  def main(self):
    return True

class SAFE(GuardState):
# request SAFE state for all suspentions
  index = 1

class NUTRAL(GuardState):
  index = 2

#setting up suspensions for various congifurations
SET_SUS_FOR_FPMI = kagralib.gen_SET_SUS_CONFIG('FPMI')
SET_SUS_FOR_FPMI.index = 3
SET_SUS_FOR_PRFPMI = kagralib.gen_SET_SUS_CONFIG('PRFPMI')
SET_SUS_FOR_PRFPMI.index = 4


class OLDAMPED(GuardState):
# request OLDAMPED state if the TM oplev signal becomes over ?

class MN_MNDAMP(GuardState):
# request MN_MNDAMP state if the TM oplev signal out of range

class PAY_LOCALDAMPED(GuardState):
# request PAY_LOCALDAMPED state if the MN oplev signal out of range

# Diagram
edges = [
  ('INIT', 'SAFE'),
  ('SAFE', 'NUTRAL'),
  ('NUTRAL', 'SET_SUS_FOR_PRFPMI'),
  ('NUTRAL', 'SET_SUS_FOR_FPMI'),
  ]
