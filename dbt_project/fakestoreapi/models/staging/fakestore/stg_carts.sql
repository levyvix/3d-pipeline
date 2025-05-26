select
    id as cart_id,
    user_id,
    date::timestamp as ordered_at,
    _dlt_id as dlt_cart_id
from {{source('fakestore', 'carts')}}