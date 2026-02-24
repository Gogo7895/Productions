import express from "express";
import { auth } from "../auth.js";
import { db } from "../db.js";

const router = express.Router();

router.get("/", auth, async (req, res) => {
    const [users] = await db.query("SELECT id, email, firstname, name FROM user WHERE id = ?", [req.user.id]);
    if (users.length === 0) {
        return res.status(404).json({ msg: "Utilisateur non trouvé" });
    }
    res.json(users[0]);
});



router.get("/todos", auth, async (req, res) => {
    const [todos] = await db.query("SELECT * FROM todo WHERE user_id = ?", [req.user.id]);
    res.json(todos);
});

export default router;