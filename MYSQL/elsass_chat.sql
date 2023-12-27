-- MariaDB dump 10.19  Distrib 10.11.4-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: Elsass_Chat
-- ------------------------------------------------------
-- Server version	10.11.4-MariaDB-1~deb12u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Autorisations`
--

DROP TABLE IF EXISTS `Autorisations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Autorisations` (
  `compte` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  `niv_auto` int(11) DEFAULT 0,
  KEY `FKAC` (`compte`),
  KEY `FKAS` (`salon`),
  CONSTRAINT `FKAC` FOREIGN KEY (`compte`) REFERENCES `Comptes` (`id_compte`),
  CONSTRAINT `FKAS` FOREIGN KEY (`salon`) REFERENCES `Salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Comptes`
--

DROP TABLE IF EXISTS `Comptes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Comptes` (
  `id_compte` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(40) DEFAULT NULL,
  `mdp` varchar(40) DEFAULT NULL,
  `pseudo` varchar(40) DEFAULT NULL,
  `statut_co` varchar(10) DEFAULT 'offline',
  `salon` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_compte`),
  UNIQUE KEY `identifiant` (`login`),
  UNIQUE KEY `pseudo` (`pseudo`),
  KEY `FKCS` (`salon`),
  CONSTRAINT `FKCS` FOREIGN KEY (`salon`) REFERENCES `Salon` (`id_salon`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IP`
--

DROP TABLE IF EXISTS `IP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IP` (
  `id_IP` int(11) NOT NULL AUTO_INCREMENT,
  `compte` int(11) DEFAULT NULL,
  `IP` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id_IP`),
  KEY `FKIC` (`compte`),
  CONSTRAINT `FKIC` FOREIGN KEY (`compte`) REFERENCES `Comptes` (`id_compte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Messages`
--

DROP TABLE IF EXISTS `Messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Messages` (
  `id_message` int(11) NOT NULL AUTO_INCREMENT,
  `content` text DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `compte` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_message`),
  KEY `FKMC` (`compte`),
  KEY `FKMS` (`salon`),
  CONSTRAINT `FKMC` FOREIGN KEY (`compte`) REFERENCES `Comptes` (`id_compte`),
  CONSTRAINT `FKMS` FOREIGN KEY (`salon`) REFERENCES `Salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Requetes`
--

DROP TABLE IF EXISTS `Requetes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Requetes` (
  `id_request` int(11) NOT NULL AUTO_INCREMENT,
  `compte` int(11) DEFAULT NULL,
  `admin` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_request`),
  KEY `FKRC1` (`compte`),
  KEY `FKRC2` (`admin`),
  KEY `FKRS` (`salon`),
  CONSTRAINT `FKRC1` FOREIGN KEY (`compte`) REFERENCES `Comptes` (`id_compte`),
  CONSTRAINT `FKRC2` FOREIGN KEY (`admin`) REFERENCES `Comptes` (`id_compte`),
  CONSTRAINT `FKRS` FOREIGN KEY (`salon`) REFERENCES `Salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Salon`
--

DROP TABLE IF EXISTS `Salon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Salon` (
  `id_salon` int(11) NOT NULL AUTO_INCREMENT,
  `nom_salon` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id_salon`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Sanctions`
--

DROP TABLE IF EXISTS `Sanctions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Sanctions` (
  `id_sanction` int(11) NOT NULL AUTO_INCREMENT,
  `compte` int(11) DEFAULT NULL,
  `IP` varchar(15) DEFAULT NULL,
  `type` varchar(4) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id_sanction`),
  KEY `FKSC` (`compte`),
  CONSTRAINT `FKSC` FOREIGN KEY (`compte`) REFERENCES `Comptes` (`id_compte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-27 15:30:39
