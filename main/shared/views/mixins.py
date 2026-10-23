from prepayment.action_processor import addItem


# class ActionMixin:

#     def get_user_full_name(self):
#         u = self.request.user
#         full_name = ('%s %s' % (u.last_name, u.first_name)).strip()
#         return full_name if full_name else u.username

#     def post(self, request, *args, **kwargs):
#         action = request.POST.get('action')

#         if not action:
#             return super().post(request, *args, **kwargs)
#         self.object = None
#         post_copy = request.POST.copy()

#         if action.startswith('add-'):
#             addItem(post_copy, action.removeprefix('add-'))

#         elif action.startswith('delete-'):
#             prefix = action.removeprefix('delete-')
#             post_copy[f'{prefix}-DELETE'] = 'True'

#         form_kwargs = self.get_form_kwargs()
#         form_kwargs['data'] = post_copy

#         form = self.get_form_class()(**form_kwargs)

#         return self.render_to_response(
#             self.get_context_data(form=form)
#         )

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs

# ---------------------------------------------------------------------------
# Общий базовый миксин: ничего специфичного для prepayment
# ---------------------------------------------------------------------------
class ActionMixin:
 
    def get_user_full_name(self):
        u = self.request.user
        full_name = ('%s %s' % (u.last_name, u.first_name)).strip()
        return full_name if full_name else u.username
 
    def get_object_or_none(self):
        return self.get_object() if self.pk_url_kwarg in self.kwargs else None
 
    def get_post_data(self):
        # Копия POST с применённым action; считается один раз за запрос
        if not hasattr(self, '_post_data'):
            data = self.request.POST.copy()
            action = data.get('action')
            if action:
                self.apply_action(data, action)
            self._post_data = data
        return self._post_data
 
    def apply_action(self, data, action):
        """Расширяйте в наследниках: свои action обрабатывать, остальное отдавать в super()."""
        if action.startswith('add-'):
            addItem(data, action.removeprefix('add-'))
        elif action.startswith('delete-'):
            data['%s-DELETE' % action.removeprefix('delete-')] = 'True'
 
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.method == 'POST':
            kwargs['data'] = self.get_post_data()
        return kwargs
 
    def post(self, request, *args, **kwargs):
        if not request.POST.get('action'):
            return super().post(request, *args, **kwargs)
        # action: перерисовываем форму с изменённым POST, без валидации и сохранения
        self.object = self.get_object_or_none()
        return self.render_to_response(self.get_context_data())
