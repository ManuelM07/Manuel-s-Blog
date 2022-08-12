from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from posts import BlogPost, app, db
from post_form import CreatePostForm
import requests
import os 
import smtplib 
import datetime


EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
EMAIL_RESPONSE = os.environ.get('EMAIL_RESPONSE')

my_email = EMAIL
password = PASSWORD


app.config['SECRET_KEY'] = ''
Bootstrap(app)


date = datetime.datetime.now()
day = date.day
month = date.strftime("%B")
year = date.year


@app.route('/')
def home():
    posts = BlogPost.query.all()
    return render_template("index.html", data_npoint=posts)



@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.form
        msg = f"Name: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\nMessage: {data['message']}"
        send_email(msg)
        return render_template("contact.html", send=True)
    return render_template("contact.html", send=False)


@app.route('/post/<int:blog_id>')
def get_blog(blog_id):
    post = BlogPost.query.get(blog_id)
    return render_template("post.html", data_npoint=post)


@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()

    if form.validate_on_submit():

        new_post = BlogPost(
            title = form.title.data,
            subtitle = form.subtitle.data,
            date = f"{month} {day}, {year}",
            body = form.body.data,
            author = form.author.data,
            img_url = form.img_url.data
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template("make-post.html", form=form, type="New Post")


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post_update = BlogPost.query.get(post_id)
    form = CreatePostForm(
        title=post_update.title,
        subtitle=post_update.subtitle,
        img_url=post_update.img_url,
        author=post_update.author,
        body=post_update.body
    )

    if form.validate_on_submit():

        post_update.title = form.title.data
        post_update.subtitle = form.subtitle.data
        post_update.body = form.body.data
        post_update.author = form.author.data
        post_update.img_url = form.img_url.data
        db.session.commit()

        return redirect(url_for('get_blog', blog_id=post_id))
    return render_template("make-post.html", form=form, type="Edit Post")


@app.route('/delete/<int:post_id>')
def delete(post_id):
    post_delete = BlogPost.query.get(post_id)
    db.session.delete(post_delete)
    db.session.commit()

    return redirect(url_for('home'))


def send_email(msg):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls() 
        connection.login(user=my_email, password=password)
        connection.sendmail(
        from_addr=my_email, 
        to_addrs=EMAIL_RESPONSE, 
        msg=f"Subject:New message blog\n\n{msg}"
    )


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
