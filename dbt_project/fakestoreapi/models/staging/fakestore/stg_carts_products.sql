with latest_carts as (
    select
        _dlt_id,
        row_number() over (partition by id order by _dlt_load_id desc) as rn
    from {{source('fakestore', 'carts')}}
),

latest_cart_ids as (
    select _dlt_id
    from latest_carts
    where rn = 1
)

select
    product_id,
    quantity as product_quantity,
    _dlt_parent_id as cart_id
from {{source('fakestore', 'carts__products')}}
where _dlt_parent_id in (select _dlt_id from latest_cart_ids)
