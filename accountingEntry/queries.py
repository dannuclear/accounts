GET_EXPENSE_CODES_REPORT = '''
	SELECT 
		entity.expense_code_id as id, 
		SUM(
		CASE 
			WHEN entity.expense_code_id = '01' THEN CASE WHEN entity.debit_account IN (2000, 2302) THEN entity.accounting_sum ELSE 0 END
			WHEN entity.expense_code_id IN ('00', '16', '69', '30') THEN CASE WHEN entity.debit_account IN (2300, 2551, 2552, 2553, 2600, 2908, 2909, 4403, 4410) THEN entity.accounting_sum ELSE 0 END
			WHEN entity.expense_code_id = '91' THEN CASE WHEN entity.debit_account IN (9120, 9122) THEN entity.accounting_sum ELSE 0 END
		ELSE 0 END) as sm,
		COUNT(DISTINCT item.prepayment_id) as cnt,
		SUM(item.days_count) as days
	FROM advance_report_item_entity entity
	INNER JOIN advance_report_item item ON item.id = entity.advance_report_item_id
	INNER JOIN prepayment p ON p.id = item.prepayment_id
	WHERE expense_code_id IS NOT NULL AND COALESCE(entity.approve_date, p.approve_date) BETWEEN COALESCE(%s::date, '01.01.1970') AND COALESCE(%s::date, now())
	GROUP BY expense_code_id'''