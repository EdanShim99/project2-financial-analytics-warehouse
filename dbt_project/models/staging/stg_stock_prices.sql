WITH source AS (
    SELECT * FROM {{ source('staging', 'stock_prices') }}
),

deduplicated AS (
    SELECT
        symbol,
        date AS trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, date
            ORDER BY loaded_at DESC
        ) AS rn
    FROM source
)

SELECT
    symbol,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    loaded_at
FROM deduplicated
WHERE rn = 1