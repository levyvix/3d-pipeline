{% test expression_is_true(model, column_name, expression, config={}) %}

{% set where_clause = config.get('where', '') %}

select *
from {{ model }}
where not ({{ column_name }} {{ expression }})
{% if where_clause %}
  and {{ where_clause }}
{% endif %}

{% endtest %}
