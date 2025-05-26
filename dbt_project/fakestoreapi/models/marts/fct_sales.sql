with carts as (
    select * from {{ ref('stg_carts') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
carts_products as (
    select * from {{ ref('stg_carts_products') }}
),
joined as (
    select 
        carts.dlt_cart_id as cart_id,
        carts.user_id as user_id,
        products.product_id as product_id,
        carts.ordered_at as ordered_at,
        products.product_price as product_price,
        carts_products.product_quantity as product_quantity,
        carts_products.product_quantity * products.product_price as total_price
    from carts_products
    left join carts on carts.dlt_cart_id = carts_products.cart_id
    left join products on products.product_id = carts_products.product_id
)

select * from joined