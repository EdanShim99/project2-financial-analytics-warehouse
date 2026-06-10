WITH digits AS (
    SELECT 0 AS n
    UNION ALL
    SELECT 1
    UNION ALL
    SELECT 2
    UNION ALL
    SELECT 3
    UNION ALL
    SELECT 4
    UNION ALL
    SELECT 5
    UNION ALL
    SELECT 6
    UNION ALL
    SELECT 7
    UNION ALL
    SELECT 8
    UNION ALL
    SELECT 9
),

numbers AS (
    SELECT
        p0.n + p1.n * 10 + p2.n * 100 + p3.n * 1000 AS n
    FROM digits AS p0
    CROSS JOIN digits AS p1
    CROSS JOIN digits AS p2
    CROSS JOIN digits AS p3
    WHERE
        p0.n + p1.n * 10 + p2.n * 100 + p3.n * 1000
        < 3650
),

date_spine AS (
    SELECT
        (DATE '2020-01-01' + n)::DATE AS date_day
    FROM numbers
)

SELECT
    date_day,
    EXTRACT(YEAR FROM date_day)::INT AS date_year,
    EXTRACT(MONTH FROM date_day)::INT AS date_month,
    EXTRACT(DAY FROM date_day)::INT AS day_of_month,
    EXTRACT(DOW FROM date_day)::INT AS day_of_week,
    EXTRACT(QUARTER FROM date_day)::INT AS date_quarter,
    TO_CHAR(date_day, 'Day') AS day_name,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DOW FROM date_day) IN (0, 6) AS is_weekend,
    EXTRACT(DOW FROM date_day) NOT IN (0, 6)
        AS is_trading_day
FROM date_spine