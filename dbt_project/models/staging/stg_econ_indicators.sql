WITH source AS (
    SELECT * FROM {{ source('staging', 'econ_indicators') }}
),

deduplicated AS (
    SELECT
        series_id,
        date AS observation_date,
        value AS observation_value,
        loaded_at,
        ROW_NUMBER() OVER (
            PARTITION BY series_id, date
            ORDER BY loaded_at DESC
        ) AS rn
    FROM source
)

SELECT
    series_id,
    observation_date,
    observation_value,
    loaded_at
FROM deduplicated
WHERE rn = 1