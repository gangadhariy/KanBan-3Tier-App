import os
import psycopg2
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 🔗 DB connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=5432,
    database="postgres",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)

# 🔥 Create table if not exists
def init_db():
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'todo'
    );
    """)
    conn.commit()

init_db()


# ✅ Health
@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ Get all tasks
@app.get("/tasks")
def get_tasks():
    cur = conn.cursor()
    cur.execute("SELECT id, title, status FROM tasks;")
    rows = cur.fetchall()

    return [
        {"id": r[0], "title": r[1], "status": r[2]}
        for r in rows
    ]


# ✅ Create task
@app.post("/tasks")
def create_task(task: dict):
    title = task.get("title")

    if not title:
        raise HTTPException(400, "Title required")

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, status) VALUES (%s, 'todo') RETURNING id;",
        (title,)
    )
    new_id = cur.fetchone()[0]
    conn.commit()

    return {"id": new_id, "title": title, "status": "todo"}


# ✅ Move task
@app.put("/tasks/{task_id}/move")
def move_task(task_id: int, body: dict):
    status = body.get("status")

    if status not in ["todo", "in_progress", "done"]:
        raise HTTPException(400, "Invalid status")

    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET status=%s WHERE id=%s RETURNING id;",
        (status, task_id)
    )

    if not cur.fetchone():
        raise HTTPException(404, "Task not found")

    conn.commit()
    return {"message": "updated"}


# ✅ Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s RETURNING id;", (task_id,))

    if not cur.fetchone():
        raise HTTPException(404, "Task not found")

    conn.commit()
    return {"message": "deleted"}