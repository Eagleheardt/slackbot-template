###################################################################
#                                                                 #
#   This will create a file of all the user names and their IDs   #
#                                                                 #
###################################################################

def createUserFile(slack_client):

    members = slack_client.api_call('users.list')
    members = members['members']
    members = [m for m in members if not m['is_bot'] and not m['is_app_user']]

    slack_users = []

    print("Beginning Slack user retrieval")

    i = 0

    for member in members:
        SlackID = member['id']
        name = member['name']
        dm_channel = slack_client.api_call('im.open', user=SlackID)['channel']['id']

        slack_users.append([SlackID,name,dm_channel])
        i += 1
        print("Processed: {}/{}".format(i,len(members)))

    print("creating a file")

    userFile = open("allUsers.user","w")

    for userID, userName, dmChannel in slack_users:
        userName.replace("."," ")
        userName = userName.title()
        userID = userID.upper()


        userFile.write("{}|{}|{}\n".format(userName,userID,dmChannel))

    userFile.close()

    print('User file created!')