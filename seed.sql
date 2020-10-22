DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE,
  password VARCHAR(255)
);

CREATE TABLE positions (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(5),
  user_id INT REFERENCES users(id)
);
