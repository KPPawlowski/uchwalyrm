-- phpMyAdmin SQL Dump
-- version 4.4.15
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 15, 2017 at 11:43 PM
-- Server version: 5.6.36
-- PHP Version: 5.3.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kacpaw_urm`
--

-- --------------------------------------------------------

--
-- Table structure for table `DzUrzWojDoln`
--

CREATE TABLE IF NOT EXISTS `DzUrzWojDoln` (
  `Title` varchar(1536) DEFAULT NULL,
  `LegalActType` varchar(32) DEFAULT NULL,
  `DuplicateChar` varchar(32) DEFAULT NULL,
  `ActDate` varchar(32) DEFAULT NULL,
  `PdfBookUrlListUrl` varchar(64) DEFAULT NULL,
  `PdfBookUrlListName` varchar(32) DEFAULT NULL,
  `IsTechnicalPosition` varchar(1) DEFAULT NULL,
  `Subject` varchar(1536) DEFAULT NULL,
  `PdfUrl` varchar(256) DEFAULT NULL,
  `CaseNumber` varchar(96) DEFAULT NULL,
  `PublishersListFlat` varchar(128) DEFAULT NULL,
  `Oid` int(11) DEFAULT NULL,
  `Publisher` varchar(256) DEFAULT NULL,
  `Day` int(11) DEFAULT NULL,
  `PublishersList` varchar(384) DEFAULT NULL,
  `ActTypeId` int(11) DEFAULT NULL,
  `HasExpired` varchar(1) DEFAULT NULL,
  `Year` int(4) DEFAULT NULL,
  `Month` int(2) DEFAULT NULL,
  `Position` int(5) DEFAULT NULL,
  `PublicationDate` varchar(48) DEFAULT NULL,
  `JournalNumber` int(5) DEFAULT NULL,
  `JSON` text
) ENGINE=InnoDB DEFAULT CHARSET=latin2;

-- --------------------------------------------------------

--
-- Table structure for table `DzUrzWojDolnOrgany`
--

CREATE TABLE IF NOT EXISTS `DzUrzWojDolnOrgany` (
  `Oid` int(11) DEFAULT NULL,
  `Name` varchar(256) DEFAULT NULL,
  `DzUrzWojnDolnOid` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin2;

-- --------------------------------------------------------

--
-- Stand-in structure for view `DzUrzWojnDolnZjaRNView`
--
CREATE TABLE IF NOT EXISTS `DzUrzWojnDolnZjaRNView` (
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `DzUrzWojnDolnZjaView`
--
CREATE TABLE IF NOT EXISTS `DzUrzWojnDolnZjaView` (
`Year` int(4)
,`Month` int(2)
,`Position` int(5)
,`ActDate` date
,`PublicationDate` date
,`Title` varchar(1536)
,`Name` varchar(256)
,`PdfUrl` varchar(256)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `DzUrzZlotoryja`
--
CREATE TABLE IF NOT EXISTS `DzUrzZlotoryja` (
);

-- --------------------------------------------------------

--
-- Structure for view `DzUrzWojnDolnZjaRNView`
--
DROP TABLE IF EXISTS `DzUrzWojnDolnZjaRNView`;
-- in use(#1267 - Illegal mix of collations (latin2_general_ci,IMPLICIT) and (utf8_general_ci,COERCIBLE) for operation 'like')

-- --------------------------------------------------------

--
-- Structure for view `DzUrzWojnDolnZjaView`
--
DROP TABLE IF EXISTS `DzUrzWojnDolnZjaView`;

CREATE ALGORITHM=UNDEFINED DEFINER=`kacpaw_urm`@`%` SQL SECURITY DEFINER VIEW `DzUrzWojnDolnZjaView` AS select `b`.`Year` AS `Year`,`b`.`Month` AS `Month`,`b`.`Position` AS `Position`,str_to_date(`b`.`ActDate`,'%Y-%m-%d') AS `ActDate`,str_to_date(`b`.`PublicationDate`,'%Y-%m-%d') AS `PublicationDate`,`b`.`Title` AS `Title`,`a`.`Name` AS `Name`,`b`.`PdfUrl` AS `PdfUrl` from (`DzUrzWojDolnOrgany` `a` join `DzUrzWojDoln` `b` on((`a`.`DzUrzWojnDolnOid` = `b`.`Oid`))) where (`a`.`Oid` in (711,157,327,383,465,918)) order by `a`.`DzUrzWojnDolnOid` desc;

-- --------------------------------------------------------

--
-- Structure for view `DzUrzZlotoryja`
--
DROP TABLE IF EXISTS `DzUrzZlotoryja`;
-- in use(#1267 - Illegal mix of collations (latin2_general_ci,IMPLICIT) and (utf8_general_ci,COERCIBLE) for operation 'like')

--
-- Indexes for dumped tables
--

--
-- Indexes for table `DzUrzWojDoln`
--
ALTER TABLE `DzUrzWojDoln`
  ADD UNIQUE KEY `UC_YearPosition` (`Year`,`Position`,`JournalNumber`) USING BTREE;

--
-- Indexes for table `DzUrzWojDolnOrgany`
--
ALTER TABLE `DzUrzWojDolnOrgany`
  ADD UNIQUE KEY `Oid` (`Oid`,`Name`,`DzUrzWojnDolnOid`),
  ADD UNIQUE KEY `Oid_2` (`Oid`,`Name`,`DzUrzWojnDolnOid`),
  ADD KEY `id_dzurzwojndolnoid` (`DzUrzWojnDolnOid`),
  ADD KEY `id_organy_oid` (`Oid`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
