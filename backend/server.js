require("dotenv").config();
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const db = require("./db");
const auth = require("./auth");
const receipt = require("./receipt");

const app = express();
app.use(cors());
app.use(express.json());

/* LOGIN */
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const u = (await db.query(
    "SELECT * FROM users WHERE username=$1",[username]
  )).rows[0];
  if (!u || !(await bcrypt.compare(password, u.password)))
    return res.status(400).json({ error: "Xato" });

  const token = jwt.sign(
    { id: u.id, role: u.role },
    process.env.JWT_SECRET
  );
  res.json({ token, role: u.role });
});

/* SOTUV */
app.post("/sales", auth(["admin","seller"]), async (req,res)=>{
  const { total, discount=0 } = req.body;
  const s = (await db.query(
    "INSERT INTO sales(user_id,total,discount) VALUES($1,$2,$3) RETURNING id",
    [req.user.id,total,discount]
  )).rows[0];

  const pdf = await receipt({
    id:s.id, total, discount, user:req.user.role
  });

  res.json({ saleId:s.id, receipt:pdf });
});

/* VAZVRAT */
app.post("/returns", auth(["admin","seller"]), async (req,res)=>{
  const { sale_id, amount } = req.body;
  await db.query(
    "INSERT INTO returns(sale_id,amount,user_id) VALUES($1,$2,$3)",
    [sale_id,amount,req.user.id]
  );
  res.sendStatus(201);
});

/* XARAJAT */
app.post("/expenses", auth(["admin","seller"]), async (req,res)=>{
  const { type, amount, note } = req.body;
  if (type==="bayram" && req.user.role!=="admin")
    return res.sendStatus(403);

  await db.query(
    "INSERT INTO expenses(type,amount,user_id,note) VALUES($1,$2,$3,$4)",
    [type,amount,req.user.id,note]
  );
  res.sendStatus(201);
});

/* TOVAR QABUL / YO‘QOTISH */
app.post("/inventory", auth(["admin"]), async (req,res)=>{
  const { expected, actual } = req.body;
  const loss = expected - actual;
  await db.query(
    "INSERT INTO inventory(expected,actual,loss) VALUES($1,$2,$3)",
    [expected,actual,loss]
  );
  res.json({ loss });
});

/* HISOBOT */
app.get("/reports", auth(["admin"]), async (_,res)=>{
  const sales = (await db.query("SELECT SUM(total) s FROM sales")).rows[0].s||0;
  const returns = (await db.query("SELECT SUM(amount) r FROM returns")).rows[0].r||0;
  const expenses = (await db.query("SELECT SUM(amount) e FROM expenses")).rows[0].e||0;
  const losses = (await db.query("SELECT SUM(loss) l FROM inventory")).rows[0].l||0;

  res.json({
    sales, returns, expenses, losses,
    profit: sales - returns - expenses - losses
  });
});

app.listen(process.env.PORT||3000);
