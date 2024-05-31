import ZendeskObj
import Constants
import sys
from tqdm import tqdm
from importlib import reload

###############################################################
constants = Constants.Constants()
userEmail=constants.USEREMAIL
apiToken=constants.APITOKEN
subDomain=constants.SUBDOMAIN
###############################################################

zenObj=ZendeskObj.ZendeskObj(userEmail, apiToken, subDomain)

#for vote in zenObj.getPostVotes(360030103051):
#    print(vote.user.name, vote.user.email)

import datetime

def get_date_input(prompt):
    while True:
        try:
            date_str = input(prompt)
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj
        except ValueError:
            print("Invalid date format. Please use 'YYYY-MM-DD'.")

#start_date = get_date_input("Enter the start date (YYYY-MM-DD): ")
#end_date = get_date_input("Enter the end date (YYYY-MM-DD): ")

def ExportToCSV(results, maxFields, fileName, header):
    reportObj = open(fileName, "w")
    reportObj.write(header)
    for rs in results:
        out=""
        for i in range(maxFields):
#            out=out+rs[i].encode('ascii','ignore')+','
            out=out+rs[i]+','
#        print rs[0], rs[1]
        out=out[:-1]+"\n"
        reportObj.write(out)
    reportObj.close()

def EscapeDoubleQuotes(title):
    return title.replace('"', '""')


def FixProdCat(oldCat):
    if oldCat=="api_general_question":
        return "API General Question"
    if oldCat=="api_users_and_groups":
        return "API Users and Groups"        
    if oldCat=="sdk_node.js":
        return "SDK NodeJS"
    if oldCat=="sdk__javascript":
        return "SDK Javascript"
    if oldCat=="sdk__sdk_react":
        return "SDK React"
    if oldCat=="sdk__sdk_redux":
        return "SDK Redux"
    if oldCat=="sdk_java":
        return "SDK Java"
    if oldCat=="sdk__python":
        return "SDK Python"
    if oldCat=="sdk__go":
        return "SDK GO"
    if oldCat=="sdk_php":
        return "SDK PHP"
    if oldCat=="sdk_ruby":
        return "SDK Ruby"
    if oldCat=="sdk_ios":
        return "SDK iOS"
    if oldCat=="sdk__android":
        return "SDK Android"
    if oldCat=="sdk_.net":
        return "SDK .NET"
    if oldCat=="sdk__java":
        return "SDK Java"        
    if oldCat=="sdk_synchronizer":
        return "SDK Synchronizer"
    if oldCat=="sdk_general_question":
        return "SDK General Question"                        
    if oldCat=="console_user_management":
        return "Console User Management"
    if oldCat=="console_user_interaction":
        return "Console User Interaction"        
    if oldCat=="console_permissions":
        return "Console Permissions"
    if oldCat=="console__metrics":
        return "Console Metrics"
    if oldCat=="console__console_segments":
        return "Console Console Segments"
    if oldCat=="console__splits":
        return "Console Splits"        
    if oldCat=="console_tagging":
        return "Console Targeting"    
    if oldCat=="console_onboarding":
        return "Console OnBoarding"                
    if oldCat=="results__recalculate_metrics":
        return "Recalculate Metrics"
    if oldCat=="results__data_request":
        return "Data Request"
    if oldCat=="results__metrics":
        return "Results Metrics"
    if oldCat=="results__traffic_cards":
        return "Results Traffic Cards"
    if oldCat=="results__interpretation":
        return "Results Interpretation"
    if oldCat=="targeting":
        return "Targeting"
    if oldCat=="targeting_editor":
        return "Targeting Editor"
    if oldCat=="integration_webhooks_impressions":
        return "Integration Webhooks Impressions"
    if oldCat=="integration_webhooks_slack":
        return "Integration Webhooks Slack"        
    if oldCat=="integration_segment_out":
        return "Integration Segment Out"
    if oldCat=="integration_segment_in":
        return "Integration Segment In"
    if oldCat=="integration__saml":
        return "SAML"
    if oldCat=="integration__mparticle":
        return "Integration mParticle"
    if oldCat=="integration_jira":
        return "Integration Jira"
    if oldCat=="integration_webhooks_changes":
        return "Integration Webhooks Changes"
    if oldCat=="integration_other":
        return "Integration Other"
    if oldCat=="integration__aws_s3_events":
        return "Integration AWS S3 Events"
    if oldCat=="integration_webhooks_email":
        return "Integration Webhooks Email"
    return oldCat


def GetChartCat(oldCat):
    if oldCat.find("api_")>-1 or oldCat.find("integration_")>-1  or oldCat.find("sso")>-1:  
        return "Integration and API"
    if oldCat.find("sdk_")>-1:
        return "SDK"
    if oldCat=="console_user_management" or oldCat=="console_onboarding"  or oldCat.find("login")>-1  or oldCat.find("user_man")>-1:
        return "User and Account Management"
    if oldCat=="console__metrics" or oldCat.find("results_")>-1:
        return "Experiment"
    if oldCat.find("console_")>-1 or oldCat.find("targeting")>-1 or oldCat=="infrastructure"  or oldCat.find("dynamic")>-1:
        return "Feature Flags"        
    if oldCat.find("other_")>-1:
        return "Other"        
    return ""


def FixTicketCat(oldCat):
    if oldCat=="user_error":
        return "User Error"
    if oldCat=="task_request":
        return "Task Request"
    if oldCat=="user_experience":
        return "User Experience"
    if oldCat=="bug":
        return "Bug"
    if oldCat=="guidance":
        return "General Guidance"
    if oldCat=="user_experience":
        return "User Experience"
    if oldCat=="feature_request":
        return "Feature Request"
    if oldCat=="fixed_bug":
        return "Fixed Bug"
    return oldCat

def FixTicketStatus(oldCat):
    if oldCat=="open":
        return "Open"
    if oldCat=="solved":
        return "Solved"
    if oldCat=="closed":
        return "Closed"
    if oldCat=="hold":
        return "On-hold"
    if oldCat=="pending":
        return "Pending"
    return oldCat

reload(sys)
#('utf8')
start_date = '2023-01-01'
end_date = datetime.date.today().strftime("%Y-%m-%d")
def get_ticketdata():
    results=[]
    for ticket in tqdm(zenObj.getAllTickets(start_date, end_date)):
        # Process the ticket
    #for ticket in zenObj.getAllTickets( '2022-08-25', '2022-09-02'):
    #for ticket in zenObj.getAllTicketsWithCustomValue('BASIC', '2020-03-06'):
    #for ticket in zenObj.GetRequesterTickets("bilal.al-shahwany@split.io", '2020-03-06'):
#        print("Ticket: ", str(ticket.id)+", "+str(ticket.created))
        print(ticket.subject)
        orgName=""
        if not ticket.organization is None:
            orgName=ticket.organization.name
        else:
            orgName=ticket.requester.email[ticket.requester.email.find("@")+1:]    
        
        CSM=""
        if not ticket.custom_fields[3]["value"] is None:
            CSM=ticket.custom_fields[3]["value"]

        productCat=""
        if not ticket.custom_fields[2]["value"] is None:
            productCat=FixProdCat(ticket.custom_fields[2]["value"])
        #    productCat=ticket.custom_fields[2]["value"]
        chartCat = GetChartCat(productCat)
        ticketCat=""
        if not ticket.custom_fields[1]["value"] is None:
            ticketCat=FixTicketCat(ticket.custom_fields[1]["value"])
        ticketStatus=FixTicketStatus(ticket.status)

        customerType=""
        if not ticket.custom_fields[6]["value"] is None:
            customerType=ticket.custom_fields[6]["value"]

        customerPaidStatus=""
        if not ticket.custom_fields[4]["value"] is None:
            customerType=ticket.custom_fields[4]["value"]
        
        userExperience=""
        userExperience_value = None  # Initialize user_experience to None in case it's not found
        for field in ticket.custom_fields:
            if field.get("value") == "user_experience":
                userExperience_value = field.get("value")
                break
        
        # Check if user_experience was found and then pass it to FixTicketCat
        if userExperience_value is not None:
            userExperience = FixTicketCat(userExperience_value)
        
    #    followers=""
    #    if len(ticket.follower_ids)>0:
    #        for ids in ticket.follower_ids:
    #            followers=followers+","+str(zenObj.GetUserEmail(ids))
    #    orgName2 = orgName if orgName != "Split" else None
        #results.append(['"'+str(orgName)+'"','"'+productCat+'"','"'+chartCat+'"','"'+str(ticket.subject.replace(chr(13)," "))+'"','"'+str(ticket.created)+'"',"",'"'+str(ticket.updated)+'"','"'+ticketStatus+'"','"'+str(ticket.id)+'"','"'+ticketCat+'"','"'+customerType+'"'])
    #    results.append(['"'+str(orgName)+'"','"'+productCat+'"','"'+followers+'"','"'+str(ticket.subject)+'"','"'+str(ticket.created)+'"',"",'"'+str(ticket.updated)+'"','"'+ticketStatus+'"','"'+str(ticket.id)+'"','"'+ticketCat+'"'])
    #    if orgName2 is not None:
    #        results.append(['"'+str(orgName)+'"','"'+CSM+'"','"'+customerType+'"','"'+customerPaidStatus+'"','"'+userExperience+'"'])

    # Only add tickets with "user_experience" to results
        
        followers = ""
        if len(ticket.follower_ids) > 0:
            for ids in ticket.follower_ids:
                followers = followers + "," + str(zenObj.GetUserEmail(ids))
        orgName2 = orgName if orgName != "Split" else None
        if userExperience_value == "user_experience" and orgName2 is not None:
            results.append(['"' + str(ticket.id) + '"', '"' + CSM + '"', '"' + customerType + '"', '"' + customerPaidStatus + '"', '"' + userExperience + '"', '"' + productCat + '"', '"' + ticket.subject + '"'])

    # Export only tickets with "user_experience" to CSV
    ExportToCSV(results, 7, "User_experience_tickets.csv", "Ticket Number,CSM, customer_paidstatus, customer_type, user_experience, product_category, Subject\n")


def get_orgs_data():
    results=[]
    orgs = zenObj.getAllOrgFields()
    for org in tqdm(orgs):
        orgName = org.name if org.name is not None else org.id
        org_fields = org.organization_fields

        results.append([
            f'"{orgName}"',
            f'"{org_fields.get("csm", "")}"',
            f'"{org_fields.get("organization_id", "")}"',
            f'"{org_fields.get("package", "")}"',
            f'"{org_fields.get("sfdc_plan_status", "")}"',
            f'"{org_fields.get("sfdc_plan_type", "")}"',
            f'"{org_fields.get("sfdc_support_plan_type", "")}"',
        ])

    header = "org_name,csm,organization_id,package,sfdc_plan_status,sfdc_plan_type,sfdc_support_plan_type\n"
    ExportToCSV(results, 6, "orgs_data.csv", header)

if __name__ == '__main__':
    get_orgs_data()
    #get_ticketdata()