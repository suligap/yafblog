import os

from yafblog import auth, blog, db


def add_users():
    u = auth.models.User(
        username=os.environ.get('ADMIN_USERNAME', 'foo'),
        email='foo@bar.com',
        password=os.environ.get('ADMIN_PASSWORD', 'bar'),
    )
    db.session.add(u)
    db.session.commit()
    db.session.close()


def populate_db():
    for i in xrange(8):
        p = blog.models.Post(
            'Title number %s' % i,
            slug='title-number-%s-slug' % i,
            content=_content,
        )
        db.session.add(p)

    for i in xrange(10):
        tag = blog.models.Tag('Tag-%s' % i)
        db.session.add(tag)

    db.session.commit()
    db.session.close()


def create_tables():
    db.drop_all()
    db.create_all()
    add_users()
    populate_db()


_content = u'''<p><i><b>White Pony</b></i> is the third <a href="https://en.wikipedia.org/wiki/Studio_album" title="Studio album">studio album</a> by American <a href="https://en.wikipedia.org/wiki/Alternative_metal" title="Alternative metal">alternative metal</a> band <a href="https://en.wikipedia.org/wiki/Deftones" title="Deftones">Deftones</a>, released on June 20, 2000. It marked a significant growth in the band's sound, incorporating <a href="https://en.wikipedia.org/wiki/New_wave_music" title="New wave music">new wave</a>, <a href="https://en.wikipedia.org/wiki/Dream_pop" title="Dream pop">dream pop</a>, <a href="https://en.wikipedia.org/wiki/Trip_hop" title="Trip hop">trip hop</a>, and <a href="https://en.wikipedia.org/wiki/Shoegazing" title="Shoegazing">shoegazing</a> influences with the alternative metal edge the group had become known for and is considered a turning point for the band in terms of experimentation. <p>Source: <a href="https://en.wikipedia.org/wiki/White_Pony">White Pony Wikipedia Article</a></p>'''  # NOQA


if __name__ == '__main__':
    create_tables()
