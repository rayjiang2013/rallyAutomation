'''
Created on Nov 10, 2014

@author: ljiang
'''
import sys
#from pprint import pprint
from testCase import *
#from testObject import *
#import datetime
#from user import *
#import user

import logging
#from rallyLogger import *
from types import *


class testSet(object):
    '''
    classdocs
    '''
    def __init__(self, rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        #rallyLogger.setup("logging.json")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
    
           
    #Show a TestSet identified by the FormattedID value
    def getTSByID(self):
        try:
            
            query_criteria = 'FormattedID = "%s"' % str(self.data['ts']['FormattedID'])
            response = self.rally.get('TestSet', fetch=True, query=query_criteria)
            dic={}
            for ts in response:
                for key in dir(ts):
                    if not key.endswith("__"):
                        dic[key]=getattr(ts,key)
                    #print key,getattr(ts,key)
                break        
            #print "Test set obtained, ObjectID: %s  FormattedID: %s " % (ts.oid,ts.FormattedID)
            #print "--------------------------------------------------------------------"
            #pprint(dic)
            self.logger.debug("Test set obtained, ObjectID: %s, FormattedID: %s, Content: %s" % (ts.oid,ts.FormattedID,dic))
            return (ts,dic)
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    #Fetch all the test cases of specific test set
    def allTCofTS(self,ts):
        try:
            lst=[]
            #ts_obj=testSet(self.rally,self.data)
            #ts=ts_obj.getTSByID()       
            query_criteria = 'TestSets = "%s"' % str(ts._ref)
            response = self.rally.get('TestCase', fetch=True, query=query_criteria, order='DragAndDropRank')
            for tc in response:
                lst.append(tc)
                #print "Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID)
                self.logger.debug("Test case obtained, ObjectID: %s  FormattedID: %s" % (tc.oid,tc.FormattedID))
            #self.logger.debug("The content of all test cases of test set %s is: %s" % (ts.FormattedID,lst))
            #pprint(lst)
            #print "--------------------------------------------------------------------"
            return lst
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)

    
    #Update test set
    def updateTS(self):
        try: 
            ts_data = {key: value for key, value in self.data['ts'].iteritems() if ((key == u'Name') or (key == u'ScheduleState') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build') or (key == u'FormattedID'))}
            #ts_data = self.data['ts']
            for key in ts_data.iterkeys():
                if ((type(ts_data[key]) is not unicode) and (type(ts_data[key]) is not str) and (type(ts_data[key]) is not int) and (type(ts_data[key]) is not bool) and (type(ts_data[key]) is not float)):
                    ts_data[key]=ts_data[key]._ref            
            ts = self.rally.post('TestSet', ts_data)  
            self.logger.debug("Test Set %s is updated" % ts.FormattedID)        
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)
        #print "Test Set %s updated" % ts.FormattedID
        #print "--------------------------------------------------------------------"
        return ts    
    
    #Update ScheduleState of Test Set 
    def updateSS(self,state):
        try:
            dic={}
            dic['ts']=self.data['ts'].copy()
            dic['ts'].pop('Build',None)
            dic['ts'].pop('Blocked',None)
            if state == 0:
                dic['ts']['ScheduleState']="In-Progress"
            if state == 1:        
                dic['ts']['ScheduleState']="Accepted"
            if state == 2:
                dic['ts']['ScheduleState']="Completed"
            #ts_obj=testSet(self.rally,dic)
            #ts_obj.updateTS()
            self.data=dic.copy()
            self.updateTS()
            self.logger.debug("ScheduleState is successfully updated to %s" % dic['ts']['ScheduleState'])
        except Exception,details:
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)
    
    #Create test set
    def createTS(self,ts_dic):
        ts_data={}
        #ts_data['Name'] = self.data['ts']['Name'] #Create a test set with the test set name defined in extra.json
        try:
            if ts_dic is not None:
                for key, value in ts_dic.iteritems():
                    #http://stackoverflow.com/questions/16069517/python-logical-evaluation-order-in-if-statement : The expression x and y first evaluates x; if x is false, its value is returned; otherwise, y is evaluated and the resulting value is returned.The expression x or y first evaluates x; if x is true, its value is returned; otherwise, y is evaluated and the resulting value is returned.
                    if (((key == u'Name') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build') ) and (value is not None)): 
                        ts_data[key]=value     
                #ts_data = {key: value for key, value in ts_dic.iteritems() if ((key == 'Name') or (key == 'ScheduleState') or (key == 'Project') or (key == 'Description') or (key == 'Owner') or (key == 'Ready') or (key == 'Release') or (key == 'PlanEstimate') or (key == 'Blocked') or (key == 'BlockedReason') or (key == 'Iteration') or (key == 'Expedite') or (key == 'Build'))}
            else: ts_data = {key: value for key, value in self.data['ts'].iteritems() if (((key == u'Name') or (key == u'Project') or (key == u'Description') or (key == u'Owner') or (key == u'Ready') or (key == u'Release') or (key == u'PlanEstimate') or (key == u'Blocked') or (key == u'BlockedReason') or (key == u'Iteration') or (key == u'Expedite') or (key == u'Build') ) and (value is not None))} #Create a test set with all fields of data['ts'] except the key value pair of 'FormattedID' and 'Build'        
            #ts_data['TestCases']=self.data['ts']['__collection_ref_for_TestCases']
            for key in ts_data.iterkeys():
                if ((type(ts_data[key]) is not unicode) and (type(ts_data[key]) is not str) and (type(ts_data[key]) is not int) and (type(ts_data[key]) is not bool) and (type(ts_data[key]) is not float)):
                    ts_data[key]=ts_data[key]._ref
            ts_data['ScheduleState']="Defined"
            ts = self.rally.put('TestSet', ts_data)

            self.data['ts'].update(ts_data)
            #self.data['ts']=ts_data
            self.logger.debug("Test set created, ObjectID: %s  FormattedID: %s" % (ts.oid, ts.FormattedID))      
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details,exc_info=True)
            sys.exit(1)
        
        return ts  
    '''
    #Copy test set
    def copyTS(self):
        try:
            (ts_origin,ts_origin_dic)=self.getTSByID()
            ts_dst=self.createTS(ts_origin_dic)
            self.addTCs(ts_origin,ts_dst)
            self.logger.debug("Test set %s is copied to test set %s" % (ts_origin.FormattedID, ts_dst.FormattedID))
        except Exception, details:
            self.logger.error('ERROR: %s \n' % details)
            sys.exit(1)
    '''
    
    #Add test cases to test set; remember to use _ref (ref is like abc/12345 and will result in some issue in debug mode
    #. _ref is like http://xyc/abc/12345) as reference to an object when needed. 
    #Ex: http://stackoverflow.com/questions/21718491/how-to-add-new-testcases-to-an-existing-rally-folder
    def addTCs(self,ts_origin,ts_dst):
        try: 
            tcs=self.allTCofTS(ts_origin)
            dic = {'FormattedID': ts_dst.FormattedID,'TestCases':[] }    
            #rank=[]
            for tc in tcs:
                dic['TestCases'].append({'_ref' : str(tc._ref)}) 
                #rank.append(tc.DragAndDropRank)     
                self.logger.debug("Test case %s is added to Test set %s" % (tc.FormattedID,ts_dst.FormattedID))  
            new_ts=self.rally.post('TestSet', dic) 
            self.logger.debug("All test cases have been added to Test set %s" % ts_dst.FormattedID)
            #Rank it 
            #new_tcs=self.allTCofTS(new_ts)
            #i=0
            #for new_tc in new_tcs:            
                #tc_rank_dic={'FormattedID':new_tc.FormattedID,'DragAndDropRank':rank[i]}
                #tc_rank=self.rally.post('TestCase', tc_rank_dic)
                #i+=1
            return new_ts
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)    
    
    #Manually add the test case because of the Rally bug: https://rallydev.force.com/cases/detail?id=5001400000mYFVuAAO
    def manualAddTCs(self,ts_dst):
        try: 
            tcids=self.data['ts']['TestCases']
            dic = {'FormattedID': ts_dst.FormattedID,'TestCases':[]}    
            for tcid in tcids:
                self.data['tc']['FormattedID']=tcid
                tc_obj=testCase(self.rally,self.data)
                tc=tc_obj.getTCByID()
                dic['TestCases'].append({'_ref' : str(tc._ref)})
                self.logger.debug("Test case %s will be added to Test set %s" % (tc.FormattedID,ts_dst.FormattedID))  
            new_ts=self.rally.post('TestSet', dic) 
            self.logger.debug("All test cases have been added to Test set %s" % ts_dst.FormattedID)
            return new_ts
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            self.logger.error('ERROR: %s \n' % details, exc_info=True)
            sys.exit(1)            

    #Delete test case
    def delTS(self):
        try: 
            delete_success=self.rally.delete('TestSet', self.data['ts']['FormattedID'])
        except Exception, details:
            self.logger.error('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['ts']['FormattedID']), exc_info=True)
            sys.exit(1)
        if delete_success == True:
            self.logger.debug("Test set deleted, FormattedID: %s" % self.data['ts']['FormattedID'], exc_info=True)

    
    '''
    #Run the test set
    def runTS(self): 
        ts_obj=testSet(self.rally,self.data)
        ts=ts_obj.getTSByID()
        tcs=ts_obj.allTCofTS()
        to_obj=testObject(self.rally,self.data)
        tc_verds=to_obj.runTO() #run the actual tests for AVNext
        ur_obj=user(self.rally,self.data)   
        ur=ur_obj.getUser()
        trs=[]     
        for tc,verd in zip(tcs,tc_verds):
            if verd == 0:
                dic = {'TestCase':tc._ref,'Verdict':u'Fail','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}      
            if verd == 1:
                dic = {'TestCase':tc._ref,'Verdict':u'Pass','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref}
            try:
                tr=self.rally.put('TestCaseResult', dic) 
                trs.append(tr)          
            except Exception, details:
                sys.stderr.write('ERROR: %s \n' % details)
                sys.exit(1)
            print "Test Case %s updated; Test result oid %s is created" % (tc.FormattedID,tr.oid)

        #Generate report
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                for tr in trs:
                    f.write("Test Report:\nTest Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" % (tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Report %s is successfully generated" % filename        
        return trs
        
        
                           
                              
                    
                    
                     
                    
    
    #Create test case
    def createTC(self):
        tc_data = {key: value for key, value in self.data['tc'].items() if key is not 'FormattedID'} #Create a test case with all fields of data['tc'] except the key value pair of 'FormattedID'
        try:
            tc = self.rally.put('TestCase', tc_data)
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test case created, ObjectID: %s  FormattedID: %s" % (tc.oid, tc.FormattedID)      
        return tc  
        
    #Update test case
    def updateTC(self):
        tc_data = self.data['tc']
        try: 
            tc = self.rally.post('TestCase', tc_data)          
        except Exception, details:
            sys.stderr.write('ERROR: %s \n' % details)
            sys.exit(1)
        print "Test Case %s updated" % tc.FormattedID
        return tc
    
    #Delete test case
    def delTC(self):
        try: 
            delete_success=self.rally.delete('TestCase', self.data['tc']['FormattedID'])
        except Exception, details:
            sys.stderr.write('ERROR: %s %s %s does not exist\n' % (Exception,details,self.data['tc']['FormattedID']))
            sys.exit(1)
        if delete_success == True:
            print "Test case deleted, FormattedID: %s" % self.data['tc']['FormattedID']        
    '''
