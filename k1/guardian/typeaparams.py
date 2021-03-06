# IP gain setting
IPgains = { 'L':1.0,
            'T':1.0,
            'Y':1.0}


GASgains = {
	'ITMY':{'F0':0.0,
                'F1':1.0,
                'F2':1.0,
                'F3':1.0,
                'BF':0.0
		},
	'ETMY':{'F0':1.0,
                'F1':0.0,
                'F2':0.0,
                'F3':0.0,
                'BF':1.0
		},
	'ETMX':{'F0':1.0,
                'F1':1.0,
                'F2':0.0,
                'F3':1.0,
                'BF':1.0
		},
	'ITMX':{'F0':0.0,
                'F1':1.0,
                'F2':1.0,
                'F3':1.0,
                'BF':0.0
		}
	}
## When ITMY is fixed...
#GASgains = { 'F0':0.0, # For ITMX
#             'F1':1.0,
#             'F2':1.0,
#             'F3':1.0,
#             'BF':1.0}


# BF gain setting
BFgains = {
    'ITMY':{ 'L':1.0,
             'T':1.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':1.0},
    'ETMY':{ 'L':1.0,
             'T':1.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':1.0},
    'ITMX':{ 'L':1.0,
             'T':1.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':1.0},
    'ETMX':{ 'L':1.0,
             'T':1.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':1.0}
    }
    
# MN gain setting
MNgains = { 'ITMY':
            {'L':1.0,
             'T':0.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':0.0},
            'ETMY':
            {'L':1.0,
             'T':0.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':0.0},
            'ITMX':
            {'L':0.0,
             'T':0.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':0.0},
            'ETMX':
            {'L':0.0,
             'T':0.0,
             'V':0.0,
             'R':0.0,
             'P':0.0,
             'Y':0.0}
            }
            


# IM gain setting
IMgains = { 'L':0.0,
            'T':0.0,
            'V':0.0,
            'R':0.0,
            'P':0.0,
            'Y':0.0}
# MN gain setting for MN oplev loop 
MNoplev_gains = { 'ITMY':
                    {'P':0.0,
                     'Y':1.0},
                    'ETMY':
                    {'P':0.0,
                     'Y':1.0},
                    'ITMX':
                    {'P':0.0,
                     'Y':1.0},
                    'ETMX':
                    {'P':1.0,
                     'Y':1.0}
                    }

# IM gain setting for oplev loop 
IMoplev_gains = { 'ITMY':
                    {'P':1.0,
                     'Y':0.0},
                    'ETMY':
                    {'P':1.0,
                     'Y':0},
                    'ITMX':
                    {'P':1.0,
                     'Y':1.0},
                    'ETMX':
                    {'P':1.0,
                     'Y':0.0}
                    }

# BF gain setting for TM oplev loop 
TMoplev_BF_gains = { 'P':0.0,
                     'Y':0.0,
                     'L':0.0}


# MN gain setting for TM oplev loop 
TMoplev_MN_gains = { 'P':0.0,
                     'Y':0.0,
                     'L':0.0}

# added by YF on 2019 Sep. 4th from #
#TMoplev_MN_gains = { 
#             'ITMY':{'P':0.0,
#                     'Y':0.0,
#                     'L':0.0},
#             'ETMY':{'P':0.0,
#                     'Y':0.0,
#                     'L':0.0},
#             'ITMX':{'P':0.0,
#                     'Y':0.0,
#                     'L':0.0},
#             'ETMX':{'P':1.0,
#                     'Y':0.0,
#                     'L':0.0}
#              }
# added by YF on 2019 Sep. 4th until #

# IM gain setting for TM oplev loop 
TMoplev_IM_gains = { 'P':1.0,
                     'Y':1.0,
                     'L':0.0}

# TM oplev gain setting
TMoplev_gains = { 'P':0.0,
                  'Y':0.0,
                  'L':0.0}

# CALM DOWN gain
CALM_DOWN_gains = { 'ITMY':
                    {'P':0.0,
                     'Y':0.0},
                    'ETMY':
                    {'P':0.0,
                     'Y':1.0},
                    'ITMX':
                    {'P':0.0,
                     'Y':0.0},
                    'ETMX':
                    {'P':1.0,
                     'Y':1.0}
                    }

                    

BIO_TWR = ['BFH','BFV','GAS','PI']
BIO_PAY = ['TM','IMB','IMH','MNIMV','MNH']

misalign_ramp = 20
misalign_amount = 100
