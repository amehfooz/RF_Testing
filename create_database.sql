SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "-08:00";

--
-- Create Database
--

CREATE Database IF NOT EXISTS RF_Data;

-- 
-- Table structure for table 'TestRun'
--

CREATE TABLE IF NOT EXISTS 'TestRun' (
	'TestRunID' int(32)
	'SN' char
	'Revision' char
	'StationID' int(16)
	'SWConfig' int(16)
	'TESTRUNTIME' DATETIME
	'TestType' enum('Mask', 'EVM', 'Sens')
	'CHAIN' int(8)
	'BW' enum('20', '40', '80', '160')
	'CHAN' int(8)
	'BAND' enum('2G', '5G')
) ENGINE=InnoDB