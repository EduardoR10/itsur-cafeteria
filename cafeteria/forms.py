from django import forms

class BuscarProductoForm(forms.Form):
    q = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Buscar producto...",
            "class": "form-control me-2"  
        })
    )

class AddItemForm(forms.Form):
    producto_id = forms.IntegerField(widget=forms.HiddenInput)
    cantidad = forms.IntegerField(min_value=1, initial=1)
