CREATE TABLE users(
 id SERIAL PRIMARY KEY,
 username TEXT UNIQUE,
 password TEXT,
 role TEXT
);

CREATE TABLE sales(
 id SERIAL PRIMARY KEY,
 user_id INT,
 total NUMERIC,
 discount NUMERIC DEFAULT 0,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE returns(
 id SERIAL PRIMARY KEY,
 sale_id INT,
 amount NUMERIC,
 user_id INT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expenses(
 id SERIAL PRIMARY KEY,
 type TEXT,
 amount NUMERIC,
 user_id INT,
 note TEXT,
 created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inventory(
 id SERIAL PRIMARY KEY,
 expected INT,
 actual INT,
 loss INT,
 created_at TIMESTAMP DEFAULT NOW()
);
