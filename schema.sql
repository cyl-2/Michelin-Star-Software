
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

INSERT INTO dish
  ( name, cost, cook_time, dishType, dishPic, description, allergies, day )
VALUES
  ('C', 50, 10, 'special', '1', 'beef description', '', 0),
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


INSERT INTO dish
  ( name, cost, cook_time, dishType, description, allergies, day)
VALUES
('Pizza', '13', '15', 'main', ' Italian origin consisting of a usually round, flat base of leavened wheat-based dough topped with tomatoes, cheese and other toppings', 'gluten', '10'),
('Veg Soup', '6', '3', 'starter', 'A hearty soup consisting of mainly vegetables and a base of vegetable broth topped with delicious croutons', 'gluten', '10'),
('Beef Burger', '10', '10', 'main', 'Classic Beef burger topped with lettuce, tomato, bacon and pickles', 'gluten', '10'),
('Roast chicken', '6', '3', 'main', 'Succulent roast chicken served with gravy, comes with a side of mixed veg and mashed potatoes', 'Non applicable', '10'),
('Smoked Salmon', '15', '16', 'main', 'Salmon fillet that has been cured and hot smoked topped with our secret sauce', 'soya', '10'),
('Carbonara', '13', '10', 'main', 'Carbonara is a Roman pasta dish made with eggs, hard cheese, cured pork and black pepper', 'Dairy', '10'),
('Bread Basket', '5', '2', 'starter', 'Selection of Bread served with a series of dips, cheese and olives', 'Cheese, Gluten', '10'),
('Share platter chicken Wings (mild)', '20', '13', 'starter', 'Platter of BBQed chicken wings covered in our mild seasoning served with ranch', 'Dairy', '10'),
('Hot share platter chicken Wings', '29', '13', 'starter', 'Platter of BBQed chicken wings covered in our homemade hot sauce, order if you dare!', 'Dairy', '10'),
('Caesar Salad', '13', '6', 'main', 'Green salad of romaine lettuce and croutons dressed with lemon juice, olive oil, egg, Worcestershire sauce, anchovies, garlic, Dijon mustard, Parmesan cheese, and black pepper', 'Dairy', '10'),
('Selction of Ice-cream', '6', '4', 'dessert', 'Selection of vanilla, chocolate and strawberry served with cream', 'Dairy', '10'),
('Cupcake', '4', '6', 'dessert', 'Classic sponge cupcake with buttercream icing', 'Dairy', '10'),
('Oreo Cheesecake', '6', '5', 'dessert', 'Delicious oreo cheesecake', 'Dairy', '10'),
('Chicken Tikka Masala','15','18','main','Chicken tikka masala is a dish consisting of roasted marinated chicken chunks in a spiced sauce. The sauce is usually creamy and orange-coloured','Dairy','0');






INSERT INTO ingredient
(name,supplier_email,status)
VALUES
('lettuce',"",""),
('tomato','',''),
('vanilla icecream','',''),
('chocolate icrecream','',''),
('strawberry icrecream','',''),
('salmon fillet','',''),
('potatoes','',''),
('spagetti','',''),
('bacon','',''),
('cheese','',''),
('pepperoni','',''),
('broccoli','',''),
('carrots','',''),
('oreo','',''),
('croutons','',''),
('Burger buns','',''),
('buttercream','',''),
('sprinkles','',''),
('chicken','',''),
('ranch','',''),
('whipped cream','','');


INSERT INTO dish_ingredient
(dish_id,ingredient_id)
VALUES
(1,2),
(1,11),
(1,10),
(2,15),
(3,16),
(3,9),
(3,1),
(3,2),
(4,7),
(4,13),
(4,12),
(4,1),
(5,6),
(6,8),
(6,9),
(8,20),
(9,20),
(10,20),
(10,1),
(10,2),
(10,15);
