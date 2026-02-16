-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Oct 27, 2025 at 10:27 AM
-- Server version: 10.11.14-MariaDB-0+deb12u2
-- PHP Version: 8.2.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ocpp`
--

-- --------------------------------------------------------

--
-- Table structure for table `charge_points`
--

CREATE TABLE `charge_points` (
  `id` varchar(50) NOT NULL,
  `vendor` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `firmware_version` varchar(100) DEFAULT NULL,
  `last_heartbeat` timestamp NULL DEFAULT NULL,
  `connected` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `charge_points`
--

INSERT INTO `charge_points` (`id`, `vendor`, `model`, `firmware_version`, `last_heartbeat`, `connected`) VALUES
('CP_111', 'DemoVendor', 'DemoModel', NULL, '2025-10-27 10:15:56', 0),
('CP_112', 'DemoVendor', 'DemoModel', NULL, '2025-10-27 10:16:05', 0),
('CP_123', 'DemoVendor', 'DemoModel', NULL, '2025-10-27 10:00:01', 0),
('CP_321', 'DemoVendor', 'DemoModel', NULL, '2025-10-27 09:21:15', 0);

-- --------------------------------------------------------

--
-- Table structure for table `connectors`
--

CREATE TABLE `connectors` (
  `cp_id` varchar(50) NOT NULL,
  `connector_id` int(11) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `error_code` varchar(50) DEFAULT NULL,
  `last_update` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `connectors`
--

INSERT INTO `connectors` (`cp_id`, `connector_id`, `status`, `error_code`, `last_update`) VALUES
('CP_111', 1, 'Available', 'NoError', '2025-10-27 10:15:31'),
('CP_112', 1, 'Available', 'NoError', '2025-10-27 10:15:35'),
('CP_123', 1, 'Available', 'NoError', '2025-10-27 09:59:21'),
('CP_321', 1, 'Available', 'NoError', '2025-10-27 09:21:00');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `cp_id` varchar(50) DEFAULT NULL,
  `connector_id` int(11) DEFAULT NULL,
  `id_tag` varchar(50) DEFAULT NULL,
  `meter_start` int(11) DEFAULT NULL,
  `meter_stop` int(11) DEFAULT NULL,
  `start_ts` timestamp NULL DEFAULT NULL,
  `stop_ts` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `cp_id`, `connector_id`, `id_tag`, `meter_start`, `meter_stop`, `start_ts`, `stop_ts`) VALUES
(1, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 07:41:47', '2025-10-27 07:41:52'),
(2, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 07:47:33', '2025-10-27 07:47:38'),
(3, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 07:54:36', '2025-10-27 07:54:41'),
(4, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 07:58:20', '2025-10-27 07:58:25'),
(5, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:04:49', '2025-10-27 08:04:54'),
(6, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:11:57', '2025-10-27 08:12:02'),
(7, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:16:18', '2025-10-27 08:16:23'),
(8, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:17:38', '2025-10-27 08:17:43'),
(9, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:20:28', '2025-10-27 08:20:33'),
(10, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:21:10', '2025-10-27 08:21:15'),
(11, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:31:33', '2025-10-27 08:31:38'),
(12, 'CP_321', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:32:38', '2025-10-27 08:32:43'),
(13, 'CP_321', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:37:14', '2025-10-27 08:37:19'),
(14, 'CP_321', 1, 'DEMO-123', 0, 1000, '2025-10-27 08:54:36', '2025-10-27 08:54:41'),
(15, 'CP_321', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:02:15', '2025-10-27 09:02:20'),
(16, 'CP_321', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:21:00', '2025-10-27 09:21:05'),
(17, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:24:20', '2025-10-27 09:24:25'),
(18, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:26:55', '2025-10-27 09:27:00'),
(19, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:29:59', '2025-10-27 09:30:04'),
(20, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:41:30', '2025-10-27 09:41:35'),
(21, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:45:04', '2025-10-27 09:45:09'),
(22, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:46:59', '2025-10-27 09:47:09'),
(23, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:53:42', '2025-10-27 09:53:52'),
(24, 'CP_123', 1, 'DEMO-123', 0, NULL, '2025-10-27 09:56:06', NULL),
(25, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:56:28', '2025-10-27 09:56:38'),
(26, 'CP_123', 1, 'DEMO-123', 0, 1000, '2025-10-27 09:59:11', '2025-10-27 09:59:21'),
(27, 'CP_111', 1, 'DEMO-123', 0, 1000, '2025-10-27 10:00:25', '2025-10-27 10:00:35'),
(28, 'CP_111', 1, 'DEMO-123', 0, 1000, '2025-10-27 10:02:42', '2025-10-27 10:02:52'),
(29, 'CP_111', 1, 'DEMO-123', 0, 1000, '2025-10-27 10:11:15', '2025-10-27 10:11:25'),
(30, 'CP_111', 1, 'DEMO-123', 0, 1000, '2025-10-27 10:15:21', '2025-10-27 10:15:31'),
(31, 'CP_112', 1, 'DEMO-123', 0, 1000, '2025-10-27 10:15:35', '2025-10-27 10:15:40');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `charge_points`
--
ALTER TABLE `charge_points`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `connectors`
--
ALTER TABLE `connectors`
  ADD PRIMARY KEY (`cp_id`,`connector_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`);

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `id_tag` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `id_tag`, `name`, `email`) VALUES
(1, 'DEMO-123', 'Demo User', 'demo@example.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_tag` (`id_tag`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
