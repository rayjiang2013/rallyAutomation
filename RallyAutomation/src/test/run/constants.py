'''
Created on Apr 15, 2015

@author: ljiang
'''
#test case execution steps
STEPS_SUP_EXE_FLC_VER=0
STEPS_SUP_EXE_FLC_VER_CLU=1
STEPS_EXE_FLC_VER=2

#associated test step index
INDEXES_SUP=[17,18,19,20,21]
INDEXES_EXE=[0,1,2,3]
INDEXES_FLC=[4,5,6,22]
INDEXES_VER=[7,8,9,10,11]
INDEXES_CLU=[12,13,14,15,16]

#test case status
FAILED=0
SUCCESS=1
BLOCKED=2

#limitation
MAX_NOTE_LENGTH=32768

#ScheduleState in Rally
INPROGRESS=0
ACCEPTED=1
COMPLETED=2

#functional test case or api test case
FUNC_LVL_TC=0
API_LVL_TC=1

#generate the report from Rally test result or exception
FROM_TR=1
FROM_EXCEPTION=0

#number of test case fields
NO_TC_FIELDS=23

#ping commands options
PING_COMMAND = {'Darwin'  : ["ping", "-o", "-c", "2", "-t", "2"],
                'Unix'    : ["ping",       "-c", "2", "-w", "2"],
                'Linux'   : ["ping",       "-c", "2", "-w", "2"],
                'Windows' : ["ping",       "-n", "2", "-w", "2"],
                'Cygwin'  : ["ping",       "-n", "2", "-w", "2"]
                }

#IP to check
CHECK_IP = ['10.10.2.166', '10.10.3.107', '10.10.2.59',
            '10.10.3.208', 'rally1.rallydev.com', 'localhost']