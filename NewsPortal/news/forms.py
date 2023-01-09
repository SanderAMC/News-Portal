from django import forms
from .models import Post
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):

   class Meta:
       model = Post
       fields = [
           'title',
           'text',
       ]

   def clean(self):
       cleaned_data = super().clean()
       title = cleaned_data.get("title")
       if title is not None and len(title) < 6:
           raise ValidationError({
               "title": "Заголовок должен быть длиннее 5 символов"
           })

       return cleaned_data