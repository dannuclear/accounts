ADD_FACTS = '''INSERT INTO public.fact(xv26ei_id, pd_id, pd_source, prepayment_id, sum_delta, sum_fact)
SELECT * FROM (SELECT 
	CASE WHEN (entity.debit_account IN (2300, 2551, 2553, 2600, 2908, 2909, 4403, 4410)) AND 
		(entity.debit_expense_item IN (465, 466, 467, 468, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481)) THEN entity.dept_expense::smallint
	ELSE COALESCE(int_p.xv26ei_id, wc07p_order.estimate_id) END as xv26ei_id,
	p.integration_prepayment_id,
	1,
	p.id,
	coalesce(distrib_carryover, 0),
	coalesce(accounting_sum, 0)
FROM prepayment p
LEFT JOIN integration_prepayment int_p ON int_p.pd_id = p.integration_prepayment_id
LEFT JOIN wc07p_order ON wc07p_order.order_id  = p.order_id
INNER JOIN advance_report_item item ON (item.prepayment_id = p.id AND item.item_type = 0)
INNER JOIN advance_report_item_entity entity ON entity.advance_report_item_id = item.id WHERE p.id = %s) t1 WHERE xv26ei_id IS NOT NULL'''

ADD_ACCOUNTING_ENTRIES = '''
INSERT INTO public.accounting_entry(ae_period, ae_no, acpl_account_debit, acpl_subaccount_debit, acpl_code_analitic_debit, acpl_code_analitic_debit_1, acpl_code_analitic_debit_2, acpl_add_sign_debit,  
					acpl_account_credit, acpl_subaccount_credit, acpl_code_analitic_credit, acpl_code_analitic_credit_1, acpl_code_analitic_credit_2, acpl_add_sign_credit, ae_sum, prepayment_id)
SELECT 
	p.approve_date as ae_period,
	p.report_accounting_num::integer as ae_no, -- Номер бухгалтерской справки

	SUBSTRING(LPAD(entity.debit_account::text, 4, '0'), 0, 3)::integer as acpl_account_debit, -- Дебет/счет
	SUBSTRING(LPAD(entity.debit_account::text, 4, '0'), 3, 3)::integer as acpl_subaccount_debit, -- Дебет/субсчет
	LPAD(coalesce(entity.debit_kau_1::text, ''), 3, '0') || LPAD(coalesce(entity.debit_kau_2::text, ''), 3, '0') as acpl_code_analitic_debit, -- Дебет/КАУ
	entity.debit_kau_1 as acpl_code_analitic_debit_1, -- Дебет/КАУ1
	entity.debit_kau_2 as acpl_code_analitic_debit_2, -- Дебет/КАУ2
	entity.debit_extra as acpl_add_sign_debit, -- Дебет/счет/ДП

	SUBSTRING(LPAD(entity.credit_account::text, 4, '0'), 0, 3)::integer as acpl_account_credit, -- Кредит/счет
	SUBSTRING(LPAD(entity.credit_account::text, 4, '0'), 3, 3)::integer as acpl_subaccount_credit, -- Кредит/субсчет
	LPAD(coalesce(entity.credit_kau_1::text, ''), 3, '0') || LPAD(coalesce(entity.credit_kau_2::text, ''), 3, '0') as acpl_code_analitic_credit, -- Кредит/КАУ
	entity.credit_kau_1 as acpl_code_analitic_credit_1, -- Кредит/КАУ1
	entity.credit_kau_2 as acpl_code_analitic_credit_2, -- Кредит/КАУ2
	entity.credit_extra as acpl_add_sign_credit, -- Кредит/счет/ДП
	entity.accounting_sum as ae_sum, -- Сумма
	p.id
FROM prepayment p
INNER JOIN advance_report_item item ON item.prepayment_id = p.id
INNER JOIN advance_report_item_entity entity ON entity.advance_report_item_id = item.id 
WHERE 	p.approve_date IS NOT NULL 
	AND p.report_accounting_num IS NOT NULL 
	AND entity.debit_kau_1 IS NOT NULL 
	AND entity.debit_kau_2 IS NOT NULL 
	AND entity.credit_kau_1 IS NOT NULL 
	AND entity.credit_kau_2 IS NOT NULL 
	AND entity.credit_extra IS NOT NULL 
	AND entity.debit_extra IS NOT NULL 
	AND p.id = %s'''

GET_ADVANCE_REPORT_ITEMS_FOR_REPORT = '''
	SELECT 
		item.id, 
		approve_doc_num, 
		approve_doc_date,
		expense_sum_currency,
		expense_sum_rub,
		expense_sum_vat,
		coalesce(document.name, '') ||
		CASE item.item_type
			WHEN 0 THEN
				' ' || coalesce(item.nomenclature, '')
		ELSE '' END || ' ' || coalesce(expense_category.print_name, '') as expense_doc_name
	FROM advance_report_item item 
	LEFT JOIN document ON item.approve_document_id = document.id
	LEFT JOIN expense_category ON item.expense_category_id = expense_category.id
	WHERE item.prepayment_id = %s and item.item_type = ANY(%s)'''

GET_ACCOUNTING_CERT_ROW = '''
	SELECT debit_account, debit_extra, credit_account, credit_extra, sum (accounting_sum) FROM (
	SELECT
		coalesce(entity.debit_account::text, '') || ' ' ||
		CASE item.item_type
			WHEN 0 THEN
				LPAD(coalesce(debit_expense_item::text, ''), 3, '0') || ' ' || LPAD(coalesce(debit_expense_workshop::text, ''), 3, '0')
			WHEN 5 THEN
				LPAD(coalesce(debit_expense_item::text, ''), 3, '0') || ' ' || LPAD(coalesce(debit_expense_workshop::text, ''), 3, '0')
		ELSE LPAD(coalesce(debit_kau_1::text, ''), 3, '0') || ' ' || LPAD(coalesce(debit_kau_2::text, ''), 3, '0') END as debit_account,
		entity.debit_extra as debit_extra,
		coalesce(entity.credit_account::text, '') || ' ' ||
		CASE item.item_type
			WHEN 0 THEN
				coalesce(credit_expense_item::text, '') || ' ' || coalesce(credit_dept::text, '')
			WHEN 5 THEN
				coalesce(credit_expense_item::text, '') || ' ' || coalesce(credit_dept::text, '')
		ELSE LPAD(coalesce(credit_kau_1::text, ''), 3, '0') || ' ' || LPAD(coalesce(credit_kau_1::text, ''), 3, '0') END as credit_account,
		entity.credit_extra as credit_extra,
		entity.accounting_sum as accounting_sum
	FROM advance_report_item_entity entity
	INNER JOIN advance_report_item item ON item.id = entity.advance_report_item_id
	WHERE item.prepayment_id = %s) t1 GROUP BY debit_account, debit_extra, credit_account, credit_extra'''