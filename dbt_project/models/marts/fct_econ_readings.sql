{{
    config(
        materialized='incremental',
        unique_key=['series_id', 'observation_date']
    )
}}

WITH indicators AS (
    SELECT *
    FROM {{ ref('stg_econ_indicators') }}
    {% if is_incremental() %}
        WHERE stg.observation_date >= (
            SELECT
                DATEADD(
                    DAY, -7, MAX(prev.observation_date)
                )
            FROM {{ this }} AS prev
        )
    {% endif %}
),

calculated AS (
    SELECT
        series_id,
        observation_date,
        observation_value,
        LAG(observation_value) OVER (
            PARTITION BY series_id
            ORDER BY observation_date
        ) AS prev_value,
        observation_value - LAG(observation_value)
            OVER (
                PARTITION BY series_id
                ORDER BY observation_date
            )
            AS change_from_prev,
        ROUND(
            (observation_value - LAG(
                observation_value
            ) OVER (
                PARTITION BY series_id
                ORDER BY observation_date
            ))
            / NULLIF(
                LAG(observation_value) OVER (
                    PARTITION BY series_id
                    ORDER BY observation_date
                ), 0
            ) * 100,
            4
        ) AS pct_change_from_prev
    FROM indicators
)

SELECT * FROM calculated
{% if is_incremental() %}
    WHERE calculated.observation_date > (
        SELECT MAX(prev.observation_date)
        FROM {{ this }} AS prev
    )
{% endif %}
