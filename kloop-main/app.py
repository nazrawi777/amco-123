from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amco.db'
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

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='BlogPost',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='Event',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def log_action(self, action, details):
        log_entry = ActionHistory(
            entity_type='NewsArticle',
            entity_id=self.id,
            action=action,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()

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

        new_job.log_action('Added', f"Job '{title}' added successfully.")

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

#blog part 
# Sample data (replace with database implementation)
blog_posts = [
    {"id": 1, "title": "First Blog Post", "description": "Lorem ipsum dolor sit amet.", "date": "2024-05-01"},
    {"id": 2, "title": "Second Blog Post", "description": "Consectetur adipiscing elit.", "date": "2024-05-05"}
]

events = [
    {"id": 1, "title": "Event 1", "description": "Lorem ipsum dolor sit amet.", "date": "2024-06-01", "location": "Location 1", "image": "event1.jpg"},
    {"id": 2, "title": "Event 2", "description": "Consectetur adipiscing elit.", "date": "2024-06-10", "location": "Location 2", "image": "event2.jpg"}
]

news_articles = [
    {"id": 1, "title": "News Article 1", "description": "Lorem ipsum dolor sit amet.", "date": "2024-05-15"},
    {"id": 2, "title": "News Article 2", "description": "Consectetur adipiscing elit.", "date": "2024-05-20"}
]
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


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

@app.route('/bloog')
def bloog():
    return render_template('c.html')

@app.route('/bagout')
def bagout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))
# Admin Pages - Main Page
@app.route('/badmin')
def badmin():
    return render_template('badmin.html')

# Admin Pages - Blog Management
@app.route('/badmin/blog/create', methods=['GET', 'POST'])
def create_blog_post():
    if request.method == 'POST':
        # Handle form submission to create a new blog post
        title = request.form['title']
        description = request.form['description']
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        # Save data to the database or any storage mechanism
        blog_posts.append({"id": len(blog_posts) + 1, "title": title, "description": description, "date": date})


        return redirect(url_for('bloog'))
    return render_template('create_blog_post.html')

@app.route('/admin/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit_blog_post(id):
    post = next((post for post in blog_posts if post['id'] == id), None)
    if request.method == 'POST':
        # Handle form submission to edit the blog post
        post['title'] = request.form['title']
        post['description'] = request.form['description']

        edit_blog_post.log_action('Edited', f"Blog post '{post['title']}' edited successfully.")
        return redirect(url_for('bloog'))
    return render_template('edit_blog_post.html', post=post)

@app.route('/badmin/blog/delete/<int:id>')
def delete_blog_post(id):
    blog_posts[:] = [post for post in blog_posts if post.get('id') != id]
    delete_blog_post.log_action('Deleted', f"Blog post '{post['title']}' deleted successfully.")
    return redirect(url_for('bloog'))

# Admin Pages - Events Management
@app.route('/badmin/events/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        events.append({"id": len(events) + 1, "title": title, "description": description, "date": date, "location": location})
        return redirect(url_for('events_page'))
    return render_template('create_event.html')

@app.route('/badmin/events/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = next((event for event in events if event['id'] == id), None)
    if request.method == 'POST':
        # Handle form submission to edit the event
        event['title'] = request.form['title']
        event['description'] = request.form['description']
        event['date'] = request.form['date']
        event['location'] = request.form['location']
        edit_event.log_action('Edited', f"Event '{event['title']}' edited successfully.")

    return render_template('edit_event.html', event=event)

@app.route('/badmin/events/delete/<int:id>')
def delete_event(id):
    events[:] = [event for event in events if event.get('id') != id]
    delete_event.log_action('Deleted', f"Event '{event['title']}' deleted successfully.")
    return redirect(url_for('events_page'))

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)