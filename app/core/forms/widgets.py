import abc
from wtforms.widgets import html_params, HTMLString


class GeBaseWidget(abc.ABC):

    html_params = staticmethod(html_params)
    input_mask = None

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        self.inputId = kwargs.get('id', field.id)
        self.html = [u'<div class="form-group">']

        # Define a configuração do tamanho do label e do input
        labelSize = kwargs.pop('labelSize', 'col-xs-12 col-md-3')
        inputSize = kwargs.pop('inputSize', 'col-xs-12 col-md-6')

        # Define o label do campo
        self.html.append(u'<label class="control-label %s" for="%s">' %
                         (labelSize, self.inputId))
        self.html.append(u'%s' % field.label)
        if field.flags.required:
            self.html.append(u'<span class="required">*</span>')
        self.html.append(u'</label>')

        # Define o tamanho do input na template
        self.html.append(u'<div class="%s">' % inputSize)

        if 'value' not in kwargs:
            v = getattr(field, '_value', None)
            if v:
                kwargs['value'] = v()

        if field.errors:
            self.html.append(u'<div class="has-error">')
            self.createInput(field, **kwargs)

            for e in field.errors:
                self.html.append(u'<span class="help-block">%s</span>' % e)

            self.html.append(u'</div>')
        else:
            self.createInput(field, **kwargs)

        self.html.append(u'</div>')
        self.html.append(u'</div>')

        return HTMLString(''.join(self.html))

    @abc.abstractmethod
    def createInput(self):
        pass


class GeInputWidget(GeBaseWidget):

    input_type = 'text'

    def __call__(self, field, **kwargs):
        if self.input_mask:
            kwargs.setdefault('data_inputmask', self.input_mask)
        return super(GeInputWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<input class="form-control" %s>' % self.html_params(name=field.name, **kwargs))
        icon = kwargs.pop('icon', None)
        if icon:
            self.html.append(u'<span class="fa %s form-control-feedback right"></span>' % icon)


class GePasswordWidget(GeBaseWidget):

    input_type = 'password'

    def __call__(self, field, **kwargs):
        return super(GePasswordWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<input class="form-control" %s>' % self.html_params(name=field.name, **kwargs))


class GeFileWidget(GeBaseWidget):
    
    input_type = 'file'

    def __call__(self, field, **kwargs):
        return super(GeFileWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<input class="form-control" %s>' % self.html_params(name=field.name, **kwargs))


class GeIntegerWidget(GeInputWidget):

    input_mask = "'mask': '9', 'repeat': 10, 'greedy': false"

    def __call__(self, field, **kwargs):
        return super(GeIntegerWidget, self).__call__(field, **kwargs)


class GePhoneWidget(GeInputWidget):

    input_mask = "'mask': '(99) 9999[9]-9999', 'skipOptionalPartCharacter': ' '"

    def __call__(self, field, **kwargs):
        return super(GePhoneWidget, self).__call__(field, **kwargs)


class GeDateWidget(GeInputWidget):

    input_mask = "'mask': '99/99/9999', 'greedy': false"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('inputSize', 'col-md-2 col-sm-2 col-xs-12')
        kwargs.setdefault('data_type', 'date')
        return super(GeDateWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<input class="form-control" %s>' % self.html_params(name=field.name, **kwargs))
        self.html.append(u'<span class="fa fa-calendar-o form-control-feedback right" aria-hidden="true"></span>')


class GeDateTimeWidget(GeInputWidget):

    input_mask = "'mask': '99/99/9999 99:99:99', 'greedy': false"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('inputSize', 'col-md-3 col-sm-3 col-xs-12')
        kwargs.setdefault('data_type', 'datetime')
        return super(GeDateTimeWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<input class="form-control" %s>' % self.html_params(name=field.name, **kwargs))
        self.html.append(u'<span class="fa fa-calendar-o form-control-feedback right" aria-hidden="true"></span>')


class GeSelectWidget(GeBaseWidget):

    input_type = 'text'

    def __call__(self, field, **kwargs):
        return super(GeSelectWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        self.html.append(u'<select class="form-control" %s>' % self.html_params(name=field.name, id=self.inputId))
        for value, label, selected in field.iter_choices():
            options = dict(value=value)
            if selected:
                options['selected'] = 'selected'
            self.html.append(u'<option %s>%s</option>' % (self.html_params(**options), label))
        self.html.append(u'</select>')


class GeCheckboxWidget(GeBaseWidget):

    input_type = 'checkbox'

    def __call__(self, field, **kwargs):
        return super(GeCheckboxWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        for value, label, checked in field.iter_choices():
            self.html.append(u'<div class="radio">')
            self.html.append(u'<label>')
            choice_id = u'%s-%s' % (self.inputId, value)
            options = dict(kwargs, name=field.name, value=value, id=choice_id)
            if checked:
                options['checked'] = 'checked'
            self.html.append(u'<input %s /> %s' % (html_params(**options), label))

            self.html.append(u'</label>')
            self.html.append(u'</div>')


class GeBooleanWidget(GeBaseWidget):

    input_type = 'checkbox'

    def __call__(self, field, **kwargs):
        if self.input_mask:
            kwargs.setdefault('data_inputmask', self.input_mask)
        return super(GeBooleanWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        if field.data:
            kwargs.setdefault('checked', True)
        self.html.append(u'<div class="checkbox">')
        self.html.append(u'<label>')
        self.html.append(u'<input class="js-switch" %s>' % self.html_params(name=field.name, **kwargs))
        self.html.append(u'</label>')
        self.html.append(u'</div>')


class GeRadioWidget(GeBaseWidget):

    input_type = 'radio'

    def __call__(self, field, **kwargs):
        if self.input_mask:
            kwargs.setdefault('data_inputmask', self.input_mask)
        return super(GeRadioWidget, self).__call__(field, **kwargs)

    def createInput(self, field, **kwargs):
        for value, label, checked in field.iter_choices():
            self.html.append(u'<div class="radio">')
            self.html.append(u'<label>')

            choice_id = u'%s-%s' % (self.inputId, value)
            options = dict(kwargs, name=field.name, value=value, id=choice_id)
            if checked:
                options['checked'] = 'checked'
            self.html.append(u'<input %s class="flat"/> %s' % (html_params(**options), label))

            self.html.append(u'</label>')
            self.html.append(u'</div>')
