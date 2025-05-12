var csrftoken = Cookies.get('csrftoken');

dayjs.locale('ru')
dayjs.extend(window.dayjs_plugin_customParseFormat);

function editColumn(path, predicate) {
	return ({
		data: null,
		defaultContent: '',
		orderable: false,
		searchable: false,
		className: 'text-center align-middle px-1',
		render: function (data, type, row) {
			if (!predicate || predicate(data))
				return `<a href="${path}/${data.id}" class="text-success m-0"><i class="fa-light fa-pencil fa-xl"></i></a>`
			return ''
		}	
	})
}

function deleteColumn(path, predicate, confirmText = 'Удалить?') {
	return ({
		data: null,
		defaultContent: '',
		orderable: false,
		searchable: false,
		className: 'text-center align-middle px-1',
		render: function (data, type, row) {
			return `<a href="${path}/${data.id}/delete" class="text-danger m-0" onclick="return confirm('${confirmText}');"><i class="fa-light fa-trash fa-xl"></i></a>`
		}
	})
}

function deleteColumnPost(path, confirmText = 'Удалить?') {
	return ({
		data: null,
		defaultContent: '',
		orderable: false,
		searchable: false,
		className: 'text-center align-middle p-0',
		render: function (data, type, row) {
			return `<form action="${path}/${data.id}/delete" method="post">
						<input type='hidden' name='csrfmiddlewaretoken' value='${csrftoken}'/>
						<button type='submit' class="text-danger h4 m-0 bg-transparent border-0" onclick="return confirm('${confirmText}');">
							<i class="fa-light fa-trash"></i>
						</button>
					</form>`
		}
	})
}

$.extend(true, $.fn.dataTable.defaults, {
	ajax: {
		headers: {'X-CSRFToken': csrftoken}
	},
	language: {
        url: '/static/main/json/ru.json',
    },
	searching: true,
	ordering: true,
	processing: true,
	serverSide: true,
	stateSave: true,
	fixedHeader: true,
	select: {info: false, style: 'single'},
	pagingType: 'first_last_numbers',
	dom: '<"row"<"toolbar col-sm-12 col-md-4"B><"filters col-sm-12 col-md-6"><"col-sm-12 col-md-2"fb>>'
		+ '<"row"<"col-sm-12"tr>>'
		+ '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-4"l><"col-sm-12 col-md-3"p>>'
});

$.datepicker.setDefaults( $.datepicker.regional[ "ru" ] )

$.fn.select2.defaults.set("theme", "bootstrap-5");

function stringDif (val1, val2) {
	if (val1 == null || val2 == null || val1.trim() == '' || val2.trim() == '')
		return null;
	let valNum1 = Number(val1.replace(',','.').replace(' ',''))
	let valNum2 = Number(val2.replace(',','.').replace(' ',''))
	if (Number.isNaN(valNum1) || Number.isNaN(valNum2))
		return null
	return (valNum1 - valNum2).toFixed(2)
}

function parseDate(dateString) {
	if (!dateString) return null;
    const parts = dateString.split('.');
    if (parts.length !== 3) {
        return null
    }
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Months are 0-based in JavaScript
    const year = parseInt(parts[2], 10);
    return new Date(year, month, day);
}