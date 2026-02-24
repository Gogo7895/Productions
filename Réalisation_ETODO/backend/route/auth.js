import express from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { db } from "../db.js";

const router = express.Router();

router.post("/register", async(req, res) => {
    const { email, password, name, firstname } = req.body;
    if (!email || !password || !name || !firstname) {
        return res.status(400).json({ msg: "Tous les champs sont requis" });
    }
    const [users] = await db.query("SELECT * FROM user WHERE email = ?", [email]);
    if (users.length > 0) {
        return res.status(409).json({ msg: "Cet email est déjà utilisé" });
    }
    const passwordCrypte = await bcrypt.hash(password, 10);
    const [result] = await db.query(
        "INSERT INTO user (email, password, name, firstname) VALUES (?, ?, ?, ?)", [email, passwordCrypte, name, firstname]
    );
    const token = jwt.sign({ id: result.insertId, email }, process.env.SECRET);
    res.json({ token });
});



router.post("/login", async(req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json({ msg: "Email et mot de passe requis" });
    }
    const [users] = await db.query("SELECT * FROM user WHERE email = ?", [email]);
    if (users.length === 0) {
        return res.status(401).json({ msg: "Email ou mot de passe incorrect" });
    }
    const user = users[0];
    const motDePasseOk = await bcrypt.compare(password, user.password);
    if (!motDePasseOk) {
        return res.status(401).json({ msg: "Email ou mot de passe incorrect" });
    }
    const token = jwt.sign({ id: user.id, email: user.email }, process.env.SECRET);
    res.json({ token });
});

export default router;