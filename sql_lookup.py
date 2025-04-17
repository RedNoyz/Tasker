import sqlite3

conn = sqlite3.connect("tasks.db")
c = conn.cursor()

c.execute("SELECT * FROM tasks ORDER BY due_date ASC")
# c.execute("SELECT * FROM settings")
# c.execute("DROP TABLE IF EXISTS tasks")
# c.execute("ALTER TABLE tasks ADD COLUMN complete_date TIMESTAMP;")

return_tasks = c.fetchall()


conn.commit()
conn.close()

print(return_tasks)

