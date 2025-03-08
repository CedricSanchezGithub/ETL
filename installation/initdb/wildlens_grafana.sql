CREATE DATABASE  IF NOT EXISTS `wildlens` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE DATABASE  IF NOT EXISTS `grafana_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

GRANT ALL PRIVILEGES ON grafana_db.* TO 'grafana'@'%';
FLUSH PRIVILEGES;

USE `wildlens`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: wildlens
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `wildlens_etat`
--

DROP TABLE IF EXISTS `wildlens_etat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wildlens_etat` (
  `id_etat` bigint unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(255) NOT NULL,
  PRIMARY KEY (`id_etat`),
  UNIQUE KEY `id_zone` (`id_etat`),
  UNIQUE KEY `type_UNIQUE` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wildlens_etat`
--

LOCK TABLES `wildlens_etat` WRITE;
/*!40000 ALTER TABLE `wildlens_etat` DISABLE KEYS */;
/*!40000 ALTER TABLE `wildlens_etat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wildlens_facts`
--

DROP TABLE IF EXISTS `wildlens_facts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wildlens_facts` (
  `id_espece` bigint unsigned NOT NULL AUTO_INCREMENT,
  `famille` varchar(255) NOT NULL,
  `nom_latin` varchar(255) NOT NULL,
  `nom_fr` varchar(255) DEFAULT NULL,
  `nom_en` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `population_estimee` double NOT NULL,
  `localisation` varchar(255) NOT NULL,
  `nombre_image` int NOT NULL,
  `coeff_multiplication` int NOT NULL,
  PRIMARY KEY (`id_espece`),
  UNIQUE KEY `id_fact` (`id_espece`),
  KEY `idx_wildlens_facts_image` (`famille`),
  KEY `idx_wildlens_facts_zone` (`nom_latin`),
  KEY `idx_wildlens_facts_espece` (`description`),
  KEY `idx_wildlens_facts_timestamp` (`population_estimee`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wildlens_facts`
--

LOCK TABLES `wildlens_facts` WRITE;
/*!40000 ALTER TABLE `wildlens_facts` DISABLE KEYS */;
/*!40000 ALTER TABLE `wildlens_facts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wildlens_images`
--

DROP TABLE IF EXISTS `wildlens_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wildlens_images` (
  `id_image` bigint unsigned NOT NULL AUTO_INCREMENT,
  `image` varchar(255) NOT NULL,
  `id_espece` bigint unsigned NOT NULL,
  `id_etat` bigint unsigned NOT NULL,
  PRIMARY KEY (`id_image`),
  UNIQUE KEY `id_image` (`id_image`) /*!80000 INVISIBLE */,
  KEY `id_fact_idx` (`id_espece`),
  KEY `id_etat_idx` (`id_etat`),
  CONSTRAINT `id_espece` FOREIGN KEY (`id_espece`) REFERENCES `wildlens_facts` (`id_espece`),
  CONSTRAINT `id_etat` FOREIGN KEY (`id_etat`) REFERENCES `wildlens_etat` (`id_etat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wildlens_images`
--

LOCK TABLES `wildlens_images` WRITE;
/*!40000 ALTER TABLE `wildlens_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `wildlens_images` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-01 13:08:46
