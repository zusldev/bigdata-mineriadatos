# DATA_DICTIONARY

Diccionario inferido desde tablas limpias canónicas.

## sales
| Columna | Tipo inferido | % Nulos |
|---|---|---:|
| `ticket_id` | `string` | 0.00% |
| `date` | `datetime64[ns]` | 0.00% |
| `time` | `object` | 0.00% |
| `day_of_week` | `string` | 0.00% |
| `month` | `string` | 0.00% |
| `branch_id` | `string` | 0.00% |
| `branch_name` | `string` | 0.00% |
| `city` | `string` | 0.00% |
| `dish` | `string` | 0.00% |
| `category` | `string` | 0.00% |
| `unit_price` | `int64` | 0.00% |
| `quantity` | `int64` | 0.00% |
| `total_sale` | `int64` | 0.00% |
| `ingredient_cost` | `int64` | 0.00% |
| `gross_margin` | `int64` | 0.00% |
| `payment_method` | `object` | 0.00% |
| `tip` | `float64` | 0.00% |
| `total_with_tip` | `float64` | 0.00% |
| `hour` | `int32` | 0.00% |
| `year_month` | `object` | 0.00% |
| `daypart` | `object` | 0.00% |

## customers
| Columna | Tipo inferido | % Nulos |
|---|---|---:|
| `customer_id` | `string` | 0.00% |
| `name` | `string` | 0.00% |
| `register_date` | `datetime64[ns]` | 0.00% |
| `loyalty_member` | `bool` | 0.00% |
| `customer_category` | `string` | 0.00% |
| `preferred_branch` | `string` | 0.00% |
| `preferred_city` | `string` | 0.00% |
| `visits_last_year` | `int64` | 0.00% |
| `avg_spend` | `float64` | 0.00% |
| `estimated_total_spend` | `float64` | 0.00% |
| `loyalty_points` | `float64` | 0.00% |
| `last_visit` | `datetime64[ns]` | 0.00% |
| `satisfaction_score` | `int64` | 0.00% |
| `nps_score` | `int64` | 0.00% |
| `survey_comment` | `string` | 0.00% |
| `acquisition_channel` | `string` | 0.00% |
| `accepts_promotions` | `bool` | 0.00% |

## branches
| Columna | Tipo inferido | % Nulos |
|---|---|---:|
| `branch_id` | `string` | 0.00% |
| `branch_name` | `string` | 0.00% |
| `city` | `string` | 0.00% |
| `address` | `string` | 0.00% |
| `postal_code` | `string` | 0.00% |
| `zone` | `string` | 0.00% |
| `socioeconomic_level` | `string` | 0.00% |
| `capacity_people` | `int64` | 0.00% |
| `num_employees` | `int64` | 0.00% |
| `open_time` | `string` | 0.00% |
| `close_time` | `string` | 0.00% |
| `peak_hours` | `string` | 0.00% |
| `rent_monthly` | `float64` | 0.00% |
| `utilities_monthly` | `float64` | 0.00% |
| `payroll_monthly` | `float64` | 0.00% |
| `operational_cost_total` | `float64` | 0.00% |
| `avg_monthly_income` | `float64` | 0.00% |
| `operating_margin` | `float64` | 0.00% |
| `profitability_pct` | `float64` | 0.00% |
| `nearby_poi` | `string` | 0.00% |
| `nearby_competitors` | `int64` | 0.00% |
| `parking` | `string` | 0.00% |
| `opening_year` | `float64` | 0.00% |
| `years_operating` | `int64` | 0.00% |

## inventory
| Columna | Tipo inferido | % Nulos |
|---|---|---:|
| `record_id` | `string` | 0.00% |
| `date` | `datetime64[ns]` | 0.00% |
| `month` | `string` | 0.00% |
| `branch_id` | `string` | 0.00% |
| `branch_name` | `string` | 0.00% |
| `city` | `string` | 0.00% |
| `ingredient` | `string` | 0.00% |
| `ingredient_category` | `string` | 0.00% |
| `unit` | `string` | 0.00% |
| `supplier` | `string` | 0.00% |
| `qty_ordered` | `int64` | 0.00% |
| `unit_price` | `float64` | 0.00% |
| `total_purchase_cost` | `float64` | 0.00% |
| `qty_wasted` | `float64` | 0.00% |
| `waste_cost` | `float64` | 0.00% |
| `waste_pct` | `float64` | 0.00% |
| `waste_reason` | `string` | 0.00% |
| `current_stock` | `float64` | 0.00% |
| `min_stock` | `float64` | 0.00% |
| `stock_status` | `string` | 0.00% |
| `needs_reorder` | `bool` | 0.00% |
| `reorder_frequency` | `string` | 0.00% |
| `shelf_life_days` | `int64` | 0.00% |
| `year_month` | `object` | 0.00% |

## digital
| Columna | Tipo inferido | % Nulos |
|---|---|---:|
| `record_id` | `string` | 0.00% |
| `date` | `datetime64[ns]` | 0.00% |
| `month` | `string` | 0.00% |
| `day_of_week` | `string` | 0.00% |
| `branch_id` | `string` | 0.00% |
| `branch_name` | `string` | 0.00% |
| `city` | `string` | 0.00% |
| `platform` | `string` | 0.00% |
| `interaction_type` | `string` | 0.00% |
| `content` | `string` | 0.00% |
| `sentiment` | `object` | 0.00% |
| `rating` | `float64` | 61.50% |
| `reach` | `float64` | 0.00% |
| `engagement` | `float64` | 0.00% |
| `engagement_rate` | `float64` | 0.00% |
| `campaign` | `string` | 0.00% |
| `campaign_cost` | `float64` | 0.00% |
| `responded` | `object` | 90.08% |
| `response_hours` | `float64` | 92.25% |
| `conversion` | `bool` | 0.00% |
| `year_month` | `object` | 0.00% |
