import React from "react";

function TaskCard({ task, onMove, onDelete }) {
  return (
    <div className="card">
      <h4>{task.title}</h4>
      <p>{task.description}</p>

      <div className="actions">
        {task.status === "todo" && (
          <button onClick={() => onMove(task.id, "in_progress")}>➡</button>
        )}

        {task.status === "in_progress" && (
          <>
            <button onClick={() => onMove(task.id, "todo")}>⬅</button>
            <button onClick={() => onMove(task.id, "done")}>➡</button>
          </>
        )}

        {task.status === "done" && (
          <button onClick={() => onMove(task.id, "in_progress")}>⬅</button>
        )}

        <button onClick={() => onDelete(task.id)}>❌</button>
      </div>
    </div>
  );
}

export default TaskCard;