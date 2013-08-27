from wtforms import Form, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_alchemy import ModelForm

from .models import Post, Tag


class PostForm(ModelForm):

    class Meta:
        model = Post


class TagForm(ModelForm):

    class Meta:
        model = Tag


class PostTagsForm(Form):
    tags = SelectMultipleField(
        coerce=int,
        widget=ListWidget(),
        option_widget=CheckboxInput(),
    )

    def __init__(self, *args, **kwargs):
        super(PostTagsForm, self).__init__(*args, **kwargs)
        self.tags.choices = \
            [(t.id, t.name) for t in Tag.query.order_by(Tag.name)]
