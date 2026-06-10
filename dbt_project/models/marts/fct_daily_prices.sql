{{
    config(
        materialized='incremental',
        unique_key=['symbol', 'trade_date']
    )
}}

WITH prices AS (
    SELECT *
    FROM {{ ref('stg_stock_prices') }}
    {% if is_incremental() %}
        WHERE stg.trade_date >= (
            SELECT
                DATEADD(
                    DAY, -30, MAX(prev.trade_date)
                )
            FROM {{ this }} AS prev
        )
    {% endif %}
),

calculated AS (
    SELECT
        symbol,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        close_price - open_price AS daily_change,
        ROUND(
            (close_price - open_price)
            / NULLIF(open_price, 0) * 100,
            4
        ) AS daily_return_pct,
        close_price - LAG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        ) AS price_change_from_prev,
        AVG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING
            AND CURRENT ROW
        ) AS moving_avg_5d,
        AVG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING
            AND CURRENT ROW
        ) AS moving_avg_20d
    FROM prices
)

SELECT * FROM calculated
{% if is_incremental() %}
    WHERE calculated.trade_date > (
        SELECT MAX(prev.trade_date)
        FROM {{ this }} AS prev
    )
{% endif %}
