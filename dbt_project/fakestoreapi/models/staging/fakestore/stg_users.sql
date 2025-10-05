with source_data as (
    select
        id,
        name__firstname,
        name__lastname,
        email,
        phone,
        username,
        address__geolocation__lat,
        address__geolocation__long,
        address__city,
        address__street,
        address__number,
        address__zipcode,
        _dlt_load_id,
        row_number() over (partition by id order by _dlt_load_id desc) as rn
    from {{source('fakestore', 'users')}}
),

deduplicated as (
    select * from source_data
    where rn = 1
)

select
    -- id
    id as user_id,

    -- personal information
    name__firstname as first_name,
    name__lastname as last_name,
    email as email,
    phone as phone_number,
    username as username,

    -- address information
    address__geolocation__lat as latitude,
    address__geolocation__long as longitude,
    address__city as city,
    address__street as street,
    address__number as house_number,
    address__zipcode as zipcode

from deduplicated