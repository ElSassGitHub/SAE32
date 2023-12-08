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
-- Table structure for table `IP`
--

DROP TABLE IF EXISTS `IP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IP` (
  `compte` int(11) DEFAULT NULL,
  `IP` varchar(15) DEFAULT NULL,
  KEY `FKIC` (`compte`),
  CONSTRAINT `FKIC` FOREIGN KEY (`compte`) REFERENCES `comptes` (`id_compte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `autorisations`
--

DROP TABLE IF EXISTS `autorisations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autorisations` (
  `compte` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  `autorise` tinyint(1) DEFAULT 0,
  `niv_auto` int(11) DEFAULT 0,
  KEY `FKAC` (`compte`),
  KEY `FKAS` (`salon`),
  CONSTRAINT `FKAC` FOREIGN KEY (`compte`) REFERENCES `comptes` (`id_compte`),
  CONSTRAINT `FKAS` FOREIGN KEY (`salon`) REFERENCES `salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comptes`
--

DROP TABLE IF EXISTS `comptes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comptes` (
  `id_compte` int(11) NOT NULL AUTO_INCREMENT,
  `identifiant` varchar(40) DEFAULT NULL,
  `mdp` varchar(40) DEFAULT NULL,
  `statut_co` varchar(10) DEFAULT 'offline',
  `salon` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_compte`),
  UNIQUE KEY `identifiant` (`identifiant`),
  KEY `FKCS` (`salon`),
  CONSTRAINT `FKCS` FOREIGN KEY (`salon`) REFERENCES `salon` (`id_salon`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `id_message` int(11) NOT NULL AUTO_INCREMENT,
  `msg` varchar(200) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `compte` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_message`),
  KEY `FKMC` (`compte`),
  KEY `FKMS` (`salon`),
  CONSTRAINT `FKMC` FOREIGN KEY (`compte`) REFERENCES `comptes` (`id_compte`),
  CONSTRAINT `FKMS` FOREIGN KEY (`salon`) REFERENCES `salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `requetes`
--

DROP TABLE IF EXISTS `requetes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `requetes` (
  `id_requete` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) DEFAULT NULL,
  `admin` int(11) DEFAULT NULL,
  `salon` int(11) DEFAULT NULL,
  `solved` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id_requete`),
  KEY `FKRC1` (`user`),
  KEY `FKRC2` (`admin`),
  KEY `FKRS` (`salon`),
  CONSTRAINT `FKRC1` FOREIGN KEY (`user`) REFERENCES `comptes` (`id_compte`),
  CONSTRAINT `FKRC2` FOREIGN KEY (`admin`) REFERENCES `comptes` (`id_compte`),
  CONSTRAINT `FKRS` FOREIGN KEY (`salon`) REFERENCES `salon` (`id_salon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salon`
--

DROP TABLE IF EXISTS `salon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salon` (
  `id_salon` int(11) NOT NULL AUTO_INCREMENT,
  `nom_salon` varchar(40) DEFAULT NULL,
  `nb_users` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_salon`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-07 16:49:27
