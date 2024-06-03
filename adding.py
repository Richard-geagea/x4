import sqlite3
import pandas as pd

def insert_users_from_csv(csv_file, database_file, table_name):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(database_file)
    
    # Iterate over the rows in the DataFrame and insert them into the specified table
    for index, row in df.iterrows():
        query = f"INSERT INTO {table_name} (user_id, username, password, date_of_birth) VALUES (?, ?, ?, ?)"
        values = tuple(row)
        try:
            conn.execute(query, values)
            conn.commit()
            print(f"Inserted user: {values}")
        except sqlite3.IntegrityError:
            print(f"Skipping duplicate user: {values[0]}")
    
    # Close the database connection
    conn.close()

# Example usage:
insert_users_from_csv('user_data.csv', 'user_database.db', 'Users')
