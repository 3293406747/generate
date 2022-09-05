/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80028
 Source Host           : localhost:3306
 Source Schema         : test_db

 Target Server Type    : MySQL
 Target Server Version : 80028
 File Encoding         : 65001

 Date: 05/09/2022 10:09:43
*/

-- 创建数据库test_db
DROP DATABASE IF EXISTS `test_db`;
CREATE DATABASE `test_db` CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
USE `test_db`;

-- 创建user数据表
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`(
  `id` int(0) AUTO_INCREMENT PRIMARY KEY,
  `username` varchar(22) NULL,
  `phone` varchar(11) NULL,
  `ssn` varchar(18) NULL,
  `address` varchar(255) NULL,
  `email` varchar(255) NULL,
  `job` varchar(255) NULL
);
