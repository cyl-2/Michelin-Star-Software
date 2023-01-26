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
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS customer;

CREATE TABLE customer
(
    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    code TEXT,
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
    ingredient_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);

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

DROP TABLE IF EXISTS dish_ingredient;

CREATE TABLE dish_ingredient
(   
    ingredient_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);

DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    time INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);

DROP TABLE IF EXISTS tables;

CREATE TABLE tables
(   
    table_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    seats INTEGER NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL
);

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
    employee TEXT NOT NULL,
    message TEXT,
    date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(20) default 'Pending'
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