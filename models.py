"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import ForeignKey

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)
    return db 


class User(db.Model):
    '''Define User Model'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    image_url = db.Column(db.String(250), nullable=False,
                          default='https://tinyurl.com/yc2rkm4z')
    posts = db.relationship('Post', backref="user",
                            cascade='all, delete-orphan')

    def __repr__(self):
        u = self
        return f'<User id={u.id} first_name={u.first_name} last_name={u.last_name} img_url={u.image_url}>'

    def get_full_name(self):
        '''Returns a users first and last name'''
        return f'{self.first_name} {self.last_name}'


class Post(db.Model):
    '''Define Post Model.'''
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)

    def __repr__(self):
        '''Display instance attributes'''
        p = self
        return f'<title: {p.title} content: {p.content} created_at: {p.created_at} user_id: {p.user_id}>'

    def get_pretty_date(self):
        '''Return string formatted date to display to users.'''
        return self.created_at.strftime('%a %b %-d %Y, %I:%-M %p')


class Tag(db.Model):
    '''Define Tag Model.'''
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True)
    posts = db.relationship('Post', secondary='post_tags', backref='tags')

    def __repr__(self):
        return f'<id: {self.id} name: {self.name} posts: {self.posts}>'


class PostTag(db.Model):
    '''Define PostTag Relationship Model.'''
    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey(
        'tags.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return f'<post_id: {self.post_id} tag_id: {self.tag_id}>'

# Issues:
# When a tag gets deleted, the related posts should not. Currently error.
# AND, when a tag gets deleted, the related posts should not