insert into budgets (user_id, budget_amount, category_id, start_date, end_date, period_type_id)

select * from (
select user_id, budget_amount, category_id,
date(new_start_date) as new_start_date,
date(new_start_date + p.period - interval '1 day') as new_end_date,
period_type_id
from (
	select user_id, budget_amount, category_id,
	end_date + interval '1 day' as new_start_date,
	period_type_id,
	-- Row number to select most recent for each category
	ROW_NUMBER() over (partition by category_id order by end_date desc) as row_num
	from budgets
	where user_id = (:quser_id)
) as a
join period_types as p on p.id = period_type_id
-- Only copy budgets that will appear in current period unless overridden
where row_num = 1
) as a2
where (:qcopy_override) = 1 or (:qcurrent_date) between new_start_date and new_end_date

returning id;
