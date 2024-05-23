from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amco.db'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class ActionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    action = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)

    def __init__(self, entity_type, entity_id, action, details):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.details = details


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='Product',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

class AppliedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    applicant_email = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    cv_path = db.Column(db.String(100), nullable=True)

    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='AppliedJob',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

# Sample BlogPost model
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)  # Add a description field
    date = db.Column(db.Date, nullable=False) 
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Event(title='{self.title}', date='{self.date}', location='{self.location}')>"

# Sample NewsArticle model
class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    requirements = db.Column(db.String(500), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.check_availability()

    def check_availability(self):
        if self.deadline and self.deadline < datetime.now():
            self.is_active = False
            db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'description': self.description,
        }

    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='Job',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/prod')
def p_page():
    products = Product.query.all()
    return render_template('prod.html', products=products)

@app.route('/login/admin')
def admin():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
            else:
                flash('No image selected.', 'error')
                return redirect(request.url)

        new_product = Product(name=name, price=price, image=filename, description=description)
        db.session.add(new_product)
        db.session.commit()
        
        new_product.log_action('Added', f"Product '{name}' added successfully.")

        flash('Product added successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('add_product.html')

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('login'))
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                product.image = filename

        db.session.commit()
        # Assuming you have a product instance named 'product'
        product.log_action('Edited', f"Product '{product.name}' edited successfully.")


        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('login'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    # Assuming you have a product instance named 'product'
    product.log_action('Deleted', f"Product '{product.name}' deleted successfully.")


    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/vadmin/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%dT%H:%M')

        job = Job(title=title, description=description, requirements=requirements, deadline=deadline)
        db.session.add(job)
        db.session.commit()

        job.log_action('Added', f"Job '{title}' added successfully.")

        return "Job added successfully!"

    return render_template('add_job.html')


@app.route('/vadmin/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    db.session.delete(job)
    db.session.commit()

    job.log_action('Deleted', f"Job '{job.title}' deleted successfully.")

    return redirect(url_for('vadmin'))

@app.route('/vacancy')
def vacancy():
    jobs = Job.query.filter_by(is_active=True).all()
    return render_template('vacancy.html', jobs=jobs)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        jobs = Job.query.filter(Job.title.ilike(f'%{search_term}%')).all()
        return render_template('search_results.html', jobs=jobs, search_term=search_term)
    return redirect(url_for('home'))

@app.route('/lagin', methods=['GET', 'POST'])
def lagin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('vadmin'))
        else:
            return render_template('lagin.html', error='Invalid username or password')

    return render_template('lagin.html')

@app.route('/lagout')
def lagout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('lagin'))

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    job = Job.query.get(job_id)
    current_time = datetime.now()  # Get the current time

    if job.deadline and job.deadline < current_time:
        return render_template('apply.html', job=job, error='Application deadline has passed.', current_time=current_time)

    if request.method == 'POST':
        first_name = request.form['first_name']
        father_name = request.form['father_name']
        email = request.form['email']
        gender = request.form['gender']
        age = request.form['age']
        cv = request.files['cv']
        cv.save(os.path.join(app.config['UPLOAD_FOLDER'], cv.filename))

        applied_job = AppliedJob(
            job_id=job_id,
            first_name=first_name,
            father_name=father_name,
            applicant_email=email,
            gender=gender,
            age=age,
            cv_path=f"uploads/{cv.filename}"
        )
        db.session.add(applied_job)
        db.session.commit()

        return redirect(url_for('vacancy'))

    return render_template('apply.html', job=job, current_time=current_time)

@app.route('/lagin/vadmin')
def vadmin():
    jobs = Job.query.all()
    return render_template('vadmin.html', jobs=jobs)

@app.route('/vadmin/applied_jobs/<int:job_id>')
def applied_jobs(job_id):
    applied_jobs = AppliedJob.query.filter_by(job_id=job_id).all()
    return render_template('applied_jobs.html', applied_jobs=applied_jobs, job_id=job_id)

@app.route('/vadmin/delete_applied_job/<int:applied_job_id>', methods=['POST'])
def delete_applied_job(applied_job_id):
    applied_job = AppliedJob.query.get(applied_job_id)
    db.session.delete(applied_job)
    db.session.commit()

    applied_job.log_action('Deleted', f"Applied job with ID '{applied_job_id}' deleted successfully.")

    return redirect(url_for('applied_jobs', job_id=applied_job.job_id))

@app.route('/download_cv/<path:cv_path>')
def download_cv(cv_path):
    cv_directory = app.config['UPLOAD_FOLDER']
    filename = os.path.basename(cv_path)
    return send_from_directory(cv_directory, filename, as_attachment=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route('/bloog')
def bloog():
    # Retrieve data from the database
    blog_posts = BlogPost.query.all()
    events = Event.query.all()
    news_articles = NewsArticle.query.all()
    # Pass data to the HTML template
    return render_template('c.html', blog_posts=blog_posts, events=events, news_articles=news_articles)



@app.route('/bagin', methods=['GET', 'POST'])
def bagin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('badmin'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('bagin.html')

@app.route('/bagout')
def bagout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/badmin')
def badmin():
    posts = BlogPost.query.all()  # Retrieve all blog posts
    articles = NewsArticle.query.all()  # Retrieve all news articles
    events = Event.query.all()  # Retrieve all events
    return render_template('badmin.html', posts=posts, articles=articles, events=events)

# Blog post routes
@app.route('/badmin/blog/create', methods=['GET', 'POST'])
def create_blog_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        new_post = BlogPost(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog post created successfully', 'success')
        return redirect(url_for('badmin'))
    return render_template('create_blog_post.html')

@app.route('/badmin/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit_blog_post(id):
    post = BlogPost.query.get(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        db.session.commit()
        flash('Blog post updated successfully', 'success')
        return redirect(url_for('badmin'))  # Changed from 'admin' to 'badmin'
    return render_template('edit_blog_post.html', post=post)

@app.route('/badmin/blog/delete/<int:id>', methods=['POST'])
def delete_blog_post(id):
    post = BlogPost.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully', 'success')
    return redirect(url_for('badmin')) 

# Event routes
@app.route('/badmin/events/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        location = request.form['location']
        new_event = Event(title=title, description=description, date=date, location=location)
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully', 'success')
        return redirect(url_for('badmin'))
    return render_template('create_event.html')

@app.route('/badmin/events/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get(id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        event.location = request.form['location']
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('badmin'))  # Changed from 'admin' to 'badmin'
    return render_template('edit_event.html', event=event)

@app.route('/badmin/events/delete/<int:id>', methods=['POST'])
def delete_event(id):
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully', 'success')
    return redirect(url_for('badmin'))  # Changed from 'admin' to 'badmin'

# News article routes
@app.route('/badmin/news/create', methods=['GET', 'POST'])
def create_news_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        new_article = NewsArticle(title=title, content=content, author=author)
        db.session.add(new_article)
        db.session.commit()
        flash('News article created successfully', 'success')
        return redirect(url_for('badmin'))
    return render_template('create_news_article.html')

@app.route('/badmin/news/edit/<int:id>', methods=['GET', 'POST'])
def edit_news_article(id):
    article = NewsArticle.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        article.author = request.form['author']
        db.session.commit()
        flash('News article updated successfully', 'success')
        return redirect(url_for('badmin'))
    return render_template('edit_news_article.html', article=article)

@app.route('/badmin/news/delete/<int:id>', methods=['POST'])
def delete_news_article(id):
    article = NewsArticle.query.get(id)
    db.session.delete(article)
    db.session.commit()
    flash('News article deleted successfully', 'success')
    return redirect(url_for('badmin'))

@app.route('/sagin/super')
def super_view():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('sagin'))
    
    actions = ActionHistory.query.order_by(ActionHistory.timestamp.desc()).all()
    
    return render_template('all.html', actions=actions)

@app.route('/sagin/delete_action/<int:action_id>', methods=['POST'])
def delete_action(action_id):
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('sagin'))
    
    action = ActionHistory.query.get_or_404(action_id)
    db.session.delete(action)
    db.session.commit()
    flash('Action deleted successfully.', 'success')
    return redirect(url_for('super_view'))


@app.route('/sagin', methods=['GET', 'POST'])
def sagin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('super_view'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('sagin.html')

@app.route('/sagout')
def sagout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(50), nullable=False)
    photo_url = db.Column(db.String(200))

    def __repr__(self):
        return f"TeamMember(id={self.id}, name='{self.name}', job_title='{self.job_title}')"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/tagin/team/add', methods=['POST'])
def add_member():
    name = request.form['name']
    
    if 'job_title' in request.form:
        job_title = request.form['job_title']
    else:
        return "The 'job_title' field is missing from the request.", 400
    
    photo = request.files.get('photo')

    if not photo:
        return 'No file part', 400
    if photo.filename == '':
        return 'No selected file', 400
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        photo_url = url_for('uploaded_file', filename=filename)

        new_member = TeamMember(name=name, job_title=job_title, photo_url=photo_url)
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for('team'))
    else:
        return 'Invalid file type.', 400

@app.route('/about')
def about():
    team_members = TeamMember.query.all()
    return render_template('about.html', team_members=team_members)

@app.route('/tagin/team/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    member = TeamMember.query.get(member_id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.job_title = request.form['job_title']
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            member.photo_url = url_for('uploaded_file', filename=filename)
        db.session.commit()
        return redirect(url_for('team'))
    return render_template('edit_member.html', member=member)

@app.route('/tagin/team/delete/<int:member_id>', methods=['GET'])
def delete_member(member_id):
    member = TeamMember.query.get(member_id)
    if member:
        db.session.delete(member)
        db.session.commit()
    return redirect(url_for('team'))

@app.route('/tagin', methods=['GET', 'POST'])
def tagin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('team'))
        else:
            return render_template('lagin.html', error='Invalid username or password')

    return render_template('tagin.html')

@app.route('/tagout')
def tagout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('tagin'))


@app.route('/tagin/team')
def team():
    team_members = TeamMember.query.all()
    return render_template('team.html', team_members=team_members)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)