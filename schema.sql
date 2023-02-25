DROP TABLE IF EXISTS notifications;

CREATE TABLE notifications
(
    notif_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    received TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO notifications
  ( user, title, message)
VALUES
  ( 'cherrylin20172027@gmail.com', 'From Sara', 'super duper duper duper long long long long long long long long long long message 1'),
  ( 'cherrylin20172027@gmail.com', 'Inventory Management', 'message 2'),
  ( 'cherrylin20172027@gmail.com', 'Critical','message 3'),
  ( 'cherrylincyl@gmail.com', 'Roster Request','message 4');

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

/*INSERT INTO staff
  ( role, first_name, last_name, password)
VALUES
  ( 'waiter', 'Ben', '', ''),
  ( 'waiter', 'Tommy', '', ''),
  ( 'waiter', 'Emma', '', ''),
  ( 'waiter', 'Cherry', '', ''),
  ( 'manager', 'Aodh', '', '');
  */

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
    access_level TEXT DEFAULT "customer" NOT NULL,
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
    quantity INTEGER DEFAULT 0,
    supplier_email TEXT
);

INSERT INTO ingredient
  ( name )
VALUES
  ('Patty'),
  ('Chips'),
  ('Chicken'),
  ('Fish'), 
  ('Buns'),
  ('Soup'),
  ('Ice cream'),
  ('Brownie');
  
INSERT INTO ingredient ( name, supplier_email )
VALUES
('Lettuce', "cherrylin20172027@gmail.com");

DROP TABLE IF EXISTS stock;

CREATE TABLE stock
(   
    batch_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    ingredient_id INTEGER NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL
);

INSERT INTO stock
( ingredient_id, expiry_date, quantity)
VALUES
(1, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 10),
(2, DATE_ADD(CURDATE(), INTERVAL 0 DAY),  20);


/*CREATE DEFINER=`root`@`localhost` TRIGGER `lowerIngredients` AFTER INSERT ON `orders` FOR EACH ROW BEGIN
UPDATE stock
SET quantity=quantity-1
WHERE ingredient_id in (
                    SELECT i.ingredient_id
                    FROM orders as o
                    JOIN dish_ingredient as di
                    JOIN ingredient as i
                    JOIN dish as d
                    ON i.ingredient_id=di.ingredient_id AND di.dish_id=d.dish_id AND d.dish_id=o.dish_id
                    WHERE di.dish_id=NEW.dish_id)
END
*/
DROP TABLE IF EXISTS dish;

CREATE TABLE dish
(   
    dish_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    cost DECIMAL NOT NULL,
    cook_time INTEGER NOT NULL,
    dishType TEXT NOT NULL,
    allergies JSON DEFAULT NULL
);

INSERT INTO dish
  ( name, cost, description, cook_time, allergies, dishType )
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
    order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    time INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    notes TEXT,
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

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    username TEXT,
    name TEXT,
    comment TEXT,
    rating INTEGER,
    dish_name TEXT,
    dish_id INTEGER
);

/*
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

*/
