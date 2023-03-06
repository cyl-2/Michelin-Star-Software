
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
  ( "manager", "New Customer Enquiry","Enquiry regarding 'Opening hours'"),
  ( "some_staff_email", "Roster Request Approved!","Your manager has approved your request!"),
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

INSERT INTO staff
  ( email, first_name, last_name, access_level, role, bio, password)
VALUES
  ( 'benc190514@gmail.com', 'Ben', 'Cahill', 'ordinary staff', 'Waiter', 'Head Waiter', 'pass'),
  ('emma@gmail.com', 'Emma', 'Rainsford', 'managerial', 'Manager', 'Floor Manager', 'pass'),
  ('cherrylin20172027@gmail.com', 'Cherry', 'Lin', 'managerial', 'Manager', 'Operations Manager', 'pass'),
  ('aodh@gmail.com', 'Aodh', "O' Gallochoir", 'ordinary staff', 'Chef', 'Head Chef', 'pass'),
  ( 'derek_don53@gmail.com', 'Derek', 'Donelly', 'ordinary staff', 'Waiter', 'Barista', 'pass'),
  ( 'markupineL@gmail.com', 'John', 'Walsh', 'ordinary staff', 'Waiter', 'Bus Boy', 'pass'),
  ( 'boscobox@gmail.com', 'Joey', 'Evans', 'ordinary staff', 'Waiter', 'Sommelier ', 'pass'),
  ( 'rubricscube@gmail.com', 'Bart', 'Bart', 'ordinary staff', 'Waiter', 'Cleaner', 'pass'),
  ( 'mbmuskery987', 'Mick', 'Burke', 'ordinary staff', 'Waiter', "Owner's son...", 'pass'),
  ( 'ailsbury23@gmail.com', 'Terry', 'McSweeney', 'ordinary staff', 'Waiter', 'Security', 'pass');


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
  ('mon', 9, 17, 3, '[1]'),
  ('tue', 9, 17, 3, '[5]'),
  ('wed', 9, 17, 3, '[]'),
  ('thu', 9, 17, 3, '[]'),
  ('fri', 0, 24, 3, '[]'),
  ('sat', 9, 17, 3, '[]'),
  ('sun', 9, 17, 2, '[]');

DROP TABLE IF EXISTS customer;

CREATE TABLE customer
(
    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    code TEXT,
    access_level VARCHAR(255) DEFAULT "customer" NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    profile_pic varchar(45)
);

INSERT INTO customer
  ( email, first_name, last_name, password, profile_pic )
VALUES
  ('benc190514@gmail.com', 'Ben', 'Cahill', 'pass', 'emptycart.jpg'),
  ('greenfields@gmail.com', 'Sarah', 'Jane', 'pass', 'emptycart.jpg'),
  ('borthwick@gmail.com', 'Markus', 'Smith', 'pass', 'emptycart.jpg'),
  ('owenfarrel@gmail.com', 'Owen', 'Farrell', 'pass', 'emptycart.jpg');

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
  (1, '', '', '09:00-17:00', '09:00-17:00', '00:00-08:00', '09:00-17:00', '09:00-17:00'),
  (2, '09:00-17:00', '', '', '09:00-17:00', '08:00-16:00', '09:00-17:00', '09:00-17:00'),
  (3, '09:00-17:00', '09:00-17:00', '', '', '00:00-08:00', '09:00-17:00', '09:00-17:00'),
  (4, '09:00-17:00', '09:00-17:00', '09:00-17:00', '', '', '09:00-17:00', '09:00-17:00'),
  (5, '', '', '09:00-17:00', '09:00-17:00', '00:00-08:00', '09:00-17:00', '09:00-17:00'),
  (6, '09:00-17:00', '', '', '09:00-17:00', '08:00-16:00', '09:00-17:00', '09:00-17:00'),
  (7, '09:00-17:00', '09:00-17:00', '', '', '08:00-16:00', '09:00-17:00', '09:00-17:00'),
  (8, '09:00-17:00', '09:00-17:00', '', '', '16:00-24:00', '09:00-17:00', '09:00-17:00'),
  (9, '09:00-17:00', '', '09:00-17:00', '09:00-17:00', '16:00-24:00', '', '09:00-17:00').
  (10, '09:00-17:00', '09:00-17:00', '', '09:00-17:00', '16:00-24:00', '', '09:00-17:00');
  

DROP TABLE IF EXISTS ingredient;
CREATE TABLE ingredient
(   
    ingredient_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    supplier_email TEXT,
    status TEXT
);

INSERT INTO ingredient
  ( name, supplier_email, status )
VALUES
  ('Patty', '', 'amber'),
  ('Chips', '', 'green'),
  ('Chicken', '', 'green'),
  ('Fish', '', 'red'), 
  ('Buns', '', 'green'),
  ('Soup', '', 'amber'),
  ('Ice cream', '', 'amber'),
  ('Brownie', '', 'amber'),
  ('Water', '', 'amber');
  
INSERT INTO ingredient ( name, supplier_email, status )
VALUES
('Lettuce', "cherrylin20172027@gmail.com", 'green');

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
(1, DATE(DATE_ADD(CURDATE()), INTERVAL 30 DAY), 50),
(2, DATE_ADD(CURDATE(), INTERVAL 0 DAY),  100),
(3, DATE_ADD(CURDATE(), INTERVAL 15 DAY), 100),
(4, DATE_ADD(CURDATE(), INTERVAL 10 DAY),  10),
(5, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 100),
(6, DATE_ADD(CURDATE(), INTERVAL 15 DAY), 60),
(7, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 65),
(8, DATE_ADD(CURDATE(), INTERVAL 100 DAY), 75),
(9, DATE_ADD(CURDATE(), INTERVAL 20 DAY), 90);

DROP TABLE IF EXISTS dish;

CREATE TABLE dish
(   
    dish_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    cost FLOAT NOT NULL,
    cook_time Integer NOT NULL,
    dishType TEXT,
    dishPic TEXT,
    description TEXT,
    allergies TEXT,
    day INTEGER DEFAULT 10
);

INSERT INTO dish
  ( name, cost, cook_time, dishType, dishPic, description, allergies )
VALUES
  ('Burger and Chips', 20, 30, 'main', '1', 'burger and chips description', ''),
  ('Chicken and Chips', 15, 20, 'main', '1', 'chicken and chips description', ''),
  ('Fish and Chips', 25, 20, 'main', '1', 'fish and chips description', ''),
  ('Tomato Soup', 20, 30, 'starter', '1', 'Soup description', ''),
  ('Chicken Salad', 15, 20, 'starter', '1', 'Chicken salad description', ''),
  ('Ice Cream', 20, 30, 'dessert', '1', 'Ice cream description', ''),
  ('Chocolate Brownie', 15, 20, 'dessert', '1', 'brownie description', '');

INSERT INTO dish
  ( name, cost, cook_time, dishType, dishPic, description, allergies, day )
VALUES
  ('Mondays Beef', 50, 10, 'special', '1', 'beef description', '', 0),
  ('Tuedays Beef', 50, 10, 'special', '1', 'beef description', '', 1),
  ('Wednesdays Beef', 50, 10, 'special', '1', 'beef description', '', 2),
  ('Thursdays Beef', 50, 10, 'special', '1', 'beef description', '', 3),
  ('Fridays Beef', 50, 10, 'special', '1', 'beef description', '', 4),
  ('Saturdays Beef', 50, 10, 'special', '1', 'beef description', '', 5),
  ('Sundays Beef', 50, 10, 'special', '1', 'beef description', '', 6);
  
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
  ( 3, 2),
  ( 4, 3),
  ( 5, 1),
  ( 6, 4),
  ( 7, 6),
  ( 8, 7),
  ( 9, 5);
  
DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    time TEXT NOT NULL,
    dish_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    notes TEXT,
    status TEXT
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
  (1, 4, "300px", "300px"), 
  (2, 4, "450px", "300px"), 
  (3, 4, "300px", "450px"),
  (4, 4, "450px", "450px"),
  (5, 4, "600px", "300px"),
  (6, 4, "600px", "450px");

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

INSERT INTO bookings ( booker_id, table_id, name, date, time)
VALUES
(5, 1, 'Emma', '2023-03-07', 19),
(5, 1, 'Emma', '2023-04-16', 17);

DROP TABLE IF EXISTS roster_requests;

CREATE TABLE roster_requests
(
    request_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    employee_email TEXT NOT NULL,
    employee_name TEXT NOT NULL,
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
    daily_users INTEGER DEFAULT 0,
    new_daily_users INTEGER DEFAULT 0
);


DROP TABLE IF EXISTS monthly_revenue;
CREATE TABLE monthly_revenue
(
	the_month TEXT NOT NULL,
  monthly_sales FLOAT DEFAULT 0
);

INSERT INTO monthly_revenue (the_month, monthly_sales)
VALUES
('2022-01-01', 5300),
('2022-02-01', 1000),
('2022-03-01', 5500),
('2022-04-01', 6040),
('2022-05-01', 7000),
('2022-06-01', 8000),
('2022-07-01', 8288),
('2022-08-01', 9929),
('2022-09-01', 10020),
('2022-10-01', 10520),
('2022-11-01', 11220),
('2022-12-01', 20020);

DROP TABLE IF EXISTS yearly_revenue;
CREATE TABLE yearly_revenue
(
	the_year TEXT NOT NULL,
  yearly_sales FLOAT DEFAULT 0
);

INSERT INTO yearly_revenue (the_year, yearly_sales)
VALUES
('2020-01-01', 213500),
('2021-01-01', 531350),
('2022-01-01', 554685),
('2023-01-01', 663000);


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
    dish_id INTEGER,
    dish_name TEXT
);

INSERT INTO reviews
  ( username, comment, rating, dish_id, dish_name)
VALUES
  ("benc190514@gmail.com", "good", 5, 1, ""), 
  ("benc190514@gmail.com", "bad", 2, 2, ""), 
  ("benc190514@gmail.com", "okay", 4, 3, ""),
  ("benc190514il.com", "AMAZING", 10, 5,"");

DROP TABLE IF EXISTS modifications;

CREATE TABLE modifications
(
	modifications_id INTEGER PRIMARY KEY auto_increment,
	dish_id INTEGER,
  changes TEXT,
  user TEXT
);