from django import forms
from .models import Post, Category
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'category',
            'post_type',
        ]

    # def clean(self):
    #     cleaned_data = super().clean()
    #     content = cleaned_data.get("content")
    #     title = cleaned_data.get("title")
    #
    #     if title == content:
    #         raise ValidationError(
    #             "Описание не должно быть идентично названию."
    #         )
    #
    #     return cleaned_data

# class ProductForm(forms.Form):
#     name = forms.CharField(label='Name')
#     description = forms.CharField(label='Description')
#     quantity = forms.IntegerField(label='Quantity')
#     category = forms.ModelChoiceField(
#         label='Category', queryset=Category.objects.all(),
#     )
#     price = forms.FloatField(label='Price')
