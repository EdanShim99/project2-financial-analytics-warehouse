{% snapshot snap_company %}

{{
    config(
        target_schema='analytics',
        unique_key='symbol',
        strategy='check',
        check_cols=['company_name', 'sector', 'industry', 'market_cap_tier']
    )
}}

SELECT * FROM {{ ref('companies') }}

{% endsnapshot %}