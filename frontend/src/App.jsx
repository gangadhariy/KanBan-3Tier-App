import React, { useEffect, useState } from "react";
import axios from "axios";
import Column from "./components/Column";
import TaskForm from "./components/TaskForm";
import "./App.css";

const API = "/api";

function App() {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    try {
      const res = await axios.get(`${API}/tasks`);
      setTasks(res.data.items || res.data || []);
    } catch (err) {
      console.error("Error fetching tasks:", err);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const addTask = async (task) => {
    try {
      await axios.post(`${API}/tasks`, task);
      fetchTasks();
    } catch (err) {
      console.error("Error adding task:", err);
    }
  };

  const moveTask = async (id, status) => {
    try {
      await axios.put(`${API}/tasks/${id}/move`, { status });
      fetchTasks();
    } catch (err) {
      console.error("Error moving task:", err);
    }
  };

  const deleteTask = async (id) => {
    try {
      await axios.delete(`${API}/tasks/${id}`);
      fetchTasks();
    } catch (err) {
      console.error("Error deleting task:", err);
    }
  };

  const todo = tasks.filter((t) => t.status === "todo");
  const inProgress = tasks.filter((t) => t.status === "in_progress");
  const done = tasks.filter((t) => t.status === "done");

  return (
    <div className="app">
      <h1>🚀 Mini Kanban App v4</h1>

      <TaskForm onAdd={addTask} />

      <div className="board">
        <Column title="Todo" tasks={todo} onMove={moveTask} onDelete={deleteTask} />
        <Column title="In Progress" tasks={inProgress} onMove={moveTask} onDelete={deleteTask} />
        <Column title="Done" tasks={done} onMove={moveTask} onDelete={deleteTask} />
      </div>
    </div>
  );
}

export default App;
