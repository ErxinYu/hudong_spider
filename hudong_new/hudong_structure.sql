-- MySQL dump 10.13  Distrib 8.0.15, for Linux (x86_64)
--
-- Host: localhost    Database: hudong_baike
-- ------------------------------------------------------
-- Server version	8.0.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `t_alias`
--

DROP TABLE IF EXISTS `t_alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_alias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alias_id` int(11) NOT NULL,
  `alias_name` varchar(255) NOT NULL,
  `entity_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pagered_red_idx` (`entity_id`),
  KEY `NewIndex1` (`alias_name`),
  KEY `alias_id` (`alias_id`)
) ENGINE=InnoDB AUTO_INCREMENT=220411 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_category`
--

DROP TABLE IF EXISTS `t_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_category` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(256) NOT NULL,
  `url` text NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`category_id`),
  KEY `page_id_fk_2` (`page_id`),
  KEY `NewIndex1` (`category_name`)
) ENGINE=MyISAM AUTO_INCREMENT=33136 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_category_rel`
--

DROP TABLE IF EXISTS `t_category_rel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_category_rel` (
  `target_id` int(11) NOT NULL,
  `rel_id` int(11) NOT NULL,
  `comment` int(3) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=126709 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_entity`
--

DROP TABLE IF EXISTS `t_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_entity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) unsigned NOT NULL,
  `entity_name` varchar(256) NOT NULL COMMENT 'page名称',
  `content` longtext COMMENT 'html内容',
  `links` text,
  `lastmodify` timestamp NULL DEFAULT NULL,
  `count_view` int(11) DEFAULT NULL,
  `count_modify` int(11) DEFAULT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `page_name_index` (`entity_name`(255)),
  KEY `page_id_fk1` (`page_id`),
  KEY `entity_id` (`entity_id`)
) ENGINE=MyISAM AUTO_INCREMENT=8394391 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_entity_category`
--

DROP TABLE IF EXISTS `t_entity_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_entity_category` (
  `entity_id` int(11) unsigned NOT NULL,
  `category_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `entity_id_fk_2` (`entity_id`),
  KEY `category_id_fk_1` (`category_id`)
) ENGINE=MyISAM AUTO_INCREMENT=9565493 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_entity_property`
--

DROP TABLE IF EXISTS `t_entity_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_entity_property` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) unsigned NOT NULL,
  `property_id` int(11) NOT NULL,
  `value` varchar(1024) DEFAULT NULL,
  `score` double(2,2) DEFAULT '0.00',
  `type` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pagecat_pageid_idx` (`property_id`),
  KEY `pagecat_catid_idx` (`value`(255)),
  KEY `entity_if_fk_3` (`entity_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7239016 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_page`
--

DROP TABLE IF EXISTS `t_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_page` (
  `page_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `url` text,
  `snapshot` longtext,
  `creator` text,
  `lastmodify` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `count_view` int(11) DEFAULT '1',
  `count_modify` int(11) DEFAULT '1',
  `page_type` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`page_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_property`
--

DROP TABLE IF EXISTS `t_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t_property` (
  `property_id` int(11) NOT NULL AUTO_INCREMENT,
  `property_name_raw` varchar(255) NOT NULL,
  `property_name_norm` varchar(255) NOT NULL,
  `property_type` int(3) NOT NULL DEFAULT '0' COMMENT '属性类别，标识人物属性，人物关系属性，武器属性等，默认0没有区分类别',
  PRIMARY KEY (`property_id`),
  KEY `att_attraw_idx` (`property_name_raw`)
) ENGINE=MyISAM AUTO_INCREMENT=649 DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-05-27 20:21:22
