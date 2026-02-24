import express from "express";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
  next();
});

import authRoutes from "./route/auth.js";
import userRoutes from "./route/user.js";
import todosRoutes from "./route/todos.js";

app.get("/", (req, res) => {
  res.json({ msg: "backend OK" });
});

app.use("/", authRoutes);
app.use("/user", userRoutes);
app.use("/todos", todosRoutes);

app.listen(process.env.PORT, () => {
  console.log("API running on port " + process.env.PORT);
});
