import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect("tasks.db")
c = conn.cursor()

# Run the ALTER TABLE command to add the 'notified' column
c.execute("SELECT * FROM tasks ORDER BY due_date ASC")
# c.execute("SELECT * FROM settings")
# c.execute("DROP TABLE IF EXISTS tasks")
# c.execute("ALTER TABLE tasks ADD COLUMN complete_date TIMESTAMP;")

return_tasks = c.fetchall()
# Commit the changes

for i in range(1, 101):
    task_name = f"Task {i}"  # Simple task names like Task 1, Task 2, etc.
    due_date = datetime.now() + timedelta(days=random.randint(1, 30))  # Random due date in the next 30 days
    status = random.choice(["open", "complete"])  # Random status
    notified = random.randint(0, 1)  # Random value for notified (0 or 1)
    snooze_counter = random.randint(0, 5)  # Random snooze counter value (0 to 5)

    c.execute(
        """
        INSERT INTO tasks (name, due_date, status, notified, snooze_counter)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_name, due_date, status, notified, snooze_counter),
    )

# Commit changes and close the connection

print("100 tasks inserted into the database.")

conn.commit()

# Close the connection
conn.close()

print(return_tasks)
