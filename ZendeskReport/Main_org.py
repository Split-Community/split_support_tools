import ZendeskObj
import Constants
import time
from zenpy.lib.api_objects import OrganizationField
from csv import reader

###############################################################
constants = Constants.Constants()
userEmail=constants.USEREMAIL
apiToken=constants.APITOKEN
subDomain=constants.SUBDOMAIN
###############################################################

zenObj=ZendeskObj.ZendeskObj(userEmail, apiToken, subDomain)

with open('gainsight.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    next(csv_reader, None) 
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
#        print("zendesk: "+row[3])
        #print(row[2])
        search = zenObj.getOrganization(row[0])
        if search.count>0:        
            orgId = search._response_json['results'][0]['id']
#        org = zenObj.getOrgFields(row[4])
            org = zenObj.getOrgFields(orgId)
            print(org.organization_fields)
#            org.organization_fields['organization_id'] = row[2]
            org.organization_fields['csm'] = row[1]
            #print(org.organization_fields['csm'])
            #org.organization_fields['package'] = row[2]
            #print(f"This is before edit" + str(org.organization_fields['csm']))
            
            org.organization_fields['sfdc_support_plan_type'] = row[2]
            
            #print(f"This is after edit" + str(org.organization_fields['csm']))
            #org.organization_fields['sfdc_plan_type']
            #print()
#            org.external_id = row[3]
            zenObj.UpdateOrg(org)
            
            print(row[0]+","+str(org.id)+","+row[1]+","+str(org.organization_fields['csm']))
#            print("org: "+row[0]+", id: "+str(org.id)+", split  id: "+org.organization_fields['organization_id'])
        else:
            print(row[0]+",not found,,")
            

'''


def ExportToCSV(results, maxFields, fileName, header):
    reportObj = open(fileName, "w")
    reportObj.write(header)
    for rs in results:
        out=""
        for i in range(maxFields+1):
#            out=out+rs[i].encode('ascii','ignore')+','
            out=out+rs[i]+','
#        print rs[0], rs[1]
        out=out[:-1]+"\n"
        reportObj.write(out)
    reportObj.close()

output=[]
#orgObj = open("danielle_orgs.csv", "r")
print("plan,csm,name,external id,id")
#customer account name, csm, support plan, sales force id (external id), zendesk org id
#for orgName in orgObj.readlines():
for org in zenObj.getAllOrgFields():    
    if str(org.organization_fields['sfdc_plan_type'])=="PAID":
        print (str(org.organization_fields['sfdc_support_plan_type'])+","+str(org.organization_fields['csm'])+","+org.name+","+str(org.external_id)+","+str(org.id))
#    org = zenObj.getOrganization(orgName)
#    if org.count>0:        
#        orgId = org._response_json['results'][0]['id']
#        print ("Org ID: "+str(orgId))
#        myOrg = zenObj.getOrgFields(orgId)
 #   output.append([orgName,"https://splitsoftware.zendesk.com/agent/organizations/"+str(orgId)])
#        myOrg.organization_fields.csm = "Alphonso Calanoc"
#        zenObj.zenpyClient.organizations.update(myOrg)
    
#ExportToCSV(output, 1, "danielle.csv", "org,url\n")

'''
