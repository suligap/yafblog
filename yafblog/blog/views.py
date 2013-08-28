import datetime

from flask import render_template, request, redirect, abort, flash, url_for
from flask.ext.login import login_required

from . import blueprint, db
from .models import Post, Tag
from .forms import PostForm, TagForm, PostTagsForm


POSTS_PER_PAGE = 6


def search(term):
    bparams = [db.bindparam('term', term)]
    return Post.query.filter(
        db.text("post.tsv @@ plainto_tsquery('english', :term)",
                bindparams=bparams)
    ).order_by(
        db.text("ts_rank_cd(tsv, plainto_tsquery('english', :term)) DESC",
                bindparams=bparams)
    )


@blueprint.route('/')
@blueprint.route('/p/<int:page>')
@blueprint.route('/tag/<tag_id>')
@blueprint.route('/tag/<tag_id>/p/<int:page>')
def post_list(page=1, tag_id=None):
    tag = tag_id and Tag.query.get_or_404(tag_id)
    per_page = POSTS_PER_PAGE
    search_term = request.args.get('q')
    if search_term:
        q = search(search_term)
    else:
        q = Post.query.order_by(Post.added.desc())
    if tag_id:
        q = q.filter(Post.tags.any(Tag.id == tag_id))
    pagination = q.order_by(Post.added.desc()).paginate(page, per_page)
    return render_template(
        'blog/post_list.html',
        pagination=pagination,
        search_term=search_term,
        tag=tag,
    )


@blueprint.route('/<int(4):year>/<int(max=12):month>/<int(max=31):day>/<slug>')
def post_show(year, month, day, slug):
    post = Post.get_by_url(year, month, day, slug)
    if post is None:
        abort(404)
    return render_template('blog/post_show.html', post=post)


@blueprint.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        return process_post_form(data=request.form, post=post)
    return process_post_form(post=post)


@blueprint.route('/post/add', methods=['GET', 'POST'])
@login_required
def post_add():
    if request.method == 'POST':
        return process_post_form(request.form)
    return process_post_form()


@blueprint.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    return process_obj_delete(post)


def process_post_form(data=None, post=None):
    is_add = post is None
    post = post or Post(added=datetime.date.today())
    form = PostForm(data, obj=post)
    if data is not None and form.validate():
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        msg = 'Post added.' if is_add else 'Post edited.'
        flash(msg)
        return redirect(post.url_show)
    return render_template(
        'blog/post_form.html',
        form=form,
        is_add=is_add,
        post=post,
    )


@blueprint.route('/post/<int:post_id>/tags', methods=['GET', 'POST'])
@login_required
def post_tags(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        form = PostTagsForm(request.form)
        if form.validate():
            post.tags = Tag.query.filter(
                Tag.id.in_(form.tags.data or [])).all()
            db.session.add(post)
            db.session.commit()
            flash('Post tagged.')
            return redirect(post.url_show)
    else:
        form = PostTagsForm(request.form, tags=[t.id for t in post.tags])
    return render_template('blog/post_tags_form.html', form=form, post=post)


@blueprint.route('/tags')
def tag_list():
    tags = Tag.by_posts_num()
    return render_template('blog/tag_list.html', tags=tags)


@blueprint.route('/tag/add', methods=['GET', 'POST'])
@login_required
def tag_add():
    if request.method == 'POST':
        return process_tag_form(data=request.form)
    return process_tag_form()


@blueprint.route('/tag/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def tag_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        return process_tag_form(data=request.form, tag=tag)
    return process_tag_form(tag=tag)


@blueprint.route('/tag/<int:tag_id>/delete', methods=['GET', 'POST'])
@login_required
def tag_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return process_obj_delete(tag)


def process_tag_form(data=None, tag=None):
    is_add = tag is None
    tag = tag or Tag()
    form = TagForm(data, obj=tag)
    if data is not None and form.validate():
        form.populate_obj(tag)
        db.session.add(tag)
        db.session.commit()
        msg = 'Tag added.' if is_add else 'Tag edited.'
        flash(msg)
        return redirect(url_for('.tag_list'))
    return render_template(
        'blog/tag_form.html',
        form=form,
        tag=tag,
        is_add=is_add,
    )


def process_obj_delete(obj):
    type_name = obj.__class__.__name__
    if request.method == 'POST':
        db.session.delete(obj)
        db.session.commit()
        flash('%s Deleted.' % type_name)
        return redirect(obj.url_list)
    return render_template(
        'blog/delete_form.html',
        obj=obj,
        type_name=type_name,
    )
