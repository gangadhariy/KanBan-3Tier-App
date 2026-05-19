import React, { useState } from "react";

function TaskForm({ onAdd }) {
  const [title, setTitle] = useState("");

  const submit = () => {
    if (!title) return;
    onAdd({ title });
    setTitle("");
  };

  return (
    <div className="form">
      <input
        placeholder="New task..."
        value={title}
        onChange={e => setTitle(e.target.value)}
      />
      <button onClick={submit}>Add</button>
    </div>
  );
}

export default TaskForm;