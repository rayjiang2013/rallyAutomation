'''
Created on Mar 31, 2015

@author: ljiang
'''
from testCase import testCase
from testSet import testSet
import inspect
import sys
import logging

class extractAPI(object):
    '''
    classdocs
    '''
    def __init__(self,rally,data):
        try:
            lines=[]
            with open('itest_api.txt') as f:
                for line in f.readlines():
                    if '-' not in line:
                        lines.append(line) 
            #print lines            
                #varbs.append(strg[i:].partition('$')[-1].partition('[\n\/\\\b\&\?\;\=]')[0])
                #f.
            ccts=[]
            for i in xrange(0,len(lines)):
                if i%2 != 0:
                    cct=lines[i-1]+lines[i]
                    ccts.append(cct)
            #print ccts        
            
            lst_lst=[]
            for cct,i in zip(ccts,xrange(0,len(ccts))):
                x=cct.partition(' ')[0]
                #rest=cct.strip(lst_lst[i][0])
                y=cct.partition('\"')[-1].partition('\"')[0]
                z=cct.partition("\'")[-1].rpartition('\'')[0]
                lst_lst.append([x,y,z])
            #Firstly create all these test cases
            tc_obj=testCase(rally,data)
            tcs=tc_obj.getAllTCs('Project = "https://rally1.rallydev.com/slm/webservice/v2.0/project/24755623223"' )
            tcs_names=[tc.Name for tc in tcs]
            for tc_data in lst_lst:
                if tc_data[0] in tcs_names:
                    continue
                data['tc'].update({        
                                        "Description": "API level test case",
                                        "Expedite": "false",
                                        "Method": "Automated",
                                        "Name": tc_data[0],
                                        "Objective": "",
                                        "TestFolder": "",
                                        "Type": "Acceptance",
                                        "Project": "https://rally1.rallydev.com/slm/webservice/v2.0/project/24755623223",
                                        "c_QATCPARAMSTEXT": tc_data[1]+"|"+tc_data[2]+"|||||||||||||||||||||||||||||||||||||||||||||||"})
                tc_obj.createTC()
            #The create test set and put all the test cases into it
            ts_obj=testSet(rally,data)
            tss=ts_obj.getAllTSs('Project = "https://rally1.rallydev.com/slm/webservice/v2.0/project/24755623223"')
            tss_names=[ts.Name for ts in tss]
            if "All API Level Test Cases" in tss_names:
                tss_api=ts_obj.getAllTSs('Name = "All API Level Test Cases"')
                if len(tss_api)>1:
                    raise Exception('More than one api level test set. Please delete one')
            else: ts=ts_obj.createTS({
                            "Name":"All API Level Test Cases",
                            "Owner": "https://rally1.rallydev.com/slm/webservice/v2.0/user/24343572282",
                            "Project": "https://rally1.rallydev.com/slm/webservice/v2.0/project/24755623223",
                            "ScheduleState": "Defined"
                            })
            
            tcs_api=tc_obj.getAllTCs('Description = "API level test case"' )
            tcs_names_api=[tc.Name for tc in tss_api[0].TestCases]    
            for tc in tcs_api:
                if not (tc.Name in tcs_names_api):
                    ts_obj.addSpecificTCs(tcs_api,ts)
            
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                print Exception,details
                #self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

        
    #print lst_lst        
    
    #ts_obj=testSet()
    
#extractAPIAndUpdateRally()