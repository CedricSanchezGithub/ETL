-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: Feb 07, 2025 at 09:30 AM
-- Server version: 8.0.33
-- PHP Version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wildlens`
--

-- --------------------------------------------------------

--
-- Table structure for table `wildlens_d1_images`
--
CREATE DATABASE IF NOT EXISTS wildlens;
CREATE DATABASE IF NOT EXISTS grafana_db;

-- Assurer que Grafana a accès à sa propre base
GRANT ALL PRIVILEGES ON grafana_db.* TO 'grafana'@'%';
FLUSH PRIVILEGES;



CREATE TABLE `wildlens_d1_images` (
  `id_image` bigint UNSIGNED NOT NULL,
  `url_image` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wildlens_d2_zone`
--

CREATE TABLE `wildlens_d2_zone` (
  `id_zone` bigint UNSIGNED NOT NULL,
  `nom_zone` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wildlens_d3_especes`
--

CREATE TABLE `wildlens_d3_especes` (
  `id_espece` bigint UNSIGNED NOT NULL,
  `nom` varchar(255) NOT NULL,
  `famille` varchar(255) NOT NULL,
  `nom_latin` varchar(255) NOT NULL,
  `description` text,
  `population_estimee` int DEFAULT NULL,
  `plus_grande_menace` text,
  `localisation` text,
  `slogan` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wildlens_facts`
--

CREATE TABLE `wildlens_facts` (
  `id_fact` bigint UNSIGNED NOT NULL,
  `id_image` int DEFAULT NULL,
  `id_zone` int DEFAULT NULL,
  `id_espece` int DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `latitude` decimal(9,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `wildlens_d1_images`
--
ALTER TABLE `wildlens_d1_images`
  ADD PRIMARY KEY (`id_image`),
  ADD UNIQUE KEY `id_image` (`id_image`);

--
-- Indexes for table `wildlens_d2_zone`
--
ALTER TABLE `wildlens_d2_zone`
  ADD PRIMARY KEY (`id_zone`),
  ADD UNIQUE KEY `id_zone` (`id_zone`);

--
-- Indexes for table `wildlens_d3_especes`
--
ALTER TABLE `wildlens_d3_especes`
  ADD PRIMARY KEY (`id_espece`),
  ADD UNIQUE KEY `id_espece` (`id_espece`);

--
-- Indexes for table `wildlens_facts`
--
ALTER TABLE `wildlens_facts`
  ADD PRIMARY KEY (`id_fact`),
  ADD UNIQUE KEY `id_fact` (`id_fact`),
  ADD KEY `idx_wildlens_facts_image` (`id_image`),
  ADD KEY `idx_wildlens_facts_zone` (`id_zone`),
  ADD KEY `idx_wildlens_facts_espece` (`id_espece`),
  ADD KEY `idx_wildlens_facts_timestamp` (`timestamp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `wildlens_d1_images`
--
ALTER TABLE `wildlens_d1_images`
  MODIFY `id_image` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `wildlens_d2_zone`
--
ALTER TABLE `wildlens_d2_zone`
  MODIFY `id_zone` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `wildlens_d3_especes`
--
ALTER TABLE `wildlens_d3_especes`
  MODIFY `id_espece` bigint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `wildlens_facts`
--
ALTER TABLE `wildlens_facts`
  MODIFY `id_fact` bigint UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
