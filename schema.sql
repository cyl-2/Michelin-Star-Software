
DROP TABLE IF EXISTS notifications;

CREATE TABLE notifications
(
    notif_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    received TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

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

DROP TABLE IF EXISTS shift_requirements;

CREATE TABLE shift_requirements 
(
    day TEXT,
    opening_time INTEGER,
    closing_time INTEGER,
    min_workers INTEGER,
    unavailable TEXT
);

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
    supplier_email TEXT,
    status TEXT
);

DROP TABLE IF EXISTS stock;

CREATE TABLE stock
(   
    batch_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    ingredient_id INTEGER NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL
);

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

DROP TABLE IF EXISTS dish_ingredient;

CREATE TABLE dish_ingredient
(   
    ingredient_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL
);
  
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

DROP TABLE IF EXISTS yearly_revenue;
CREATE TABLE yearly_revenue
(
	the_year TEXT NOT NULL,
  yearly_sales FLOAT DEFAULT 0
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

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions
(
    username TEXT,
    dish_id INTEGER,
    cost INTEGER,
    quantity INTEGER,
    date TEXT
);

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    username TEXT,
    comment TEXT,
    rating INTEGER,
    dish_id INTEGER,
    dish_name TEXT
);

DROP TABLE IF EXISTS modifications;

CREATE TABLE modifications
(
	modifications_id INTEGER PRIMARY KEY auto_increment,
	dish_id INTEGER,
  changes TEXT,
  user TEXT
);
