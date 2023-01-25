DROP TABLE IF EXISTS staff;

CREATE TABLE staff 
(
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS roster;

CREATE TABLE roster 
(
    staff_id INTEGER PRIMARY KEY,
    mon TEXT,
    tue TEXT,
    wed TEXT,
    thu TEXT,
    fri TEXT,
    sat TEXT,
    sun TEXT
);

DROP TABLE IF EXISTS ingredient;

CREATE TABLE ingredient
(   
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);



DROP TABLE IF EXISTS dish;

CREATE TABLE dish
(   
    dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cost INTEGER NOT NULL,
    cook_time Integer NOT NULL,
    allergies TEXT
);



DROP TABLE IF EXISTS dish_ingredient;

CREATE TABLE dish_ingredient
(   
    ingredient_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);
INSERT INTO dish
  ( name, cost, cook_time, allergies )
VALUES
  ('Burger and chips', 20, 30, ''),
  ('Chicken and chips', 15, 20, ''),
  ('Fish and chips', 25, 20, '');

INSERT INTO ingredient
  ( name, quantity )
VALUES
  ('Patty', 40),
  ('Chips', 150),
  ('Chicken', 40),
  ('Fish', 0), 
  ('Buns', 70);

SELECT MIN(quantity) FROM ingredient WHERE ingredient_id IN (1,2,5);

INSERT INTO dish_ingredient
VALUES
  ( 1, 1),
  ( 2, 1),
  ( 2, 2),
  ( 3, 2),
  ( 4, 3),
  ( 5, 1);

DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    time INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);

DROP TABLE IF EXISTS tables;

CREATE TABLE tables
(   
    table_id INTEGER PRIMARY KEY,
    seats INTEGER NOT NULL,
    x TEXT NOT NULL,
    y TEXT NOT NULL
);

INSERT INTO tables
  ( table_id, seats, x, y )
VALUES
  (1, 4, "100px", "100px"), 
  (2, 4, "200px", "200px"), 
  (3, 4, "300px", "300px"),
  (4, 4, "400px", "400px");
SELECT * FROM dish;
SELECT * FROM tables;

DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings
(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    time INTEGER NOT NULL
);


DROP TABLE IF EXISTS stats;

CREATE TABLE stats
(
    staff_id INTEGER,
    turnover INTEGER,
    meal_cost INTEGER NOT NULL,
    tip INTEGER NOT NULL,
    tables INTEGER NOT NULL
);