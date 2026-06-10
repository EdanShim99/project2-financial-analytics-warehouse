with source as (
    select * from {{ source('staging', 'econ_indicators') }}
),

deduplicated as (
    select
        series_id,
        date as observation_date,
        value as observation_value,
        loaded_at,
        row_number() over (partition by series_id, date order by loaded_at desc) as rn
    from source
)

select
    series_id,
    observation_date,
    observation_value,
    loaded_at
from deduplicated
where rn = 1
