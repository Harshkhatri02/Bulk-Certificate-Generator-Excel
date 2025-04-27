-- Drop existing tables if they exist
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS subscription;
DROP TABLE IF EXISTS get_updates;
DROP TABLE IF EXISTS organisation;

-- Create organisation table
CREATE TABLE `organisation` (
    `oid` INT NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL,
    `institution` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `Iagree` TINYINT(1) NOT NULL,
    PRIMARY KEY (`oid`),
    UNIQUE INDEX (`email`)
);

-- Create get_updates table
CREATE TABLE `get_updates` (
    `uid` INT NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`uid`),
    INDEX (`email`)
);

-- Create subscription table
CREATE TABLE `subscription` (
    `sid` INT NOT NULL AUTO_INCREMENT,
    `samt` DECIMAL(10,2) NOT NULL,
    `s_time` TIMESTAMP NOT NULL,
    `s_type` VARCHAR(50) NOT NULL,
    `oid` INT NULL,
    PRIMARY KEY (`sid`),
    INDEX (`oid`),
    FOREIGN KEY (`oid`) REFERENCES `organisation` (`oid`)
);

-- Create payment table
CREATE TABLE `payment` (
    `pid` INT NOT NULL AUTO_INCREMENT,
    `pamt` DECIMAL(10,2) NOT NULL,
    `date` DATE NOT NULL,
    `time` TIME NOT NULL,
    `modeOfPayment` VARCHAR(50) NOT NULL,
    `sid` INT NULL,
    PRIMARY KEY (`pid`),
    INDEX (`sid`),
    FOREIGN KEY (`sid`) REFERENCES `subscription` (`sid`)
);

-- Create reviews table
CREATE TABLE `reviews` (
    `rid` INT NOT NULL AUTO_INCREMENT,
    `description` TEXT NOT NULL,
    `oid` INT NULL,
    PRIMARY KEY (`rid`),
    INDEX (`oid`),
    FOREIGN KEY (`oid`) REFERENCES `organisation` (`oid`)
); 