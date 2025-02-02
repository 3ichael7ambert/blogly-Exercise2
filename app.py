"""Blogly application."""

from flask import Flask, request, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User, Post, Tag, PostTag,db
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:smooth@localhost/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = str(os.environ.get('FLASK_SECRET_KEY'))
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.app_context().push()
#debug = DebugToolbarExtension(app)

# db=SQLAlchemy(app)
#db.init_app(app)
db = connect_db(app)

# def connect_db(app):


@app.route('/')
def show_homepage():
    '''Show homepage'''
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('home.html', posts=posts)

@app.route('/users')
def show_users():
    '''Show list of users'''
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users.html', users=users)

@app.route('/users/new')
def create_user():
    '''Render form to create new user'''
    return render_template('create-user.html')

@app.route('/users/new', methods=['POST'])
def add_user():
    '''Create user from form inputs. Update list and database.'''
    first = request.form['first-name']
    last = request.form['last-name']
    url = request.form['url'] or None
    user = User(first_name=first, last_name=last, image_url=url)
    db.session.add(user)
    db.session.commit()
    flash(f'User {user.get_full_name()} added.')
    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    '''Show user details page'''
    user = User.query.get(user_id)
    posts = Post.query.filter(Post.user_id == user_id).all()
    return render_template('user-details.html', user=user, posts=posts)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    '''Render form to edit user'''
    user = User.query.get(user_id)
    return render_template('edit-user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user(user_id):
    '''Update users information on site and in database'''
    first = request.form.get('first-name')
    last = request.form.get('last-name')
    url = request.form.get('url')
    user = User.query.get(user_id)
    user.first_name = first
    user.last_name = last
    user.image_url = url
    db.session.add(user)
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    '''Delete user from site and database.'''
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

@app.route('/users/<int:user_id>/posts/new')
def render_post_form(user_id):
    '''Render form to create new post.'''
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('create-post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_post(user_id):
    '''Add post attributed to user.'''
    title = request.form['title']
    post = request.form['post']
    checked_tags = request.form.getlist('tag-list')
    relevant_tags = Tag.query.filter(Tag.name.in_(checked_tags)).all()
    user = User.query.get_or_404(user_id)
    new_post = Post(title=title, content=post, user=user, tags=relevant_tags)
    db.session.add(new_post)
    db.session.commit()
    flash(f'Post added.')
    return redirect(f'/users/{user_id}')

@app.route('/posts/<int:post_id>')
def display_post(post_id):
    '''Show single post, along with buttons to cancel, edit or delete post.'''
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    return render_template('post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    '''Render form to edit post.'''
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('edit-post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def update_post(post_id):
    '''Update post information on site and in database'''
    post = Post.query.get(post_id)
    title = request.form['title']
    content = request.form['post']
    checked_tags = request.form.getlist('tag-list')
    relevant_tags = Tag.query.filter(Tag.name.in_(checked_tags)).all()
    post.title = title
    post.content = content
    post.tags = relevant_tags
    db.session.add(post)
    db.session.commit()
    flash(f'Post edited.')
    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    '''Remove post from site and database.'''
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(f'/users/{post.user_id}',)

# Tag Routes


@app.route('/tags')
def list_tags():
    '''List all tags'''
    # users = User.query.order_by(User.last_name, User.first_name).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def display_tag(tag_id):
    '''Display Tag Page'''
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts
    return render_template('posts-by-tag.html', posts=posts, tag=tag)

@app.route('/tags/new')
def render_new_tag_form():
    return render_template('create-tag.html')

@app.route('/tags/new', methods=['POST'])
def add_new_tag():
    tag_name = request.form['tag']
    new_tag = Tag(name=tag_name)
    db.session.add(new_tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def render_edit_tag_form(tag_id):
    tag = Tag.query.get(tag_id)
    return render_template('edit-tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def update_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    name = request.form['tag']
    tag.name = name
    db.session.add(tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags')

# if __name__== '__main__':
#     app.run(debug=True)
    