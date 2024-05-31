#####################################
# Zendesk-JIRA tool - Zendesk wrapper class
# Author: Bilal Al-Shahwany
# Date: 2018-09-14
#


from zenpy import Zenpy
import Log

class ZendeskObj:
    def __init__(self, userEmail, apiToken, subDomain):
        self.log = Log.Log("a")
        try:
            creds = {
                'email' : userEmail,
                'token' : apiToken,
               'subdomain': subDomain
            }
            self.zenpyClient = Zenpy(**creds)
        except Exception as e:
            self.log.Debug("Failed to Initialize Zendesk instance "+str(e))

    def getTicketComments(self, ticketId):
        return self.zenpyClient.tickets.comments(ticket=ticketId)

    def getTicketActivities(self, ticketId):
        return self.zenpyClient.activities(ticket=ticketId)

    def getAudit(self, ticketId):
        return self.zenpyClient.tickets.audits(ticket=ticketId)
        
    def getTicketFields(self, ticketId):        
        return self.zenpyClient.tickets(id=ticketId)
    
    def getOrgFields(self, orgId):        
        return self.zenpyClient.organizations(id=orgId)
    
    def getAllOrgFields(self):        
        return self.zenpyClient.organizations()
    
    def getTicketJIRALinks(self, ticketId):        
        return self.zenpyClient.jira_links(ticket_id=ticketId)
        
    def getAllTickets(self, createdAfter, createdBefore):
        return self.zenpyClient.search(type='ticket', created_after=createdAfter, created_before=createdBefore)        
    def getPostVotes(self, articleId):
        return self.zenpyClient.help_center.posts.votes(articleId)

    def getArticleVotes(self, articleId):
        return self.zenpyClient.help_center.articles.votes(articleId)
    
    def getAllArticles(self):
        return self.zenpyClient.help_center.articles()
    
    def getPRoductIdeas(self):
        return self.zenpyClient.help_center.topics.posts("115000296107")

    def getArticleComments(self, articleId):
        return self.zenpyClient.help_center.posts.comments(articleId)

    def getAllTicketsWithCustomValue(self, customValue, createdAfter):
        return self.zenpyClient.search(type='ticket', fieldvalue=customValue, created_after=createdAfter)        

    def getOrganization(self, customValue):
        return self.zenpyClient.search(type='organization', name=customValue)        

    def GetUserEmail(self, userId):
        return  self.zenpyClient.users._get_user(userId).email
    
    def GetRequesterTickets(self, requester, createdAfter):
        return self.zenpyClient.search(type='ticket', requester=requester, created_after=createdAfter)
                    
    def UpdateOrg(self, org):
        self.zenpyClient.organizations.update(org)
        