WITH company_history AS (
    SELECT * FROM {{ ref('snap_company') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(
        ['symbol', 'dbt_valid_from']
    ) }} AS company_key,
    symbol,
    company_name,
    sector,
    industry,
    market_cap_tier,
    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,
    dbt_valid_to IS NULL AS is_current
FROM company_history