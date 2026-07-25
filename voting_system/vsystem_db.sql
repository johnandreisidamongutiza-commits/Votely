-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 05, 2026 at 07:13 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `vsystem_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity_logs`
--

CREATE TABLE `activity_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` varchar(50) NOT NULL,
  `election_id` int(11) DEFAULT NULL,
  `details` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activity_logs`
--

INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `election_id`, `details`, `created_at`) VALUES
(1, 32, 'Viewed Results', NULL, NULL, '2026-05-03 04:49:23'),
(2, 32, 'Viewed Results', 4, NULL, '2026-05-03 05:25:36'),
(3, 32, 'Viewed Results', NULL, NULL, '2026-05-03 05:29:06'),
(4, 32, 'Submitted Vote', 8, 'Voted in 1 out of 2 positions', '2026-05-03 08:24:24'),
(5, 32, 'Submitted Vote', 8, 'Voted in 1 out of 2 positions', '2026-05-03 08:25:07'),
(6, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:25:18'),
(7, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:39:30'),
(8, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:39:51'),
(9, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:40:22'),
(10, 32, 'Viewed Results', 4, NULL, '2026-05-03 08:42:16'),
(11, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:43:50'),
(12, 32, 'Viewed Results', 8, NULL, '2026-05-03 08:49:41'),
(13, 32, 'Viewed Results', 4, NULL, '2026-05-03 08:49:53'),
(14, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:17:37'),
(15, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:18:48'),
(16, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:32:51'),
(17, 32, 'Viewed Results', 7, NULL, '2026-05-03 09:33:03'),
(18, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:33:07'),
(19, 32, 'Viewed Results', 7, NULL, '2026-05-03 09:46:39'),
(20, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:46:48'),
(21, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:48:16'),
(22, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:48:28'),
(23, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:48:32'),
(24, 32, 'Viewed Results', 8, NULL, '2026-05-03 09:48:40'),
(25, 32, 'Viewed Results', 8, NULL, '2026-05-03 10:13:47'),
(26, 32, 'Submitted Vote', 7, 'Voted in 1 out of 3 positions', '2026-05-03 10:47:04'),
(27, 32, 'Viewed Results', 7, NULL, '2026-05-03 10:47:11'),
(28, 32, 'Submitted Vote', 7, 'Voted in 2 out of 3 positions', '2026-05-03 10:51:40'),
(29, 32, 'Viewed Results', 7, NULL, '2026-05-04 03:37:08'),
(30, 25, 'Register Voter', NULL, 'Registered inactive voter 241-4444 (Onin Napiza)', '2026-05-05 01:57:12'),
(31, 25, 'Start Election', 10, 'Started election 10', '2026-05-05 02:07:57'),
(32, 25, 'End Election', 10, 'Ended election 10', '2026-05-05 02:08:13'),
(33, 25, 'Create Election', NULL, 'Created election \"vcxzvcz\" running 2026-05-20T10:18 to 2026-05-28T10:18', '2026-05-05 02:08:36'),
(34, 25, 'Create Election', NULL, 'Created election \"adfafdsa\" running 2026-06-06T12:59 to 2026-06-18T12:59', '2026-05-05 04:51:05'),
(35, 25, 'Start Election', 12, 'Started election 12', '2026-05-05 04:51:17'),
(36, 25, 'End Election', 12, 'Ended election 12', '2026-05-05 04:51:33'),
(37, 32, 'Viewed Results', 6, NULL, '2026-05-05 04:54:17');

-- --------------------------------------------------------

--
-- Table structure for table `candidates`
--

CREATE TABLE `candidates` (
  `id` int(11) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `position_id` int(11) NOT NULL,
  `election_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidates`
--

INSERT INTO `candidates` (`id`, `firstname`, `lastname`, `photo`, `position_id`, `election_id`) VALUES
(1, 'Gerald', 'Delo Santos', 'Google__G__logo.svg.png', 1, 4),
(12, 'John Andrei', 'Gutiza', 'Todo_LIst.png', 7, 8),
(13, 'John Andrei', 'Gutiza', NULL, 8, 8),
(14, 'Onin', 'Napiza', NULL, 8, 8),
(15, 'John Andrei', 'Gutiza', NULL, 9, 7),
(16, 'Onin', 'Napiza', NULL, 9, 7),
(17, 'John Andrei', 'Gutiza', 'Todo_LIst-removebg-preview.png', 10, 7),
(18, 'Onin', 'Napiza', NULL, 10, 7),
(19, 'John Andrei', 'Gutiza', NULL, 11, 7),
(20, 'Onin', 'Napiza', NULL, 11, 7);

-- --------------------------------------------------------

--
-- Table structure for table `elections`
--

CREATE TABLE `elections` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `status` enum('draft','active','ended') DEFAULT 'draft',
  `is_archived` tinyint(1) NOT NULL DEFAULT 0,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `elections`
--

INSERT INTO `elections` (`id`, `title`, `description`, `start_date`, `end_date`, `status`, `is_archived`, `created_by`, `created_at`, `updated_at`) VALUES
(4, 'LU election 2026', '', '2026-04-05 04:01:00', '2026-04-08 07:57:00', 'ended', 0, 25, '2026-03-29 23:58:25', '2026-05-03 10:44:03'),
(6, 'Student Election 1111', '', '2026-05-04 15:28:00', '2026-05-05 15:28:00', 'active', 0, 25, '2026-05-03 07:28:46', '2026-05-04 22:30:19'),
(7, 'SCouncil 2026', '', '2026-05-03 17:00:00', '2026-05-05 15:57:00', 'ended', 0, 25, '2026-05-03 07:59:16', '2026-05-05 02:06:26'),
(8, 'SSStudent Council', '', '2026-05-03 16:15:00', '2026-05-04 16:09:00', 'ended', 0, 25, '2026-05-03 08:09:43', '2026-05-04 22:30:19'),
(9, 'asdfasdf', '', '2026-05-06 10:09:00', '2026-05-07 10:09:00', 'draft', 0, 25, '2026-05-05 01:59:35', '2026-05-05 01:59:35'),
(10, 'asdffdafda', '', '2026-05-05 10:07:57', '2026-05-09 10:16:00', 'ended', 0, 25, '2026-05-05 02:06:50', '2026-05-05 02:08:13'),
(11, 'vcxzvcz', '', '2026-05-20 10:18:00', '2026-05-28 10:18:00', 'draft', 0, 25, '2026-05-05 02:08:36', '2026-05-05 02:08:36'),
(12, 'adfafdsa', '', '2026-05-05 12:51:17', '2026-06-18 12:59:00', 'ended', 1, 25, '2026-05-05 04:51:05', '2026-05-05 04:51:38');

-- --------------------------------------------------------

--
-- Table structure for table `notifications_sent`
--

CREATE TABLE `notifications_sent` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `election_id` int(11) NOT NULL,
  `type` varchar(10) NOT NULL,
  `sent_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications_sent`
--

INSERT INTO `notifications_sent` (`id`, `user_id`, `election_id`, `type`, `sent_at`) VALUES
(1, 32, 8, '24h', '2026-05-03 08:19:19'),
(2, 32, 8, '1h', '2026-05-03 08:19:22'),
(3, 32, 7, '24h', '2026-05-03 10:41:48'),
(4, 32, 7, '1h', '2026-05-03 10:41:51'),
(5, 32, 6, '24h', '2026-05-05 04:43:27');

-- --------------------------------------------------------

--
-- Table structure for table `positions`
--

CREATE TABLE `positions` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `election_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `positions`
--

INSERT INTO `positions` (`id`, `name`, `election_id`) VALUES
(1, 'President', 4),
(2, 'Vice President', 4),
(3, 'Secretary', 4),
(4, 'PIO', 4),
(5, 'President', 6),
(6, 'Vice President', 6),
(7, 'President', 8),
(8, 'Vice President', 8),
(9, 'President', 7),
(10, 'Vice President', 7),
(11, 'Secretary', 7);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','user','superadmin') DEFAULT 'user',
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `activation_code` varchar(6) DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `user_id`, `firstname`, `lastname`, `email`, `password`, `role`, `status`, `activation_code`, `profile_photo`) VALUES
(23, '241-0005', 'joan', 'gutiza', 'kyutipakyu69@gmail.com', '$2b$12$uOxvea8JSw8XQCa2e48gj.hU9KHBwSG21IaymtEavKS8.6yItF1ey', 'user', 'active', NULL, NULL),
(25, 'ADM-0001', 'Admin', 'Admin', 'johnandreigutiza125@gmail.com', 'admin123', 'admin', 'active', NULL, NULL),
(28, '241-0360', 'Onin', 'Napiza', 'oninnapiza4@gmail.com', '123', 'user', 'active', NULL, NULL),
(29, 'SADM-0001', 'Super', 'Admin', 'jgutiza30@gmail.com', 'superadmin123', 'superadmin', 'active', NULL, NULL),
(32, '241-0333', 'John Andrei', 'Gutiza', 'johnandreisidamongutiza@gmail.com', '123', 'user', 'active', NULL, 'c63a636d53b84b969a8ff7852ef35b5c.png'),
(33, '241-0007', 'Minato', 'Lasdsd', 'student@gmail.com', '', 'user', 'inactive', '794117', NULL),
(35, '241-4444', 'Onin', 'Napiza', 'oninnapiza@gmail.com', '', 'user', 'inactive', '191024', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `user_2fa`
--

CREATE TABLE `user_2fa` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `otp_code` varchar(6) DEFAULT NULL,
  `otp_expires` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_2fa`
--

INSERT INTO `user_2fa` (`id`, `user_id`, `is_enabled`, `otp_code`, `otp_expires`) VALUES
(1, 25, 1, NULL, NULL),
(2, 32, 1, '856696', '2026-05-05 13:14:56');

-- --------------------------------------------------------

--
-- Table structure for table `user_notifications`
--

CREATE TABLE `user_notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `election_id` int(11) NOT NULL,
  `type` varchar(10) NOT NULL,
  `message` varchar(255) NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_notifications`
--

INSERT INTO `user_notifications` (`id`, `user_id`, `election_id`, `type`, `message`, `is_read`, `created_at`) VALUES
(1, 32, 8, '24h', '\"SSStudent Council\" closes in less than 24 hours. 2 position(s) left to vote.', 1, '2026-05-03 08:19:19'),
(2, 32, 8, '1h', 'URGENT: \"SSStudent Council\" closes in less than 1 hour! 2 position(s) left to vote.', 1, '2026-05-03 08:19:22'),
(3, 32, 7, '24h', '\"SCouncil 2026\" closes in less than 24 hours. 1 position(s) left to vote.', 1, '2026-05-03 10:41:48'),
(4, 32, 7, '1h', 'URGENT: \"SCouncil 2026\" closes in less than 1 hour! 1 position(s) left to vote.', 1, '2026-05-03 10:41:51'),
(5, 32, 6, '24h', '\"Student Election 1111\" closes in less than 24 hours. 2 position(s) left to vote.', 1, '2026-05-05 04:43:27');

-- --------------------------------------------------------

--
-- Table structure for table `votes`
--

CREATE TABLE `votes` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `position_id` int(11) NOT NULL,
  `election_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `votes`
--

INSERT INTO `votes` (`id`, `user_id`, `candidate_id`, `position_id`, `election_id`) VALUES
(1, 32, 12, 7, 8),
(2, 32, 14, 8, 8),
(3, 32, 16, 9, 7),
(4, 32, 17, 10, 7),
(5, 32, 20, 11, 7);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `election_id` (`election_id`);

--
-- Indexes for table `candidates`
--
ALTER TABLE `candidates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `position_id` (`position_id`),
  ADD KEY `election_id` (`election_id`);

--
-- Indexes for table `elections`
--
ALTER TABLE `elections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `notifications_sent`
--
ALTER TABLE `notifications_sent`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_notification` (`user_id`,`election_id`,`type`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `election_id` (`election_id`);

--
-- Indexes for table `positions`
--
ALTER TABLE `positions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_positions_election` (`election_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_2fa`
--
ALTER TABLE `user_2fa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `user_notifications`
--
ALTER TABLE `user_notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `election_id` (`election_id`);

--
-- Indexes for table `votes`
--
ALTER TABLE `votes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_votes_user` (`user_id`),
  ADD KEY `fk_votes_candidate` (`candidate_id`),
  ADD KEY `fk_votes_position` (`position_id`),
  ADD KEY `fk_votes_election` (`election_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activity_logs`
--
ALTER TABLE `activity_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT for table `candidates`
--
ALTER TABLE `candidates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `elections`
--
ALTER TABLE `elections`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `notifications_sent`
--
ALTER TABLE `notifications_sent`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `positions`
--
ALTER TABLE `positions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `user_2fa`
--
ALTER TABLE `user_2fa`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user_notifications`
--
ALTER TABLE `user_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `votes`
--
ALTER TABLE `votes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD CONSTRAINT `fk_logs_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `candidates`
--
ALTER TABLE `candidates`
  ADD CONSTRAINT `fk_candidates_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_candidates_position` FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `elections`
--
ALTER TABLE `elections`
  ADD CONSTRAINT `fk_elections_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications_sent`
--
ALTER TABLE `notifications_sent`
  ADD CONSTRAINT `fk_notif_sent_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_notif_sent_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `positions`
--
ALTER TABLE `positions`
  ADD CONSTRAINT `fk_positions_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_2fa`
--
ALTER TABLE `user_2fa`
  ADD CONSTRAINT `fk_2fa_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_notifications`
--
ALTER TABLE `user_notifications`
  ADD CONSTRAINT `fk_user_notif_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user_notif_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `votes`
--
ALTER TABLE `votes`
  ADD CONSTRAINT `fk_votes_candidate` FOREIGN KEY (`candidate_id`) REFERENCES `candidates` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_votes_election` FOREIGN KEY (`election_id`) REFERENCES `elections` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_votes_position` FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_votes_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
