import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("tasks.db")
c = conn.cursor()

# Run the ALTER TABLE command to add the 'notified' column
c.execute("SELECT * FROM tasks ORDER BY due_date ASC")

return_tasks = c.fetchall()
# Commit the changes
conn.commit()

# Close the connection
conn.close()

print(return_tasks)
