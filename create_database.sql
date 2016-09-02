SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "-08:00";
--
-- Create Database
--

CREATE Database IF NOT EXISTS RF_Data;
use RF_Data

--
-- Table structure for table `StationID`
--
CREATE TABLE IF NOT EXISTS `StationID` (
	`StationID` int(16) PRIMARY KEY,
	`Bench` varchar(32),
	`Equipment` varchar(32),
	`Calibaration` varchar(256)
) ENGINE=InnoDB;

--
-- Table structure for table `SWConfig`
--
CREATE TABLE IF NOT EXISTS `SWConfig` (
	`SWConfigID` int(16) PRIMARY KEY,
	`ImageName` varchar(256),
	`BuildNumber` int(16)
) ENGINE=InnoDB;

-- 
-- Table structure for table `TestRun`
--
CREATE TABLE IF NOT EXISTS `TestRun` (
	`TestRunID` int(32) PRIMARY KEY,
	`SN` varchar(32),
	`Revision` varchar(32),
	`StationID` int(16), 
	`SWConfigID` int(16),
	`TESTRUNTIME` DATETIME,
	`TestType` enum('Mask', 'EVM', 'Sens'),
	`CHAIN` int(8),
	`BW` enum('20', '40', '80', '160'),
	`CHAN` int(8),
	`BAND` enum('2G', '5G'),
	`RATE` varchar(10),
	`ANT` int(8),
	`COMMENT` varchar(256),

	FOREIGN KEY (`StationID`) REFERENCES `StationID`(`StationID`),
	FOREIGN KEY (`SWConfigID`) REFERENCES `SWConfig`(`SWConfigID`)
) ENGINE=InnoDB;
-- 
-- Table structure for table `RXPER`
--
CREATE TABLE IF NOT EXISTS `RXPER` (
	`TestRunID` int(32),
	`PWR` int(8),
	`PER` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXEVM` (
	`TestRunID` int(32),
	`TargetPower` decimal,
	`LP_EVM` decimal,
	`LP_Power` decimal,
	`LP_freqErrorHz` decimal,
	`LP_ClockErrorPpm` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;
