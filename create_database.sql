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
CREATE TABLE IF NOT EXISTS `Station` (
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
-- Table structure for table `File`
--

CREATE TABLE IF NOT EXISTS `File` (
	`FileID` int(32) PRIMARY KEY,
	`SN` varchar(16),
	`Revision` varchar(32),
	`StationID` int(16), 
	`COMMENT` varchar(256),
	`SWConfigID` int(16),
	`TESTRUNTIME` DATETIME,
	
	FOREIGN KEY (`StationID`) REFERENCES `Station`(`StationID`),
	FOREIGN KEY (`SWConfigID`) REFERENCES `SWConfig`(`SWConfigID`)
)
-- 
-- Table structure for table `TestRun`
--
CREATE TABLE IF NOT EXISTS `TestRun` (
	`TestRunID` int(32) PRIMARY KEY,
	`FileID` int(32),
	`TestType` enum('Mask', 'EVM', 'Sens'),
	`CHAIN` int(8),
	`BW` enum('20', '40', '80', '160'),
	`CHAN` int(8),
	`BAND` enum('2G', '5G'),
	`RATE` varchar(10),
	`ANT` int(8),

	FOREIGN KEY (`FileID`) REFERENCES `File`(`FileID`)
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

CREATE TABLE IF NOT EXISTS `RXSensitivity` (
	`TestRunID` int(32),
	`PER Floor` decimal,
	`Low End Sensitivity` decimal,
	`High End Sensitivity` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXEVMPower` (
	`TestRunID` int(32),
	`EVM Floor` decimal,
	`TXEVM` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`) 
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `TXPower` (
	`TestRunID` int(32),
	`TargetPower` decimal,
	`MeasurementMethod` varchar(32),
	`MeasuredPower` decimal,
	`MeasuredError` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `RXBlocker` (
	`TestRunID` int(32),
	`BlockerFreq` decimal,
	`BlockerPower` decimal,

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `SpectrumMask` (
	`TestRunID` int(32),
	`Region` varchar(32),
	`LP_FreqOffset` decimal,
	`Mask_Power` decimal,
	`Mask_Limit` decimal,
	`Pass/Fail` boolean,
	`MARGIN` decimal,
	`FAIL(%)` decimal,
	SpectrumPlotID int(32),

	FOREIGN KEY (`TestRunID`) REFERENCES `TestRun`(`TestRunID`)
) ENGINE=InnoDB;