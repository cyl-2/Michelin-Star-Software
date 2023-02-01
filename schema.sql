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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO staff
  ( role, first_name, last_name, password)
VALUES
  ( 'waiter', 'Ben', '', ''),
  ( 'waiter', 'Tommy', '', ''),
  ( 'waiter', 'Emma', '', ''),
  ( 'waiter', 'Cherry', '', ''),
  ( 'manager', 'Aodh', '', '');
  

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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
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
);

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
    dishType TEXT NOT NULL,
    allergies TEXT
);

INSERT INTO dish
  ( name, cost, cook_time, allergies, dishType )
VALUES
  ('Burger and chips', 20, 30, '', 'main'),
  ('Chicken and chips', 15, 20, '', 'main'),
  ('Fish and chips', 25, 20, '', 'main'),
  ('Tomato soup', 20, 30, '', 'starter'),
  ('Chicken Salad', 15, 20, '', 'starter'),
  ('Ice Cream', 20, 30, '', 'dessert'),
  ('Chocolate Brownie', 15, 20, '', 'dessert');

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
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    time INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    status TEXT
);


DROP TABLE IF EXISTS tables;

CREATE TABLE tables
(   
    table_id INTEGER PRIMARY KEY AUTO_INCREMENT,
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
    date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS roster_requests;

CREATE TABLE roster_requests
(
    request_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    employee TEXT NOT NULL,
    message TEXT,
    response TEXT,
    date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(20) default 'Pending',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS user_analytics;

CREATE TABLE user_analytics
(
    todays_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    daily_users INTEGER,
    new_daily_users INTEGER
);

DROP TABLE IF EXISTS sales_analytics;
CREATE TABLE sales_analytics
(
	the_month TEXT NOT NULL,
    daily_sales DECIMAL,
    monthly_sales DECIMAL,
    yearly_sales DECIMAL
);


############
TRIGGER TO UPDATE STATUS AFTER UPDATING QUANTITY IN INGREDIENT TABLE

CREATE DEFINER=`root`@`localhost` TRIGGER `ingredient_BEFORE_UPDATE` BEFORE UPDATE ON `ingredient` FOR EACH ROW BEGIN
	IF NEW.quantity <= 10 THEN
        SET NEW.status = 'RED';
    END IF;
    IF NEW.quantity >= 11 THEN
        SET NEW.status = 'AMBER';
    END IF;
    IF NEW.quantity >= 50 THEN
        SET NEW.status = 'GREEN';
    END IF;
END

############
CLEARS CODE AFTER 10 SECONDS OF INSERTING

CREATE EVENT clear_code
ON SCHEDULE
EVERY 5 SECOND
STARTS (CURRENT_TIMESTAMP + INTERVAL 10 SECOND)
DO 
UPDATE staff
SET code = null WHERE TIMESTAMPDIFF(SECOND, last_updated, NOW()) >= 10 ;