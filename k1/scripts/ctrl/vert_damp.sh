#!/bin/sh

#Damping
tdswrite K1:VIS-PROTO_GAS_SERVOF_F0_RSET 2
tdswrite K1:VIS-PROTO_GAS_SERVOF_F0_TRAMP 5.0
tdswrite K1:VIS-PROTO_IM_SERVOF_V_TRAMP 5.0

#GAIN ON
tdswrite K1:VIS-PROTO_GAS_SERVOF_F0_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_V_GAIN -1.0

sleep 20

tdswrite K1:VIS-PROTO_GAS_SERVOF_F0_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_V_GAIN 0.0







