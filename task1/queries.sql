-- Q1. List all products
SELECT *
FROM products
ORDER BY "productCode";

-- Q2. Get all customers
SELECT *
FROM customers
ORDER BY "customerNumber";

-- Q3. Show all orders
SELECT *
FROM orders
ORDER BY "orderNumber";

-- Q4. List all employees
SELECT *
FROM employees
ORDER BY "employeeNumber";

-- Q5. Get all offices
SELECT *
FROM offices
ORDER BY "officeCode";

-- Q6. Show all product lines
SELECT *
FROM productlines
ORDER BY "productLine";

-- Q7. List all payments
SELECT *
FROM payments
ORDER BY "customerNumber", "checkNumber";

-- Q8. Get product names and prices
SELECT
  "productName",
  "buyPrice",
  "MSRP"
FROM products
ORDER BY "productName";

-- Q9. Get customer names and cities
SELECT
  "customerName",
  "city"
FROM customers
ORDER BY "customerName";

-- Q10. List employee first and last names
SELECT
  "firstName",
  "lastName"
FROM employees
ORDER BY "lastName", "firstName";

-- Q11. Get all order dates
SELECT
  "orderNumber",
  "orderDate"
FROM orders
ORDER BY "orderDate", "orderNumber";

-- Q12. Show product vendor list
SELECT DISTINCT
  "productVendor"
FROM products
ORDER BY "productVendor";

-- Q13. Get all product codes
SELECT
  "productCode"
FROM products
ORDER BY "productCode";

-- Q14. List all countries from offices
SELECT DISTINCT
  "country"
FROM offices
ORDER BY "country";

-- Q15. Show all order statuses
SELECT DISTINCT
  "status"
FROM orders
ORDER BY "status";

-- Q16. Get all payment amounts
SELECT
  "customerNumber",
  "checkNumber",
  "amount"
FROM payments
ORDER BY "customerNumber", "checkNumber";

-- Q17. List all job titles
SELECT DISTINCT
  "jobTitle"
FROM employees
ORDER BY "jobTitle";

-- Q18. Get customer phone numbers
SELECT
  "customerName",
  "phone"
FROM customers
ORDER BY "customerName";

-- Q19. Show product MSRP values
SELECT
  "productName",
  "MSRP"
FROM products
ORDER BY "productName";

-- Q20. List order numbers
SELECT
  "orderNumber"
FROM orders
ORDER BY "orderNumber";

-- Q21. Get orders with customer names
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName"
FROM orders AS o
JOIN customers AS c
  ON o."customerNumber" = c."customerNumber"
ORDER BY o."orderNumber";

-- Q22. Get employees with office city
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  o."city" AS "officeCity"
FROM employees AS e
JOIN offices AS o
  ON e."officeCode" = o."officeCode"
ORDER BY e."employeeNumber";

-- Q23. Get payments with customer names
SELECT
  p."customerNumber",
  c."customerName",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON p."customerNumber" = c."customerNumber"
ORDER BY p."customerNumber", p."checkNumber";

-- Q24. Get order details with product names
SELECT
  od."orderNumber",
  od."productCode",
  p."productName",
  od."quantityOrdered",
  od."priceEach"
FROM orderdetails AS od
JOIN products AS p
  ON od."productCode" = p."productCode"
ORDER BY od."orderNumber", od."orderLineNumber";

-- Q25. Get products with product line description
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  pl."textDescription"
FROM products AS p
JOIN productlines AS pl
  ON p."productLine" = pl."productLine"
ORDER BY p."productCode";

-- Q26. Get customers with sales rep names
SELECT
  c."customerNumber",
  c."customerName",
  e."firstName" AS "salesRepFirstName",
  e."lastName" AS "salesRepLastName"
FROM customers AS c
LEFT JOIN employees AS e
  ON c."salesRepEmployeeNumber" = e."employeeNumber"
ORDER BY c."customerNumber";

-- Q27. Get orders with customer city
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."city"
FROM orders AS o
JOIN customers AS c
  ON o."customerNumber" = c."customerNumber"
ORDER BY o."orderNumber";

-- Q28. Get employees and their manager
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  m."firstName" AS "managerFirstName",
  m."lastName" AS "managerLastName"
FROM employees AS e
LEFT JOIN employees AS m
  ON e."reportsTo" = m."employeeNumber"
ORDER BY e."employeeNumber";

-- Q29. Get orderdetails with product vendor
SELECT
  od."orderNumber",
  od."productCode",
  p."productVendor",
  od."quantityOrdered",
  od."priceEach"
FROM orderdetails AS od
JOIN products AS p
  ON od."productCode" = p."productCode"
ORDER BY od."orderNumber", od."orderLineNumber";

-- Q30. Get payments with customer country
SELECT
  p."customerNumber",
  c."customerName",
  c."country",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON p."customerNumber" = c."customerNumber"
ORDER BY p."customerNumber", p."checkNumber";

-- Q31. Count customers per country
SELECT
  "country",
  COUNT(*) AS "customerCount"
FROM customers
GROUP BY "country"
ORDER BY "country";

-- Q32. Total payments per customer
SELECT
  c."customerNumber",
  c."customerName",
  SUM(p."amount") AS "totalPayments"
FROM customers AS c
JOIN payments AS p
  ON c."customerNumber" = p."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY c."customerNumber";

-- Q33. Number of orders per status
SELECT
  "status",
  COUNT(*) AS "orderCount"
FROM orders
GROUP BY "status"
ORDER BY "status";

-- Q34. Products per product line
SELECT
  "productLine",
  COUNT(*) AS "productCount"
FROM products
GROUP BY "productLine"
ORDER BY "productLine";

-- Q35. Employees per office
SELECT
  o."officeCode",
  o."city",
  COUNT(e."employeeNumber") AS "employeeCount"
FROM offices AS o
LEFT JOIN employees AS e
  ON o."officeCode" = e."officeCode"
GROUP BY o."officeCode", o."city"
ORDER BY o."officeCode";

-- Q36. Total stock per product vendor
SELECT
  "productVendor",
  SUM("quantityInStock") AS "totalQuantityInStock"
FROM products
GROUP BY "productVendor"
ORDER BY "productVendor";

-- Q37. Average buy price per product line
SELECT
  "productLine",
  ROUND(AVG("buyPrice"), 2) AS "averageBuyPrice"
FROM products
GROUP BY "productLine"
ORDER BY "productLine";

-- Q38. Orders per customer
SELECT
  c."customerNumber",
  c."customerName",
  COUNT(o."orderNumber") AS "orderCount"
FROM customers AS c
LEFT JOIN orders AS o
  ON c."customerNumber" = o."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY c."customerNumber";

-- Q39. Max MSRP per product line
SELECT
  "productLine",
  MAX("MSRP") AS "maxMSRP"
FROM products
GROUP BY "productLine"
ORDER BY "productLine";

-- Q40. Min buy price per vendor
SELECT
  "productVendor",
  MIN("buyPrice") AS "minBuyPrice"
FROM products
GROUP BY "productVendor"
ORDER BY "productVendor";

-- Q41. Total number of customers
SELECT COUNT(*) AS "totalCustomers"
FROM customers;

-- Q42. Total number of products
SELECT COUNT(*) AS "totalProducts"
FROM products;

-- Q43. Total revenue from payments
SELECT SUM("amount") AS "totalRevenue"
FROM payments;

-- Q44. Average product price
SELECT ROUND(AVG("buyPrice"), 2) AS "averageProductBuyPrice"
FROM products;

-- Q45. Max payment amount
SELECT MAX("amount") AS "maxPaymentAmount"
FROM payments;

-- Q46. Min payment amount
SELECT MIN("amount") AS "minPaymentAmount"
FROM payments;

-- Q47. Count total orders
SELECT COUNT(*) AS "totalOrders"
FROM orders;

-- Q48. Total quantity in stock
SELECT SUM("quantityInStock") AS "totalQuantityInStock"
FROM products;

-- Q49. Average MSRP
SELECT ROUND(AVG("MSRP"), 2) AS "averageMSRP"
FROM products;

-- Q50. Number of employees
SELECT COUNT(*) AS "totalEmployees"
FROM employees;
