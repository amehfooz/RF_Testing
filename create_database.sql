SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "-08:00";
--
-- Create Database
--

CREATE Database IF NOT EXISTS RF_Data;
use RF_Data

--
-- Table structure for table `SWConfig`
--
CREATE TABLE IF NOT EXISTS `SWConfig` (
	`SWConfigID` int(16) PRIMARY KEY NOT NULL AUTO_INCREMENT,
	`ImageName` varchar(256),
	`BuildNumber` int(16)
) ENGINE=InnoDB;

--
-- Table structure for table `File`
--

CREATE TABLE IF NOT EXISTS `File` (
	`FileID` BIGINT PRIMARY KEY,
	`SN` varchar(32),
	`Station` varchar(32),
	`Revision` varchar(32),
	`TestType` enum('Mask', 'EVM', 'Sens', 'PwrAccuracy', 'Simu', 'Blocker'),
	`COMMENT` varchar(256) DEFAULT NULL,
	`SWConfigID` int(16) DEFAULT NULL,
	`TESTRUNTIME` DATETIME
) ENGINE=InnoDB;
-- 
-- Table structure for table `TestRun`
--
CREATE TABLE IF NOT EXISTS `TestRun` (
	`TestRunID` int(32),
	`FileID` BIGINT, 
	`CHAIN` int(8),
	`BW` enum('20', '40', '80', '160'),
	`CHAN` int(8),
	`CHAN_2` int(8),
	`BAND` enum('2G', '5G'),
	`RATE` enum('v0-1', 'v9-1', 'm7', 'v8-1', 'v7-1', 'm0', '54', '1l', '11s', '11'),
	`ANT` enum('0', '1', '2', '3', '0-2', '1-3'),

	PRIMARY KEY (`TestRunID`, `FileID`),
	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;
-- 
-- Table structure for table `RXPER`
--
CREATE TABLE IF NOT EXISTS `RXPER` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`PWR` int(8),
	`PER` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXEVM` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`Target_Power` decimal,
	`LP_EVM` decimal,
	`LP_Power` decimal,
	`LP_freqErrorHz` decimal,
	`LP_ClockErrorPpm` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `RXSensitivity` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`PER Floor` decimal,
	`Low End Sensitivity` decimal,
	`High End Sensitivity` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXEVMPower` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`EVM Floor` decimal,
	`TXEVM` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXPower` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`TargetPower` decimal,
	`MeasurementMethod` varchar(32),
	`MeasuredPower` decimal,
	`MeasuredError` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `RXBlocker` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`BlockerFreq` decimal,
	`BlockerPower` decimal,
	`LVL_PWR_Offset` decimal,

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Spectrum` (
	`TestRunID` int(32),
	`FileID` BIGINT,
	`Region` enum('LO_A', 'LO_B', 'LO_C', 'LO_D', 'LO_E', 'UP_A', 'UP_B', 'UP_C', 'UP_D', 'UP_E'),
	`LP_FreqOffset` decimal,
	`Mask_Power` decimal,
	`Mask_Limit` decimal,
	`Pass` boolean,
	`Margin` decimal,
	`Fail` decimal,
	SpectrumPlotID int(32),

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
) ENGINE=InnoDB;