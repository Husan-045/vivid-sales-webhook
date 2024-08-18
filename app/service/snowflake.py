from snowflake import connector

def snowflake_cursor(creds):
    snowflake_connection = connector.connect(**creds)
    return snowflake_connection.cursor()

def get_description(cursor):
    return [x.name.lower() for x in cursor.description]
