'''
Created on Nov 10, 2014

@author: ljiang
'''


#from testSet import *
from smtplib import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sys
from testSet import testSet
import datetime
from user import user
from testCaseResult import testCaseResult
import logging
from defect import defect
import requests
import ast
from copy import deepcopy
import inspect
from buildDefinition import buildDefinition
from build import build

from jenkinsNotifier import jenkinsNotifier
from dateutil import tz

import json


class testObject(object):
    '''
    classdocs
    '''


    def __init__(self,rally,data):
        '''
        Constructor
        '''
        self.data=data
        self.rally=rally
        #setup("logging.json")
        #logger.debug("testObject is initiated successfully")
        self.logger = logging.getLogger(__name__)
        self.logger.propagate=False
    
    def sanityCheck(self):
        try:
            pass
            #raise Exception
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        self.logger.info("Sanity check is successfully performed")
        return True
    
    #Get last build information. 
    def getLastBuildInfoFromJenkins(self):
        try:
            jenkins_obj=jenkinsNotifier(self.rally,self.data)
            server=jenkins_obj.getServerInstance()
            build_obj,job_obj=jenkins_obj.getLastBuildInfo(server)
            duration_list=str(build_obj.get_duration()).split(':')
            duration_double=int(duration_list[0])*3600+int(duration_list[1])*60+float(duration_list[2])
            utc1=str(build_obj.get_timestamp()).split('+')[0] #2015-03-19 00:01:35+00:00
            utc2=datetime.datetime.strptime(utc1,'%Y-%m-%d %H:%M:%S')
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            utc2 = utc2.replace(tzinfo=from_zone)
            local = utc2.astimezone(to_zone)
            local_iso=local.isoformat()
            bd_dict={
                     'Number':build_obj.get_number(),
                     'Duration':duration_double,
                     'Uri':build_obj.baseurl, 
                     'Message':'Build for job '+job_obj.name+ ' was successful.',
                     'Status': build_obj.get_status(),
                     'Start':local_iso
                     }
            bddf_dict={
                       'Name':job_obj.name
                       }
            self.data['build'].update(bd_dict)
            self.data['builddf'].update(bddf_dict)
            self.logger.info("The last build information at Jenkins instance %s is successfully obtained" % (server.baseurl))
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)            
    
    #Update build info
    def updateBuildInfo(self):
        try:
            
            builddf_obj=buildDefinition(self.rally,self.data)
            builddfs=builddf_obj.getAllBuildDefinitions()
            for builddf in builddfs:
                if builddf.Name == self.data['builddf']['Name']:
                    break
            else:   
                new_builddf=builddf_obj.createBuildDefinition()
                self.logger.info("New build definition name %s is created" % (new_builddf.Name))
            
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bd=build_obj.createBuild()
            #self.data['ts']['Build']=build.Number
            self.logger.info("Build name %s number %s is created" % (bd.Name, bd.Number))

            if bd.Status=="SUCCESS":
                return
            else: raise Exception('Build failed')

        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)        
    
    #Get build information
    def getBuildInfo(self):
        try:
            builddf_obj=buildDefinition(self.rally,self.data)
            builddf=builddf_obj.getBuildDefinitionByName()
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bd=build_obj.getBuild()
            #self.data['ts']['Build']=build.Number
            self.logger.info("Build name %s number %s is obtained" % (bd.Name, bd.Number))

            if bd.Status=="SUCCESS":
                return
            else: raise Exception('Build failed')

        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)


    #Get build information
    def getLatestBuild(self):
        try:
            builddf_obj=buildDefinition(self.rally,self.data)
            builddf=builddf_obj.getBuildDefinitionByName()
            data_with_bddf_ref=deepcopy(self.data)
            data_with_bddf_ref['build'].update({'BuildDefinition':builddf._ref})
            build_obj=build(self.rally,data_with_bddf_ref)
            bds=build_obj.getAllBuilds()
            sorted_bds=sorted(bds, key=lambda x: x.CreationDate, reverse=True)
            bd=sorted_bds[0]
            #build_number=bd.number
            self.data['ts']['Build']=bd.Number
            self.logger.info("Latest build name %s number %s is obtained" % (bd.Name, bd.Number))
            
            if bd.Status=="SUCCESS":
                return
            else: raise Exception('Build failed')

        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)                
    
    #Copy test set
    def copyTS(self):
        try:
            ts_obj=testSet(self.rally,self.data)
            (ts_origin,ts_origin_dic)=ts_obj.getTSByID()
            ts_dst=ts_obj.createTS(ts_origin_dic)
            ts_new=ts_obj.addTCs(ts_origin,ts_dst)
            self.logger.info("Test set %s is copied to test set %s" % (ts_origin.FormattedID, ts_dst.FormattedID))
            #self.data['ts']={}
            #self.data['ts']['FormattedID']=ts_dst.FormattedID
            #self.logger.info("The test set is successfully copied")
            return ts_new
        except Exception, details:

            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)

    #Replace variable
    def rep(self,strg,tc,ts):
        varbs=[]
        for i in xrange(0,len(strg)):
            if strg[i]=='$':
                varbs.append(strg[i:].partition('$')[-1].partition('[\n\/\\\b\&\?\;\=]')[0])
                if varbs[-1] in self.data['env']:
                    strg=strg.replace('$'+varbs[-1]+'%',self.data['env'][varbs[-1]])
                else:
                    self.logger.debug("The test case %s for build %s in test set %s is failed to setup because %s in extra.json is not defined." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID,varbs[-1]))    
                    return False,strg
        return True,strg

    #Setup
    def setup(self,lst,tc,ts,s_ession):
        try:
            if lst[1]!= u'':
                lst[1]=self.data['env']['ControllerURL']+lst[1]
            if lst[7]!= u'':
                lst[7]=self.data['env']['ControllerURL']+lst[7]
            if lst[12]!= u'':
                lst[12]=self.data['env']['ControllerURL']+lst[12]
            if lst[17]!=u'':
                lst[17]=self.data['env']['ControllerURL']+lst[17]            

            r_stp=None
            if lst[17]==u"":
                self.logger.debug("As not enough setup information is provided, the test setup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                
                if '$' in lst[1]:
                    rep_status,lst[1]=self.rep(lst[1],tc,ts)
                    if rep_status==False:
                        return False,lst
                if '$' in lst[7]:
                    rep_status,lst[7]=self.rep(lst[7],tc,ts)
                    if rep_status==False:
                        return False,lst                                       
                if '$' in lst[12]:
                    rep_status,lst[12]=self.rep(lst[12],tc,ts)
                    if rep_status==False:
                        return False,lst
                if '$' in lst[17]:
                    rep_status,lst[17]=self.rep(lst[17],tc,ts)
                    if rep_status==False:
                        return False,lst
                
                if lst[16] == "GET":
                    r_stp = s_ession.get(lst[17])                        
                if lst[16] == "POST":
                    r_stp = s_ession.post(lst[17],data=json.loads(lst[18]))
                if lst[16] == "DELETE":
                    r_stp = s_ession.delete(lst[17])
                if lst[16] == "PUT":
                    r_stp = s_ession.put(lst[17],data=json.loads(lst[18]))

        
                if r_stp.status_code != int(lst[19]):
                    self.logger.debug("The test case %s for build %s in test set %s is failed to setup because status code is unexpected." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))    
                    return False,lst          
                else:
                    if (lst[20] != u'' ):
                        '''
                        ver_point = ast.literal_eval(lst[18])
                        r_ver_content=deepcopy(r_stp.content)
                        r1= r_ver_content.replace("true","\"true\"")
                        r2= r1.replace("false","\"false\"")    
                        r_ver_content=ast.literal_eval(r2)
                        '''
                        ver_point=deepcopy(json.loads(lst[20]))
                        r_ver_content=deepcopy(json.loads(r_stp.content))
                        
                        error_message=self.searchDict2(ver_point,r_ver_content,"")
                        if error_message=='':
                            self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                        else:
                            self.logger.debug("The test case %s for build %s in test set %s is failed to setup because the content of response body is unexpected" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))   
                            return False,lst
                    else:
                        self.logger.debug("The test case %s for build %s in test set %s is setup successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
            return True,lst 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)       
        
    

    #Test execution
    def executor(self,lst,tc,s_ession):
        try:
            #lst=tc.c_QATCPARAMSSTRING.split('|')
            '''
            if lst[1]!= u'':
                lst[1]=self.data['env']['ControllerURL']+lst[1]
            if lst[6]!= u'':
                lst[6]=self.data['env']['ControllerURL']+lst[6]
            if lst[10]!= u'':
                lst[10]=self.data['env']['ControllerURL']+lst[10]
            '''
            if lst[0] == "GET":
                r = s_ession.get(lst[1])                        
            if lst[0] == "POST":#only support http for now, verify = false
                r = s_ession.post(lst[1],data=json.loads(lst[2]),verify=False)
            if lst[0] == "DELETE":
                r = s_ession.delete(lst[1])
            if lst[0] == "PUT":#only support http for now, verify = false
                r = s_ession.put(lst[1],data=json.loads(lst[2]),verify=False)
            
            self.logger.debug("The test case %s for build %s is executed." % (tc.FormattedID,self.data["ts"]["Build"]))       
            return (r,lst) 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1) 


    #search dictionary recursively
    def searchDict(self,dict1,dict2):
        try:
            for item2 in dict2.items():                
                for item1 in dict1.items():
                    if item2[0]==item1[0]:
                        if (type(item2[1]) != dict):
                            if item2[1]==dict1[item1[0]]:
                                #verified=True
                                status=1
                                #verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                                #verdict.append((1,'Success: status code expected and verified'))
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))  
                                break         
                            else: 
                                status=2
                                #verdict[-1]=(0,'Failure: verification failed')
                                #verified=False
                                #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                                return status   
                        else:
                            return self.searchDict(item1[1],item2[1])
                            #break
                else:
                    status=2
                    #verdict[-1]=(0,'Failure: verification failed')
                    #verified=False
                    #self.logger.debug("The test execution for test case %s, build %s is verified to be failed." % (tc.FormattedID,self.data["ts"]["Build"]))   
                    return status                           
            return status
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)     
    
    def searchDict2(self,d1, d2, error_message):
        #print "Changes in " + ctx
        for k in d1:
            if k not in d2:
                #print "%s:%s is missing from content of response" % (k,d1[k])
                error_message+= " '"+k+"' : "+str(d1[k])+" is missing from content of response."
        for k in d2:
            
            if k not in d1:
                #print k + " added in d2"
                continue
            
            if d2[k] != d1[k]:
                if type(d2[k]) != dict:
                    #print "%s:%s is different in content of response" % (k,str(d2[k]))
                    error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                else:
                    if type(d1[k]) != type(d2[k]):
                        error_message+= " '"+k+"' : "+str(d2[k])+" in content of response is different from the expected." 
                        continue
                    else:
                        if type(d2[k]) == dict:
                            error_message=self.searchDict2(d1[k], d2[k],error_message)
                            continue
        #print "Done with changes in " + ctx
        return error_message
    
    
    #First level check
    def firstLevelCheck(self,lst,r,verdict,tc,s_ession):
        try: 
            if r.status_code != int(lst[3]):
                #Run Env Sanity Check
                #to_obj=testObject(self.rally,self.data)       
                if self.sanityCheck():
                    verdict.append((0,'Failure: status code unexpected. The unexpected status code of the response is %s' % r.status_code)) 
                    self.logger.debug("Test case %s, build %s failed because status code unexpected. The unexpected status code of the response is %s" % (tc.FormattedID,self.data["ts"]["Build"],r.status_code))                       
                    #return verdict
                else:    
                    raise Exception('Environment sanity check failed')
                    #verdict.append((0,'Failure: sanity check of environment failed'))            
            else:
                if (lst[4] != u'' ):# and (r.content==str(lst[4])):

                    #ver_point = ast.literal_eval(lst[4])
                    ver_point=deepcopy(json.loads(lst[4]))
                    r_ver_content=deepcopy(json.loads(r.content))
                    #r1= r_ver_content.replace("true","\"true\"")
                    #r2= r1.replace("false","\"false\"")    
                    #r_ver_content=ast.literal_eval(r2)
                    

                    error_message=self.searchDict2(ver_point,r_ver_content,"")
                    if error_message=='':
                        #First level check succeed
                        #z=ast.literal_eval(lst[4])
                        if 'message' in r.content:
                            verdict.append((1,'Success: status code expected and first level check succeed. Message: '+ver_point['message']))
                        else:
                            verdict.append((1,'Success: status code expected and first level check succeed.'))
                        self.logger.debug("First level check for Test case %s, build %s is successful." % (tc.FormattedID,self.data["ts"]["Build"]))
                    else:
                        #First level check failed
                        verdict.append((0,'Failure: status code expected but first level check failed. Error:%s' % error_message))
                        self.logger.debug("Test case %s, build %s failed because first level check failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))   
                    

                else:
                    verdict.append((1,'Success: status code expected without first level check.'))
                    self.logger.debug("Test case %s, build %s is successful without first level check." % (tc.FormattedID,self.data["ts"]["Build"]))
         
            
            return verdict
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)           
    


    
    #Test verification:
    def verificator(self,lst,r,verdict,tc,s_ession):
        try:
            #Verification

            if (lst[8]==u"" or lst[6]==u"" or lst[7]==u""):
                self.logger.debug("As not enough verification information is provided, the test execution for test case %s, build %s is not verified" % (tc.FormattedID,self.data["ts"]["Build"]))
                verdict[-1]=(verdict[-1][0],verdict[-1][1]+' No verification is done.')
            else:    
                if lst[8] == "GET":
                    r_ver = s_ession.get(lst[7])                        
                if lst[8] == "POST":
                    r_ver = s_ession.post(lst[7],data=json.loads(lst[9]))
                if lst[8] == "DELETE":
                    r_ver = s_ession.delete(lst[7])
                if lst[8] == "PUT":
                    r_ver = s_ession.put(lst[7],data=json.loads(lst[9]))
                '''
                ver_point = ast.literal_eval(lst[5])
                r_ver_content=deepcopy(r_ver.content)
                r1= r_ver_content.replace("true","\"true\"")
                r2= r1.replace("false","\"false\"")    
                r_ver_content=ast.literal_eval(r2)
                #keys_ver_point,values_ver_point=ver_point.keys(),ver_point.values()
                #keys_r_ver_content,values_r_ver_content=r_ver_content.keys(),r_ver_content.values()
                '''
                ver_point=deepcopy(json.loads(lst[6]))
                r_ver_content=deepcopy(json.loads(r_ver.content))
                
                error_message=self.searchDict2(ver_point,r_ver_content,"")
                if error_message=='':
                    verdict[-1]=(verdict[-1][0],verdict[-1][1]+' Verification is successful.')
                    #verdict.append((1,'Success: status code expected and verified'))
                    self.logger.debug("The test execution for test case %s, build %s is verified to be successful." % (tc.FormattedID,self.data["ts"]["Build"]))                  
                else:
                    verdict[-1]=(0,'Failure: verification failed. Error:%s' % error_message)
                    self.logger.debug("The test execution for test case %s, build %s is verified to be failed. Error: %s" % (tc.FormattedID,self.data["ts"]["Build"],error_message))   

            return verdict
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)                       
        
    #Cleanup
    def cleaner(self,lst,tc,ts,s_ession):
        try:
            r_clr=None
            if lst[12]==u"":
                self.logger.debug("As not enough cleanup information is provided, the test cleanup for test case %s, build %s, test set %s is skipped" % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
            else: 
                if lst[11] == "GET":
                    r_clr = s_ession.get(lst[12])                        
                if lst[11] == "POST":
                    r_clr = s_ession.post(lst[12],data=json.loads(lst[13]))
                if lst[11] == "DELETE":
                    r_clr = s_ession.delete(lst[12])
                if lst[11] == "PUT":
                    r_clr = s_ession.put(lst[12],data=json.loads(lst[13]))
                '''    
                if int(lst[12])==r_clr.status_code:              
                    self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                else: 
                    raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                    #self.logger.debug("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                '''
        
                if r_clr.status_code != int(lst[14]):
                    raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                
                else:
                    if (lst[15] != u'' ):
                        '''
                        ver_point = ast.literal_eval(lst[13])
                        r_ver_content=deepcopy(r_clr.content)
                        r1= r_ver_content.replace("true","\"true\"")
                        r2= r1.replace("false","\"false\"")    
                        r_ver_content=ast.literal_eval(r2)
                        '''
                        ver_point=deepcopy(json.loads(lst[15]))
                        r_ver_content=deepcopy(json.loads(r_clr.content))
                        
                        error_message=self.searchDict2(ver_point,r_ver_content,"")
                        if error_message=='':
                            self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))
                        else:
                            raise Exception("The test case %s for build %s in test set %s is failed to clean up." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))                    
                    else:
                        self.logger.debug("The test case %s for build %s in test set %s is cleaned up successfully." % (tc.FormattedID,self.data["ts"]["Build"],ts.FormattedID))       
                 
        except Exception, details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        
    #Main execution wrapper      
    def runTO(self,testset_under_test):
         
        try:
            
            verdict=[]
            for tc in testset_under_test.TestCases:
                sorted_trs=sorted(tc.Results, key=lambda x: x.Date, reverse=True)
                #Check if the test case is blocked in most recent run with current build. For...else is used(http://psung.blogspot.com/2007/12/for-else-in-python.html)
                for tr in sorted_trs:
                    if self.data['ts']['Build']==tr.Build:
                        if tr.Verdict=='Blocked':                            
                            #dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Blocked','Build':self.data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':testset_under_test._ref}  
                            #update test case result
                            #tcr=testCaseResult(self.rally,dic)                
                            #tr=tcr.createTCResult() 
                            verdict.append((2,'Blocked: the test case is blocked in last test run with same build id %s' % self.data["ts"]["Build"]))
                            self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            break
                        else:
                            lst=tc.c_QATCPARAMSTEXT.split('|')
                            s = requests.session()
                            setup_result,lst=self.setup(lst, tc, testset_under_test, s)
                            if setup_result==True:
                                (response,lst_of_par)=self.executor(lst,tc,s)
                                verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                                if verdict[-1][0]!=0:
                                    verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                                self.cleaner(lst_of_par, tc,testset_under_test,s)
                            else:
                                verdict.append((2,'Blocked: the test case is blocked because the test setup failed'))
                                self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
                            break
                                                        
                else:
                    lst=tc.c_QATCPARAMSTEXT.split('|')
                    s = requests.session()
                    setup_result,lst=self.setup(lst, tc, testset_under_test, s)
                    if setup_result==True:
                        (response,lst_of_par)=self.executor(lst,tc,s)
                        verdict=self.firstLevelCheck(lst_of_par, response, verdict, tc,s)
                        if verdict[-1][0]!=0:
                            verdict=self.verificator(lst_of_par, response, verdict, tc,s)
                        self.cleaner(lst_of_par, tc,testset_under_test,s)
                    else:
                        verdict.append((2,'Blocked: the test case is blocked because the test setup failed'))
                        self.logger.debug("The test case %s is blocked for build %s, will skip it." % (tc.FormattedID,self.data["ts"]["Build"]))
            
            #Update ScheduleState of Test Set 
            new_data=deepcopy(self.data) 
            new_data['ts']['FormattedID']=testset_under_test.FormattedID
            ts_obj=testSet(self.rally,new_data)
            ts_obj.updateSS(0) 
                    
            #verdict=[0,1,1]
            #verdict=[(0,"Failure reason 3"),(1,"Success reason 3"),(0,"Failure reason 4"),(1,"Success reason 4")]
            self.logger.info("The test run is successfully executed on Chasis")
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        return (verdict,new_data)
    
    #Run the test set
    def runTS(self,tc_verds,new_data): 
        try:
            ts_obj=testSet(self.rally,new_data)
            ts=ts_obj.getTSByID()[0]
            tcs=ts_obj.allTCofTS(ts)
            #to_obj=testObject(self.rally,self.data)
            #tc_verds=to_obj.runTO() #run the actual tests for AVNext
            ur_obj=user(self.rally,new_data)   
            ur=ur_obj.getUser()
    
            trs=[]
            num_pass=0     
            for tc,verd in zip(tcs,tc_verds):
                dic={}
                if verd[0] == 0:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Fail','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}  
                    df_obj=defect(self.rally,dic)   
                    dfs=df_obj.allDFofTC(tc)
                    i=1
                    #if there is no existing defects in the test case, just create one
                    if len(dfs)==0:
                        #if not exist create new issue for the failed test cases
                        create_df={"FoundInBuild": new_data['ts']['Build'],
                                    "Project": ts.Project._ref,
                                    "Owner": ts.Owner._ref,
                                    "ScheduleState":"Defined",
                                    "State":"Submitted",
                                    "Name":"Error found in %s: %s" % (tc.FormattedID,tc.Name),
                                    "TestCase":tc._ref}
                        new_data['df'].update(create_df)
                        df_obj=defect(self.rally,new_data)
                        new_df=df_obj.createDF()
                        
                        #update test case result
                        tcr=testCaseResult(self.rally,dic)                
                        #tr=self.rally.put('TestCaseResult', dic)
                        tr=tcr.createTCResult() 
                        trs.append(tr)  
                            
                        #update defect with link to test case result
                        update_df={'df':None}
                        update_df['df']={"FormattedID":new_df.FormattedID,"TestCaseResult":tr._ref}
                        df_obj=defect(self.rally,update_df)
                        df_obj.updateDF()    
                        self.logger.debug("The defect %s is linked to test case result %s" % (new_df.FormattedID,tr._ref))  
                    for df in dfs:
                        #if not exist create new issue for the failed test cases
                        if (not hasattr(df.TestCaseResult,'Notes')) or (str(df.TestCaseResult.Notes) != dic['tcresult']['Notes']):
                            if i==len(dfs):

                                create_df={"FoundInBuild": new_data['ts']['Build'],
                                            "Project": ts.Project._ref,
                                            "Owner": ts.Owner._ref,
                                            "ScheduleState":"Defined",
                                            "State":"Submitted",
                                            "Name":"Error found in %s: %s" % (tc.FormattedID,tc.Name),
                                            "TestCase":tc._ref}
                                new_data['df'].update(create_df)
                                df_obj=defect(self.rally,new_data)
                                new_df=df_obj.createDF()
                                
                                #update test case result
                                tcr=testCaseResult(self.rally,dic)                
                                #tr=self.rally.put('TestCaseResult', dic)
                                tr=tcr.createTCResult() 
                                trs.append(tr)  
                                
                                #update defect with link to test case result
                                update_df={'df':None}
                                update_df['df']={"FormattedID":new_df.FormattedID,"TestCaseResult":tr._ref}
                                df_obj=defect(self.rally,update_df)
                                df_obj.updateDF()    
                                self.logger.debug("The defect %s is linked to test case result %s" % (new_df.FormattedID,tr._ref))         
                            i+=1                                
                            continue        
                        #if exist
                        else:
                            #check if the defect is marked as fixed or closed
                            if df.State == "Fixed" or df.State == "Closed":
                                update_df={'df':None}
                                #reopen the defect, make notes about the build, env and steps. Assign to someone
                                update_df['df']={"FormattedID":df.FormattedID,"State":"Open","Owner":getattr(df.Owner,'_ref',None),"Notes":df.Notes+"<br>The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}        
                                self.logger.debug("The defect %s is reproduced in build %s, test set %s, test case %s. Will re-open and update it with repro info" % (df.FormattedID,new_data['ts']['Build'],ts.FormattedID,tc.FormattedID))                      
                            else: #inserting notes. 
                                update_df={'df':None}
                                #print df.Notes
                                update_df['df']= {"FormattedID":df.FormattedID,"Notes":df.Notes+"<br>The defect is reproduced in build %s, test set %s, test case %s.<br />" % (new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)}
                                self.logger.debug("The defect %s is reproduced in build %s, test set %s, test case %s. Will update it with repro info" % (df.FormattedID,new_data['ts']['Build'],ts.FormattedID,tc.FormattedID)) 
                            df_obj=defect(self.rally,update_df)
                            df_obj.updateDF()   

                            #update test case result
                            tcr=testCaseResult(self.rally,dic)                
                            #tr=self.rally.put('TestCaseResult', dic)
                            tr=tcr.createTCResult() 
                            trs.append(tr)  
                            break
                                                   

                elif verd[0] == 1:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Pass','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}
                    num_pass=num_pass+1

                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    #tr=self.rally.put('TestCaseResult', dic)
                    tr=tcr.createTCResult() 
                    trs.append(tr)          

                elif verd[0] == 2:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Blocked','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':verd[1]}  
                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    tr=tcr.createTCResult()    
                    trs.append(tr) 
                
                else:
                    dic['tcresult'] = {'TestCase':tc._ref,'Verdict':u'Error','Build':new_data["ts"]["Build"],'Date':datetime.datetime.now().isoformat(),'TestSet':ts._ref,'Tester':ur._ref,'Notes':'Unexpected verdict'}  
                    #update test case result
                    tcr=testCaseResult(self.rally,dic)                
                    tr=tcr.createTCResult()    
                    trs.append(tr) 
                                 
            if num_pass == len(tc_verds):
                ts_obj.updateSS(1) 

            else:
                ts_obj.updateSS(2)       
            self.logger.info("The test set %s on Rally is successfully updated with test execution information" % ts.FormattedID)     
        except Exception,details:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        return trs
        
    #Generate report
    def genReport(self,trs):
        filename="Report-%s.log" % datetime.datetime.now()
        try:
            with open(filename,"ab+") as f:
                i=0
                for tr in trs:
                    if i == 0:
                        f.write("Test Report for Test Set %s:\n" % tr.TestSet.FormattedID)
                        i+=1                       
                    f.write("Test Case ID: %s\nBuild: %s\nVerdict: %s\nDate: %s\nTester: %s\n" % (tr.TestCase.FormattedID,tr.Build,tr.Verdict,tr.Date,tr.Tester.UserName))
            self.logger.info('Report %s is successfully generated' % filename)
        except Exception, details:
            #sys.stderr.write('ERROR: %s \n' % details)
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error('ERROR: %s \n' % details,exc_info=True)
                sys.exit(1)
        #print "Report %s is successfully generated" % filename   
        #print "--------------------------------------------------------------------"     
        return filename
            
    
    #Send email notification; two ways - 1.http://z3ugma.github.io/blog/2014/01/26/getting-python-working-on-microsoft-exchange/    not working, hold for now
    #2. http://www.tutorialspoint.com/python/python_sending_email.htm
    # Also, the current smtp server of spirent doesnot allow sending email to email address outside the spirent domain.
    def sendNotification(self,fname):
        try:
            #Create the email.
            msg = MIMEMultipart()
            msg["Subject"] = str(self.data['email']['EMAIL_SUBJECT']) #EMAIL_SUBJECT 
            msg["From"] =  str(self.data['email']['EMAIL_FROM']) #EMAIL_FROM   
            msg["To"] =  str(",".join(self.data['email']['EMAIL_RECEIVER'])) #",".join(EMAIL_RECEIVER)   
            #body = MIMEMultipart('alternative')
            #body.attach(MIMEText("test", TEXT_SUBTYPE))
            #Attach the message
            #msg.attach(body)
            #Attach a text file
            msg.attach(MIMEText(file(fname).read()))  
        
            #smtpObj = SMTP(GMAIL_SMTP, GMAIL_SMTP_PORT)
            smtpObj = SMTP(str(self.data['email']['EMAIL_SMTP']), self.data['email']['EMAIL_SMTP_PORT'])
            #Identify yourself to GMAIL ESMTP server.
            smtpObj.ehlo()
            #Put SMTP connection in TLS mode and call ehlo again.
            #smtpObj.starttls()
            #smtpObj.ehlo()
            #Login to service
            #smtpObj.login(None,None)#user=EMAIL_FROM, password=EMAIL_PASSWD) Actually the spirent smtp server does not allow authentication, so no login is needed
            #Send email
            #smtpObj.sendmail(EMAIL_FROM, EMAIL_RECEIVER, msg.as_string())
            smtpObj.sendmail(msg["From"], msg["To"].split(','), msg.as_string())
            #close connection and session.
            smtpObj.quit()
            #print "The report is successfully sent"
            #print "--------------------------------------------------------------------"
            self.logger.info("The report is successfully sent")
        except SMTPException as error:
            #x=inspect.stack()
            if 'test_' in inspect.stack()[1][3] or 'test_' in inspect.stack()[2][3]:
                raise
            else:
                #print Exception,details
                self.logger.error("Error: unable to send email :  {err}".format(err=error),exc_info=True)
                sys.exit(1)
            #print "Error: unable to send email :  {err}".format(err=error)
            

