#!/bin/sh

#Damping


#GAIN ON
tdswrite K1:VIS-PROTO_TM_SERVOF_L_GAIN -1.0
tdswrite K1:VIS-PROTO_TM_SERVOF_P_GAIN -1.0
tdswrite K1:VIS-PROTO_TM_SERVOF_Y_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_L_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_T_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_V_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_R_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_P_GAIN -1.0
tdswrite K1:VIS-PROTO_IM_SERVOF_Y_GAIN -1.0

sleep 20

tdswrite K1:VIS-PROTO_TM_SERVOF_L_GAIN 0.0
tdswrite K1:VIS-PROTO_TM_SERVOF_P_GAIN 0.0
tdswrite K1:VIS-PROTO_TM_SERVOF_Y_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_L_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_T_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_V_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_R_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_P_GAIN 0.0
tdswrite K1:VIS-PROTO_IM_SERVOF_Y_GAIN 0.0













