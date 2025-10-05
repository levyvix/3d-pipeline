with source_data as (
    select
        id,
        user_id,
        date,
        _dlt_id,
        _dlt_load_id,
        row_number() over (partition by id order by _dlt_load_id desc) as rn
    from {{source('fakestore', 'carts')}}
),

deduplicated as (
    select * from source_data
    where rn = 1
)

select
    id as cart_id,
    user_id,
    date::timestamp as ordered_at,
    _dlt_id as dlt_cart_id
from deduplicated
