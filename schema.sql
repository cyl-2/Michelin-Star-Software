
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

INSERT INTO orders
  ( time, dish_id, table_id, notes, status )
VALUES
  ('22:31:55', 3, 5, "tomato-0", "unmade"),
  ('22:31:55', 5, 5, "", "unmade"),
  ('22:31:55', 1, 5, "", "unmade"),
  ('22:31:55', 7, 5, "", "unmade"),
  ('22:31:55', 3, 5, "", "unmade"),
  
  ('22:11:55', 4, 3, "Priority", "unmade"),
  ('22:11:55', 2, 3, "", "unmade"),
  ('22:11:55', 5, 3, "", "unmade"),
  
  ('22:52:56', 3, 5, "Priority", "unmade"),
  ('22:52:56', 4, 5, "", "unmade")
  ;

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

INSERT INTO bookings ( booker_id, table_id, name, date, time)
VALUES
(5, 5, 'Emma', '2023-03-07', 20);

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

INSERT INTO reviews
  ( username, comment, rating, dish_id, dish_name)
VALUES
  ("benc190514@gmail.com", "I really like the pepperoni", 5, 1, "Pizza"), 
  ("James", "Best cripsy base", 5, 1, "Pizza"),
  ("John", "Delish dish", 5, 1, "Pizza"),
  
  ("Kevin", "Love this", 4, 2, "Veg Soup"),
  ("Kevin", "Salty", 2, 2, "Veg Soup"),
  
  ("Will", "Dish was served to me cold...", 1, 3, "Beef Burger"), 
  ("Billy", "Great", 4, 3, "Beef Burger"),
  ("Sean", "", 3, 3, "Beef Burger"),
  
  ("Steve", "Portion was absolutely huge", 5, 4, "Roast Chicken"),
  ("Trevor", "Great family meal", 5, 4, "Roast Chicken"),
  ("Bob", "Would recommend", 5, 4, "Roast Chicken"),
  
  ("Bart", "Great insta pic", 4, 5, "Smoked Salmon"),
  ("Billy", "Too expensive", 4, 5, "Smoked Salmon"),
  
  ("Aaron", "cheap and cheerful", 4, 6, "Carbonara"),
  
  ("Megan", "not even free", 1, 7, "Bread Basket"),
  ("Sandra", "very fresh", 4, 7, "Bread Basket"),
  
  ("Samantha", "yum yum yum", 5, 8, "Share Platter Chicken Wings"),
  
  ("Samantha", "Too spicy", 5, 9, "Hot Share Platter Chicken Wings"),
  
  ("Rachel", "Nice", 4, 10, "Ceasar Salad"),
  ("Billy", "Very nice", 4, 3, "Selection of Ice Cream"),
  ("Billy", "Cupcake", 4, 3, "tastes like my mom's fr fr"),
  ("Billy", "Wow I just love oreo what a fantastic ", 4, 3, "Oreo Cheesecake"),
  
  ("benc190514il.com", "AMAZING", 5, 5,"");

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

################
customer -> AFTER INSERT TRIGGER for user_analytics "new_daily_users"

CREATE DEFINER=`root`@`localhost` TRIGGER `customer_AFTER_INSERT` AFTER INSERT ON `customer` FOR EACH ROW BEGIN
    -- check if there is already a row in user_analytics for today's date
    IF NOT EXISTS (SELECT new_daily_users FROM user_analytics WHERE DATE(todays_date) = CURDATE()) THEN
        -- insert a new row with new_daily_users = 1
        INSERT INTO user_analytics (new_daily_users) VALUES (1);
    ELSE
        -- update the existing row by incrementing new_daily_users by 1
        UPDATE user_analytics
        SET new_daily_users = new_daily_users + 1
        WHERE DATE(todays_date) = CURDATE();
    END IF;
END

########################
TRIGGER FOR DAILY USERS customer AFTER UPDATE

CREATE DEFINER=`root`@`localhost` TRIGGER `customer_AFTER_UPDATE` AFTER UPDATE ON `customer` FOR EACH ROW BEGIN

    IF DATE(OLD.last_updated) <> CURDATE() THEN
		IF NOT EXISTS (SELECT daily_users FROM user_analytics WHERE DATE(todays_date) = CURDATE()) THEN
			INSERT INTO user_analytics (daily_users) VALUES (1);
		ELSE
			UPDATE user_analytics
			SET daily_users = daily_users + 1
			WHERE DATE(todays_date) = CURDATE();
		END IF;
    END IF;
END

##########################
EVENT THAT WOULD CALCULATE THE YEARLY SALES ON 01/01 OF EVERY YEAR AND THEN INSERT THE VALUE INTO "yearly_revenue"

DELIMITER //
CREATE EVENT IF NOT EXISTS `yearly_revenue_calculation`
ON SCHEDULE EVERY 1 YEAR STARTS '2022-01-01 00:00:00'
DO
BEGIN
  SET @total_cost = (
    SELECT SUM(dish.cost)
    FROM orders
    INNER JOIN dish ON orders.dish_id = dish.dish_id
    WHERE YEAR(orders.time) = YEAR(CURDATE())
  );
  INSERT INTO yearly_revenue (the_year, yearly_sales)
  VALUES (YEAR(CURDATE()), @total_cost);
END//
DELIMITER ;

##########################
EVENT THAT WOULD CALCULATE THE MONTHLY SALES ON 01/01 OF EVERY YEAR AND THEN INSERT THE VALUE INTO "monthly_revenue"

DELIMITER //
CREATE EVENT IF NOT EXISTS `monthly_revenue_calculation`
ON SCHEDULE
EVERY 1 MONTH 
STARTS ('2022-01-01 00:00:00')
DO
BEGIN
SET @gross_profit = (
  SELECT SUM(dish.cost)
  FROM orders
  INNER JOIN dish ON orders.dish_id = dish.dish_id
  WHERE YEAR(orders.time) = YEAR(CURDATE()) AND MONTH(orders.time) = MONTH(CURDATE())
);
INSERT INTO monthly_revenue (the_month, monthly_sales)
VALUES (DATE_FORMAT(CURDATE(), '%Y-%m-01'), @gross_profit);
END//
DELIMITER ;
*/
