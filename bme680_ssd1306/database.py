import mysql.connector
import configparser


# setup config
config = configparser.ConfigParser()
config.read('config.ini')

host = config["production.server"].get("host")
user = config["production.server"].get("user")
password = config["production.server"].get("password")
db_name = config["production.server"].get("dbname")


def insert(sql, values, single=True):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    cursor = connection.cursor()

    if single:
        cursor.execute(sql, values)
    else:
        cursor.executemany(sql, values)

    connection.commit()

    connection.close()

