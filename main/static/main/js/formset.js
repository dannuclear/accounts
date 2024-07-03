function addForm (prefix) {
    const container = $(`.${prefix}-container`)
    const allForms = $(`.${prefix}-form`)
    const formsCount = allForms.length

    const newForm = allForms[0].cloneNode(true)
    const formRegex = RegExp(`${prefix}-(\\d){1}-`,'g')
    const nextNum = formsCount + 1
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `${prefix}-${formsCount}-`)
    container.append(newForm).find(`#id_${prefix}-${formsCount}-id`).remove()
    document.querySelector(`#id_${prefix}-TOTAL_FORMS`).setAttribute('value', `${nextNum}`)
    return newForm
}