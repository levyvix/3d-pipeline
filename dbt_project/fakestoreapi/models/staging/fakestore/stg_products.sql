select
    id as product_id,

    title as product_name,
    price as product_price,
    description as product_description,
    category as product_category,
    image as product_image_url,
    rating__rate as product_rating,
    rating__count as product_rating_count

from {{source('fakestore', 'products')}}
