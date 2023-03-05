/* CLEARS 'FORGOT PASSWORD' FEATURE CONFIRMATION 
CODE AFTER 10 SECONDS OF INSERTING */

CREATE EVENT clear_code
ON SCHEDULE
EVERY 5 SECOND
STARTS (CURRENT_TIMESTAMP + INTERVAL 10 SECOND)
DO 
UPDATE staff
SET code = null WHERE TIMESTAMPDIFF(SECOND, last_updated, NOW()) >= 10 ;


/* customer -> AFTER INSERT TRIGGER for user_analytics "new_daily_users" */

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


/* TRIGGER FOR DAILY USERS customer AFTER UPDATE */

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


/* EVENT THAT WOULD CALCULATE THE YEARLY SALES ON 01/01 OF 
EVERY YEAR AND THEN INSERT THE VALUE INTO "yearly_revenue" */

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


/* EVENT THAT WOULD CALCULATE THE MONTHLY SALES ON 01/01 OF 
EVERY YEAR AND THEN INSERT THE VALUE INTO "monthly_revenue" */

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

/* TRIGGER TO UPDATE STATUS AFTER UPDATING QUANTITY IN INGREDIENT TABLE */

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