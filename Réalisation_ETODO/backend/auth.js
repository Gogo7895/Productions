import jwt from "jsonwebtoken";
export function auth(req, res, next) {
    const header = req.headers.authorization;
    if (!header) {
        return res.status(401).json({ msg: "Token manquant" });
    }
    const token = header.split(" ")[1];
    if (!token) {
        return res.status(401).json({ msg: "Token manquant" });
    }
    try {
        const decoded = jwt.verify(token, process.env.SECRET);
        req.user = decoded;
        next(); 
    } catch (err) {
        return res.status(403).json({ msg: "Token invalide" });
    }
}