ADD_PAYMENT_ENTRIES = '''
INSERT INTO public.payment_entry(ae_period, ae_no, acpl_account_debit, acpl_subaccount_debit, acpl_code_analitic_debit, acpl_code_analitic_debit_1, acpl_code_analitic_debit_2, acpl_add_sign_debit,  
					acpl_account_credit, acpl_subaccount_credit, acpl_code_analitic_credit, acpl_code_analitic_credit_1, acpl_code_analitic_credit_2, acpl_add_sign_credit, ae_sum, payment_prepayment_id)
SELECT 
	payment.create_date as ae_period,
	p.report_accounting_num::integer as ae_no, -- Номер бухгалтерской справки

	SUBSTRING(LPAD(p.imprest_account_id::text, 4, '0'), 0, 3)::integer as acpl_account_debit, -- Дебет/счет
	SUBSTRING(LPAD(p.imprest_account_id::text, 4, '0'), 3, 3)::integer as acpl_subaccount_debit, -- Дебет/субсчет
	'000' || LPAD(coalesce(p.emp_div_num::text, ''), 3, '0') as acpl_code_analitic_debit, -- Дебет/КАУ
	'000' as acpl_code_analitic_debit_1, -- Дебет/КАУ1
	LPAD(coalesce(p.emp_div_num::text, ''), 3, '0') as acpl_code_analitic_debit_2, -- Дебет/КАУ2
	LPAD(coalesce(p.emp_num::text, ''), 8, '0') as acpl_add_sign_debit, -- Дебет/счет/ДП

	om.credit_account::integer as acpl_account_credit, -- Кредит/счет
	om.credit_subaccount::integer as acpl_subaccount_credit, -- Кредит/субсчет
	coalesce(om.credit_kau_1, '') || coalesce(om.credit_kau_2, '') as acpl_code_analitic_credit, -- Кредит/КАУ
	coalesce(om.credit_kau_1, '') as acpl_code_analitic_credit_1, -- Кредит/КАУ1
	coalesce(om.credit_kau_2, '') as acpl_code_analitic_credit_2, -- Кредит/КАУ2
	coalesce(om.credit_extra, '') as acpl_add_sign_credit, -- Кредит/счет/ДП

	item.value as ae_sum, -- Сумма
	pp.id
FROM payment_prepayment pp
INNER JOIN prepayment_item item ON item.id = pp.prepayment_item_id
INNER JOIN prepayment p ON p.id = item.prepayment_id
INNER JOIN obtain_method om ON om.id = item.obtain_method_id
INNER JOIN payment ON payment.id = pp.payment_id
WHERE payment.create_date IS NOT NULL 
	AND p.report_accounting_num IS NOT NULL 
	AND p.imprest_account_id IS NOT NULL 
	AND om.credit_kau_1 IS NOT NULL 
	AND om.credit_kau_2 IS NOT NULL 
	AND payment.id in %s'''