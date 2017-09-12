# Categories Table
CREATE TABLE `categories` (
  `categories_id` int(11) NOT NULL,
  `id` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `products` int(11) NOT NULL,
  `url` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# Product Table
CREATE TABLE `product` (
  `id` bigint(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `brands` varchar(100) NOT NULL,
  `nutrition_grade` varchar(1) NOT NULL,
  `fat` float NOT NULL,
  `saturated_fat` float NOT NULL,
  `sugars` float NOT NULL,
  `salt` float NOT NULL,
  `url` varchar(150) NOT NULL,
  `categorie` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;