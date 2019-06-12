import sqlite3

###################################################################
#                                                                 #
#   This will insert user names and slack IDs into a database     #
#                                                                 #
###################################################################

MAIN_CONNECTION = None

def EXEC(sqlCmd): # fetches data from the database
	try:
		someCursor = MAIN_CONNECTION.cursor()
		someCursor.execute(sqlCmd)
		someCursor.close()
		MAIN_CONNECTION.commit() 

		return 0

	except TypeError:
		return 7

	except ValueError:
		return 8

	except:
		return 9

def SIMPLE_INSERT(tableName, column, value):
	cmd = """
		INSERT INTO 
			{0} ({1})
		VALUES
			({2});
	""".format(tableName, column, value)

	return EXEC(cmd)

def addToDB(values):
    table = "Users"
    columns = "SlackID, DisplayName, DirectChannel"
    return SIMPLE_INSERT(table, columns, values)

def getInfo(slack_client):

    members = slack_client.api_call('users.list')
    members = members['members']
    members = [m for m in members if not m['is_bot'] and not m['is_app_user']]

    print("Beginning Slack user retrieval")

    for member in members:
        SlackID = member['id'].upper()
        name = member['name'].replace(".", " ").title()
        dm_channel = slack_client.api_call('im.open', user=SlackID)['channel']['id']

        insertString = "'{}', '{}', '{}'".format(SlackID, name, dm_channel)
        result = addToDB(insertString)
        if result != 0:
            print("INSERT ERROR!\n{}".format(insertString))
            break
        print("INSERTING: {}".format(insertString))

print("\n\nInsert complete")