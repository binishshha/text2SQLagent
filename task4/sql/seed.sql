-- Drop tables safely (order + CASCADE matters)
DROP TABLE IF EXISTS orderdetails CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS offices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS productlines CASCADE;

-- Tables
CREATE TABLE productlines (
  "productLine" VARCHAR(50) PRIMARY KEY,
  "textDescription" VARCHAR(4000),
  "htmlDescription" TEXT,
  "image" BYTEA
);

CREATE TABLE products (
  "productCode" VARCHAR(15) PRIMARY KEY,
  "productName" VARCHAR(70) NOT NULL,
  "productLine" VARCHAR(50) NOT NULL,
  "productScale" VARCHAR(10) NOT NULL,
  "productVendor" VARCHAR(50) NOT NULL,
  "productDescription" TEXT NOT NULL,
  "quantityInStock" INTEGER NOT NULL,
  "buyPrice" NUMERIC(10,2) NOT NULL,
  "MSRP" NUMERIC(10,2) NOT NULL,
  FOREIGN KEY ("productLine") REFERENCES productlines("productLine")
);

CREATE TABLE offices (
  "officeCode" VARCHAR(10) PRIMARY KEY,
  "city" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "state" VARCHAR(50),
  "country" VARCHAR(50) NOT NULL,
  "postalCode" VARCHAR(15) NOT NULL,
  "territory" VARCHAR(10) NOT NULL
);

CREATE TABLE employees (
  "employeeNumber" INTEGER PRIMARY KEY,
  "lastName" VARCHAR(50) NOT NULL,
  "firstName" VARCHAR(50) NOT NULL,
  "extension" VARCHAR(10) NOT NULL,
  "email" VARCHAR(100) NOT NULL,
  "officeCode" VARCHAR(10) NOT NULL,
  "reportsTo" INTEGER,
  "jobTitle" VARCHAR(50) NOT NULL,
  FOREIGN KEY ("reportsTo") REFERENCES employees("employeeNumber"),
  FOREIGN KEY ("officeCode") REFERENCES offices("officeCode")
);

CREATE TABLE customers (
  "customerNumber" INTEGER PRIMARY KEY,
  "customerName" VARCHAR(50) NOT NULL,
  "contactLastName" VARCHAR(50) NOT NULL,
  "contactFirstName" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "city" VARCHAR(50) NOT NULL,
  "state" VARCHAR(50),
  "postalCode" VARCHAR(15),
  "country" VARCHAR(50) NOT NULL,
  "salesRepEmployeeNumber" INTEGER,
  "creditLimit" NUMERIC(10,2),
  FOREIGN KEY ("salesRepEmployeeNumber") REFERENCES employees("employeeNumber")
);

CREATE TABLE payments (
  "customerNumber" INTEGER NOT NULL,
  "checkNumber" VARCHAR(50) NOT NULL,
  "paymentDate" DATE NOT NULL,
  "amount" NUMERIC(10,2) NOT NULL,
  PRIMARY KEY ("customerNumber", "checkNumber"),
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orders (
  "orderNumber" INTEGER PRIMARY KEY,
  "orderDate" DATE NOT NULL,
  "requiredDate" DATE NOT NULL,
  "shippedDate" DATE,
  "status" VARCHAR(15) NOT NULL,
  "comments" TEXT,
  "customerNumber" INTEGER NOT NULL,
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orderdetails (
  "orderNumber" INTEGER NOT NULL,
  "productCode" VARCHAR(15) NOT NULL,
  "quantityOrdered" INTEGER NOT NULL,
  "priceEach" NUMERIC(10,2) NOT NULL,
  "orderLineNumber" SMALLINT NOT NULL,
  PRIMARY KEY ("orderNumber", "productCode"),
  FOREIGN KEY ("orderNumber") REFERENCES orders("orderNumber"),
  FOREIGN KEY ("productCode") REFERENCES products("productCode")
);

-- Minimal representative seed data for local development.
INSERT INTO productlines ("productLine", "textDescription") VALUES
  ('Classic Cars', 'Attention to detail and historically accurate classic car replicas.'),
  ('Motorcycles', 'Two-wheeled collectible motorcycle replicas.'),
  ('Planes', 'Commercial, private, and military aircraft replicas.');

INSERT INTO products (
  "productCode", "productName", "productLine", "productScale", "productVendor",
  "productDescription", "quantityInStock", "buyPrice", "MSRP"
) VALUES
  ('S10_1949', '1952 Alpine Renault 1300', 'Classic Cars', '1:10', 'Classic Metal Creations', 'Detailed Alpine Renault model.', 7305, 98.58, 214.30),
  ('S10_1678', '1969 Harley Davidson Ultimate Chopper', 'Motorcycles', '1:10', 'Min Lin Diecast', 'Detailed Harley Davidson chopper model.', 7933, 48.81, 95.70),
  ('S18_1662', '1980s Black Hawk Helicopter', 'Planes', '1:18', 'Red Start Diecast', 'Detailed Black Hawk helicopter model.', 5330, 77.27, 157.69);

INSERT INTO offices (
  "officeCode", "city", "phone", "addressLine1", "addressLine2", "state",
  "country", "postalCode", "territory"
) VALUES
  ('1', 'San Francisco', '+1 650 219 4782', '100 Market Street', 'Suite 300', 'CA', 'USA', '94080', 'NA'),
  ('2', 'Boston', '+1 215 837 0825', '1550 Court Place', 'Suite 102', 'MA', 'USA', '02107', 'NA'),
  ('3', 'Paris', '+33 14 723 4404', '43 Rue Jouffroy D''abbans', NULL, NULL, 'France', '75017', 'EMEA');

INSERT INTO employees (
  "employeeNumber", "lastName", "firstName", "extension", "email", "officeCode", "reportsTo", "jobTitle"
) VALUES
  (1002, 'Murphy', 'Diane', 'x5800', 'dmurphy@classicmodelcars.com', '1', NULL, 'President'),
  (1056, 'Patterson', 'Mary', 'x4611', 'mpatterso@classicmodelcars.com', '1', 1002, 'VP Sales'),
  (1165, 'Jennings', 'Leslie', 'x3291', 'ljennings@classicmodelcars.com', '1', 1056, 'Sales Rep'),
  (1337, 'Bondur', 'Loui', 'x6493', 'lbondur@classicmodelcars.com', '3', 1056, 'Sales Rep');

INSERT INTO customers (
  "customerNumber", "customerName", "contactLastName", "contactFirstName", "phone",
  "addressLine1", "addressLine2", "city", "state", "postalCode", "country",
  "salesRepEmployeeNumber", "creditLimit"
) VALUES
  (103, 'Atelier graphique', 'Schmitt', 'Carine', '40.32.2555', '54 rue Royale', NULL, 'Nantes', NULL, '44000', 'France', 1337, 21000.00),
  (112, 'Signal Gift Stores', 'King', 'Jean', '7025551838', '8489 Strong St.', NULL, 'Las Vegas', 'NV', '83030', 'USA', 1165, 71800.00),
  (114, 'Australian Collectors, Co.', 'Ferguson', 'Peter', '03 9520 4555', '636 St Kilda Road', 'Level 3', 'Melbourne', 'Victoria', '3004', 'Australia', 1165, 117300.00);

INSERT INTO payments ("customerNumber", "checkNumber", "paymentDate", "amount") VALUES
  (103, 'HQ336336', '2004-10-19', 6066.78),
  (103, 'JM555205', '2003-06-05', 14571.44),
  (112, 'BO864823', '2004-12-17', 14191.12),
  (114, 'GG31455', '2003-05-20', 45864.03),
  (114, 'MA765515', '2004-12-15', 82261.22);

INSERT INTO orders (
  "orderNumber", "orderDate", "requiredDate", "shippedDate", "status", "comments", "customerNumber"
) VALUES
  (10100, '2003-01-06', '2003-01-13', '2003-01-10', 'Shipped', NULL, 103),
  (10101, '2003-01-09', '2003-01-18', '2003-01-11', 'Shipped', 'Check availability.', 112),
  (10102, '2003-01-10', '2003-01-18', '2003-01-14', 'Shipped', NULL, 114);

INSERT INTO orderdetails (
  "orderNumber", "productCode", "quantityOrdered", "priceEach", "orderLineNumber"
) VALUES
  (10100, 'S10_1949', 30, 136.00, 3),
  (10100, 'S10_1678', 50, 55.09, 2),
  (10101, 'S18_1662', 45, 120.92, 1),
  (10102, 'S10_1949', 39, 95.55, 2),
  (10102, 'S10_1678', 41, 43.13, 1);
