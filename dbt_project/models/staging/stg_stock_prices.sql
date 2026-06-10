with source as (
    select * from {{ source('staging', 'stock_prices') }}
),

deduplicated as (
    select
        symbol,
        date as trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        loaded_at,
        row_number() over (partition by symbol, date order by loaded_at desc) as rn
    from source
)

select
    symbol,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    loaded_at
from deduplicated
where rn = 1
