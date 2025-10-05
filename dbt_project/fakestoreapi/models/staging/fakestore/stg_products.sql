with source_data as (
    select
        id,
        title,
        price,
        description,
        category,
        image,
        rating__rate,
        rating__count,
        _dlt_load_id,
        row_number() over (partition by id order by _dlt_load_id desc) as rn
    from {{source('fakestore', 'products')}}
),

deduplicated as (
    select * from source_data
    where rn = 1
)

select
    id as product_id,
    title as product_name,
    price as product_price,
    description as product_description,
    category as product_category,
    image as product_image_url,
    rating__rate as product_rating,
    rating__count as product_rating_count
from deduplicated
