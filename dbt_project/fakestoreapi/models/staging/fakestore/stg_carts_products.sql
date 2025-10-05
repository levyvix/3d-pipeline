select
    product_id,
    quantity as product_quantity,
    _dlt_parent_id as cart_id
from {{source('fakestore', 'carts__products')}}
