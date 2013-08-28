import os
import datetime

from sqlalchemy import func, event, DDL
from flask import url_for
from wtforms import validators

from . import db
from .dbfields import TSVector


PostTag = db.Table(
    'post_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), nullable=False),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False),
)


class Post(db.Model):
    _slug_validator = validators.Regexp(
        r'^[0-9a-z-]+$',
        message='Only digits, lower case letters and hyphens are allowed.',
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
        info={'validators': [_slug_validator]},
    )
    content = db.Column(db.UnicodeText, nullable=False)
    added = db.Column(db.Date, default=datetime.date.today, nullable=False)
    tsv = db.Column(TSVector, index=True)
    tags = db.relationship(
        'Tag',
        secondary=PostTag,
        backref=db.backref('posts', lazy='dynamic'),
    )

    @classmethod
    def get_by_url(cls, year, month, day, slug):
        q = cls.query.filter(
            cls.slug == slug,
            cls.added == datetime.date(year, month, day),
        )
        return q.first()

    def __init__(self, title=None, slug=None, content=None, added=None):
        self.title = title
        self.slug = slug
        self.content = content
        self.added = added

    def __repr__(self):
        return '<Post %r>' % self.slug[:20]

    def __str__(self):
        return self.title

    @property
    def _url_kwargs(self):
        return {
            'year': self.added.year,
            'month': self.added.month,
            'day': self.added.day,
            'slug': self.slug,
        }

    @property
    def url_list(self):
        return url_for('.post_list')

    @property
    def url_show(self):
        return url_for('.post_show', **self._url_kwargs)

    @property
    def url_edit(self):
        return url_for('.post_edit', post_id=self.id)

    @property
    def url_tags(self):
        return url_for('.post_tags', post_id=self.id)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % self.name

    def __str__(self):
        return self.name

    @classmethod
    def by_posts_num(cls):
        return (
            db.session.query(cls,
                             func.count(PostTag.c.post_id).label('num_posts'))
            .outerjoin(PostTag)
            .group_by(cls)
            .order_by('num_posts DESC')
        )

    @property
    def url_list(self):
        return url_for('.tag_list')

    @property
    def url_show(self):
        return url_for('.post_list', tag_id=self.id)

    @property
    def url_edit(self):
        return url_for('.tag_edit', tag_id=self.id)


_here = os.path.dirname(__file__)
_sql_path = os.path.join(_here, 'ddl-post.sql')
_on_ddl = DDL(open(_sql_path).read())

event.listen(Post.__table__, 'after_create',
             _on_ddl.execute_if(dialect='postgresql'))
