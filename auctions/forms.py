from django import forms


class ListingForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter title'
            }
        ),
        max_length=64
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter description'
            }
        )
    )

    bid = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form=control',
                'placeholder': 'Enter bid'
            }
        )
    )

    image = forms.URLField(
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter image url'
            }
        ),
        required=False
    )

    category = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter category',
            }
        ),
        required=False,
        max_length=64
    )
