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

from {{source('fakestore', 'users')}}