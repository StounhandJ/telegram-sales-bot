SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `ban_list` (
  `id` int NOT NULL,
  `userID` int NOT NULL,
  `date` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `department` (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `tag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `messages` (
  `id` int NOT NULL,
  `userID` int NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `isOrder` tinyint(1) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `date` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tasks` (
  `id` int NOT NULL,
  `orderID` int NOT NULL,
  `staff` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `departmentTag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tasks_completes` (
  `id` int UNSIGNED NOT NULL,
  `userID` int UNSIGNED NOT NULL,
  `orderID` int UNSIGNED NOT NULL,
  `departmentTag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `date` int UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


ALTER TABLE `ban_list`
  ADD PRIMARY KEY (`id`),
  ADD KEY `userID` (`userID`);

ALTER TABLE `department`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `tasks`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `tasks_completes`
  ADD PRIMARY KEY (`id`);


ALTER TABLE `ban_list`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `department`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `messages`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `tasks`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `tasks_completes`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
