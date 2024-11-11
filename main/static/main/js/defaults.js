var csrftoken = Cookies.get('csrftoken');

const defaultLang = {
	info: 'Страница _PAGE_ из _PAGES_',
	lengthMenu: 'На странице _MENU_',
	zeroRecords: 'Сотрудников не найдено',
	infoEmpty: 'Не найдено',
	search: 'Поиск',
	processing: 'Загрузка...',
	loadingRecords: 'Загрузка...',
	paginate: {
	  first: '|<',
	  last: '>|',
	  next: '>',
	  previous: '<'
	}
  }

$.extend(true, $.fn.dataTable.defaults, {
	ajax: {
		//type: 'POST',
		// contentType: 'application/json',
		// data: function(d) {
		// 	return JSON.stringify(d);
		// },
		headers: {'X-CSRFToken': csrftoken}
	},
	language: {
        url: '/static/main/json/ru.json',
    },
	searching: true,
	ordering: true,
	processing: true,
	serverSide: true,
	pagingType: 'first_last_numbers',
	dom: '<"row"<"toolbar col-sm-12 col-md-4"B><"filters col-sm-12 col-md-4"><"col-sm-12 col-md-4"fb>>'
		+ '<"row"<"col-sm-12"tr>>'
		+ '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-2"l><"col-sm-12 col-md-5"p>>'
});

$.datepicker.setDefaults( $.datepicker.regional[ "ru" ] )

$.fn.select2.defaults.set("theme", "bootstrap4");

function stringDif (val1, val2) {
	if (val1 == null || val2 == null || val1.trim() == '' || val2.trim() == '')
		return null;
	let valNum1 = Number(val1.replace(',','.').replace(' ',''))
	let valNum2 = Number(val2.replace(',','.').replace(' ',''))
	if (Number.isNaN(valNum1) || Number.isNaN(valNum2))
		return null
	return valNum1 - valNum2
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