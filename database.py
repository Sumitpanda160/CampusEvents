
import os
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "college_events")
    )


if __name__ == "__main__":
    try:
        connection = get_db_connection()

        if connection.is_connected():
            print("Database Connected Successfully!")

        connection.close()

    except mysql.connector.Error as error:
        print("Database Connection Failed:", error)
