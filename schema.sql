DROP TABLE IF EXISTS staff;

CREATE TABLE staff 
(
    staff_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    code TEXT,
    access_level TEXT NOT NULL,
    role TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    bio TEXT,
    address TEXT,
    password TEXT NOT NULL,
    last_updated TEXT NOT NULL
);

DROP TABLE IF EXISTS shift_requirements;

CREATE TABLE shift_requirements 
(
    day TEXT,
    opening_time INTEGER,
    closing_time INTEGER,
    min_workers INTEGER,
    unavailable TEXT
);

INSERT INTO shift_requirements
  ( day, opening_time, closing_time, min_workers, unavailable )
VALUES
  ('mon', 9, 5, 2, '[1]'),
  ('tue', 0, 24, 2, '[5]'),
  ('wed', 9, 5, 2, '[]'),
  ('thu', 9, 5, 2, '[]'),
  ('fri', 9, 5, 2, '[]'),
  ('sat', 9, 5, 2, '[]'),
  ('sun', 9, 5, 2, '[]');

DROP TABLE IF EXISTS customer;

CREATE TABLE customer
(
    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    code TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL,
    profile_pic varchar(45)
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

INSERT INTO roster
  ( staff_id, mon, tue, wed, thu, fri, sat, sun )
VALUES
  (1, '', '', '09:00-17:00', '09:00-17:00', '09:00-17:00', '09:00-17:00', '09:00-17:00'),
  (2, '09:00-17:00', '', '', '09:00-17:00', '09:00-17:00', '09:00-17:00', '09:00-17:00'),
  (3, '09:00-17:00', '09:00-17:00', '', '', '09:00-17:00', '09:00-17:00', '09:00-17:00'),
  (4, '09:00-17:00', '09:00-17:00', '09:00-17:00', '', '', '09:00-17:00', '09:00-17:00'),
  (5, '09:00-17:00', '09:00-17:00', '09:00-17:00', '09:00-17:00', '', '', '09:00-17:00');
  

DROP TABLE IF EXISTS ingredient;

CREATE TABLE ingredient
(   
    ingredient_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);/* supplier */

INSERT INTO ingredient
  ( name, quantity )
VALUES
  ('Patty', 40),
  ('Chips', 150),
  ('Chicken', 40),
  ('Fish', 0), 
  ('Buns', 70),
  ('Soup', 40),
  ('Ice cream', 40),
  ('Brownie', 40),
  ('Lettuce', 70);

DROP TABLE IF EXISTS dish;

CREATE TABLE dish
(   
    dish_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    cost INTEGER NOT NULL,
    cook_time Integer NOT NULL,
    dishType TEXT,
    dishPic TEXT,
    description TEXT,
    allergies TEXT
    
);

INSERT INTO dish
  ( name, cost, cook_time, dishType, dishPic, description, allergies )
VALUES
  ('Burger and chips', 20, 30, 'main', '1', 'burger and chips description', ''),
  ('Chicken and chips', 15, 20, 'main', '1', 'chicken and chips description', ''),
  ('Fish and chips', 25, 20, 'main', '1', 'fish and chips description', ''),
  ('Tomato soup', 20, 30, 'starter', '1', 'Soup description', ''),
  ('Chicken Salad', 15, 20, 'starter', '1', 'Chicken salad description', ''),
  ('Ice Cream', 20, 30, 'dessert', '1', 'Ice cream description', ''),
  ('Chocolate Brownie', 15, 20, 'dessert', '1', 'brownie description', '');

DROP TABLE IF EXISTS dish_ingredient;

CREATE TABLE dish_ingredient
(   
    ingredient_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);

INSERT INTO dish_ingredient
VALUES
  ( 1, 1),
  ( 2, 1),
  ( 2, 2),
  ( 3, 2),
  ( 4, 3),
  ( 5, 1),
  ( 6, 4),
  ( 3, 5),
  ( 9, 5),
  ( 7, 6),
  ( 8, 7);



DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    time INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    status TEXT, 
    info TEXT/* notes */
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

DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings
(
    booking_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    booker_id INTEGER,
    table_id INTEGER,
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

DROP TABLE IF EXISTS user_queries;

CREATE TABLE user_queries
(
    query_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    name TEXT NOT NULL,
    message TEXT NOT NULL,
    date DATE NOT NULL
);

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions
(
    username TEXT,
    dish_id INTEGER,
    cost INTEGER,
    quantity INTEGER,
    date TEXT
);

INSERT INTO transactions
  ( username, dish_id, cost, quantity, date )
VALUES
  ("benc190514@gmail.com", 1, 2, 1, null), 
  ("benc190514@gmail.com", 2, 2, 1, null), 
  ("benc190514@gmail.com", 3, 2, 1, null),
  ("benc190514il.com", 5, 2, 1, null);
  
  
  DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    username TEXT,
    comment TEXT,
    rating INTEGER,
    dish_id INTEGER
);

INSERT INTO reviews
  ( username, comment, rating, dish_id)
VALUES
  ("benc190514@gmail.com", "good", 5, 1), 
  ("benc190514@gmail.com", "bad", 2, 2), 
  ("benc190514@gmail.com", "okay", 4, 3),
  ("benc190514il.com", "AMAZING", 10, 5);
  
SELECT AVG(rating), dish_id FROM reviews GROUP BY dish_id;

CREATE TABLE modifications
(
	modifications_id INTEGER,
	dish_id INTEGER,
    changes TEXT,
    user TEXT
);