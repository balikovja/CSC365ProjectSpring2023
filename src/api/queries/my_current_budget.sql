WITH spending AS (
	SELECT t.category_id, b.id AS budget_id, sum(t.amount) AS category_spent
	FROM transactions AS t
	JOIN budgets AS b
		ON b.category_id = t.category_id
		AND b.user_id = t.user_id
		AND t.transaction_date BETWEEN b.start_date AND b.end_date
	WHERE t.user_id = (:quserid)
	AND t.transaction_date BETWEEN b.start_date AND b.end_date
	GROUP BY t.category_id, b.id
)
SELECT c.name, b.budget_amount, s.category_spent, b.start_date, b.end_date, p.name AS period_text
FROM categories AS c
LEFT JOIN budgets AS b ON b.category_id = c.id
	AND (:qcurrent_date) BETWEEN b.start_date AND b.end_date
LEFT JOIN period_types AS p ON p.id = b.period_type_id
LEFT JOIN spending AS s ON s.budget_id = b.id
ORDER BY c.name