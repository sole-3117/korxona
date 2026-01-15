const jwt = require("jsonwebtoken");

module.exports = (roles = []) => (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.sendStatus(401);

  try {
    const user = jwt.verify(token, process.env.JWT_SECRET);
    if (roles.length && !roles.includes(user.role))
      return res.sendStatus(403);
    req.user = user;
    next();
  } catch {
    res.sendStatus(401);
  }
};
