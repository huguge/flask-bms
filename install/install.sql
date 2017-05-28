-- Make sure your mysql process is running first!

DROP DATABASE IF EXISTS `flaskbms_development`;
CREATE DATABASE IF NOT EXISTS `flaskbms_development`  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `flaskbms_development`;
SHOW create database flaskbms_development;


DROP DATABASE IF EXISTS `flaskbms_test`;
CREATE DATABASE IF NOT EXISTS `flaskbms_test`  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `flaskbms_test`;
SHOW create database flaskbms_test;


DROP DATABASE IF EXISTS `flaskbms_production`;
CREATE DATABASE IF NOT EXISTS `flaskbms_production`  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `flaskbms_production`;

-- Enable client program to communicate with the server using utf8 character set
SET NAMES 'utf8';

SHOW create database flaskbms_production;
