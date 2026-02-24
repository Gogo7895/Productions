import express from "express";
import { db } from "../db.js";
import { auth } from "../auth.js";

const router = express.Router();


router.get("/", auth, async (req, res) => {
    const [todos] = await db.query("SELECT * FROM todo");
    res.json(todos);
});



router.get("/:id", auth, async (req, res) => {
    const [todos] = await db.query("SELECT * FROM todo WHERE id = ?", [req.params.id]);
    if (todos.length === 0) {
        return res.status(404).json({ msg: "Tâche non trouvée" });
    }
    res.json(todos[0]);
});



router.post("/", auth, async (req, res) => {
    const { title, description, due_time, status } = req.body;
    if (!title || !description || !due_time) {
        return res.status(400).json({ msg: "Titre, description et date requis" });
    }
    const [result] = await db.query(
        "INSERT INTO todo (title, description, due_time, user_id, status) VALUES (?, ?, ?, ?, ?)",
        [title, description, due_time, req.user.id, status || "todo"]
    );
    const [newTodo] = await db.query("SELECT * FROM todo WHERE id = ?", [result.insertId]);
    res.json(newTodo[0]);
});



router.put("/:id", auth, async (req, res) => {
    const { title, description, due_time, status } = req.body;
    const [oldTodo] = await db.query("SELECT * FROM todo WHERE id = ?", [req.params.id]);
    if (oldTodo.length === 0) {
        return res.status(404).json({ msg: "Tâche non trouvée" });
    }
    const newTitle = title || oldTodo[0].title;
    const newDescription = description || oldTodo[0].description;
    const newDueTime = due_time || oldTodo[0].due_time;
    const newStatus = status || oldTodo[0].status;
    await db.query(
        "UPDATE todo SET title=?, description=?, due_time=?, status=? WHERE id=?",
        [newTitle, newDescription, newDueTime, newStatus, req.params.id]
    );
    const [updatedTodo] = await db.query("SELECT * FROM todo WHERE id = ?", [req.params.id]);
    res.json(updatedTodo[0]);
});



router.delete("/:id", auth, async (req, res) => {
    await db.query("DELETE FROM todo WHERE id = ?", [req.params.id]);
    res.json({ msg: "Tâche supprimée" });
});

export default router;