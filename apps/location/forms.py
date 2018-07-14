from django.forms import forms


class ImportForm(forms.Form):
    """Form to upload the address."""
    import_address = forms.FileField(allow_empty_file=False)
