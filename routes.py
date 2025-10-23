from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Category, Purchase, AuditLog
from datetime import datetime
import os
import json
import csv
from io import StringIO, BytesIO
from functools import wraps
from sqlalchemy import func, extract

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('login'))
            if current_user.role != role and current_user.role != 'dev':
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def register_routes(app):
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('dashboard'))
            elif current_user.role == 'dev':
                return redirect(url_for('dev_home'))
            else:
                return redirect(url_for('upload'))
        return redirect(url_for('login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'shopper')
            
            if not username or not email or not password:
                flash('All fields are required.', 'danger')
                return render_template('register.html')
            
            if role not in ['shopper', 'admin']:
                role = 'shopper'
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return render_template('register.html')
            
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=True)
                flash(f'Welcome back, {user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/dev')
    @login_required
    @role_required('dev')
    def dev_home():
        return render_template('dev_home.html')
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    @role_required('shopper')
    def upload():
        categories = Category.query.all()
        
        if request.method == 'POST':
            try:
                description = request.form.get('description', '').strip()
                amount = request.form.get('amount', '').strip()
                quantity = request.form.get('quantity', '1').strip()
                vendor = request.form.get('vendor', '').strip()
                date_collected = request.form.get('date_collected', '').strip()
                purchase_type = request.form.get('purchase_type', 'product')
                category_id = request.form.get('category_id', '').strip()
                notes = request.form.get('notes', '').strip()
                paid_on_collection = 1 if request.form.get('paid_on_collection') else 0
                
                if not description or not amount or not vendor or not date_collected:
                    flash('Description, amount, vendor, and date are required.', 'danger')
                    return render_template('upload.html', categories=categories)
                
                try:
                    amount = float(amount)
                    if amount <= 0:
                        raise ValueError()
                except ValueError:
                    flash('Amount must be a positive number.', 'danger')
                    return render_template('upload.html', categories=categories)
                
                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                        raise ValueError()
                except ValueError:
                    flash('Quantity must be a positive integer.', 'danger')
                    return render_template('upload.html', categories=categories)
                
                try:
                    date_obj = datetime.strptime(date_collected, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format.', 'danger')
                    return render_template('upload.html', categories=categories)
                
                attachment_url = None
                if 'attachment' in request.files:
                    file = request.files['attachment']
                    if file and file.filename:
                        if allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            filename = f"{timestamp}_{filename}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            file.save(filepath)
                            attachment_url = f"uploads/{filename}"
                        else:
                            flash('Invalid file type. Only PDF, JPG, and PNG are allowed.', 'danger')
                            return render_template('upload.html', categories=categories)
                
                purchase = Purchase(
                    user_id=current_user.id,
                    description=description,
                    amount=amount,
                    quantity=quantity,
                    vendor=vendor,
                    date_collected=date_obj,
                    purchase_type=purchase_type,
                    category_id=int(category_id) if category_id else None,
                    attachment_url=attachment_url,
                    notes=notes,
                    paid_on_collection=paid_on_collection
                )
                db.session.add(purchase)
                db.session.flush()
                
                audit_data = {
                    'description': description,
                    'amount': amount,
                    'quantity': quantity,
                    'vendor': vendor,
                    'date_collected': date_collected,
                    'purchase_type': purchase_type,
                    'category_id': category_id,
                    'notes': notes,
                    'paid_on_collection': paid_on_collection
                }
                
                audit_log = AuditLog(
                    purchase_id=purchase.id,
                    user_id=current_user.id,
                    action='create',
                    changes=json.dumps(audit_data)
                )
                db.session.add(audit_log)
                db.session.commit()
                
                flash('Purchase uploaded successfully!', 'success')
                return redirect(url_for('upload'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')
        
        return render_template('upload.html', categories=categories)
    
    @app.route('/dashboard')
    @login_required
    @role_required('admin')
    def dashboard():
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()
        vendor_filter = request.args.get('vendor', '').strip()
        type_filter = request.args.get('type', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        
        query = Purchase.query
        
        if search_query:
            query = query.filter(
                (Purchase.description.contains(search_query)) | 
                (Purchase.vendor.contains(search_query))
            )
        
        if category_filter:
            query = query.filter_by(category_id=int(category_filter))
        
        if vendor_filter:
            query = query.filter_by(vendor=vendor_filter)
        
        if type_filter:
            query = query.filter_by(purchase_type=type_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Purchase.date_collected >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Purchase.date_collected <= date_to_obj)
            except ValueError:
                pass
        
        purchases = query.order_by(Purchase.date_collected.desc()).all()
        
        total_spend = db.session.query(
            func.sum(Purchase.amount * Purchase.quantity)
        ).scalar() or 0
        
        category_totals = db.session.query(
            Category.name,
            func.sum(Purchase.amount * Purchase.quantity)
        ).join(Purchase).group_by(Category.name).all()
        
        vendor_totals = db.session.query(
            Purchase.vendor,
            func.sum(Purchase.amount * Purchase.quantity)
        ).group_by(Purchase.vendor).order_by(
            func.sum(Purchase.amount * Purchase.quantity).desc()
        ).limit(10).all()
        
        type_totals = db.session.query(
            Purchase.purchase_type,
            func.sum(Purchase.amount * Purchase.quantity)
        ).group_by(Purchase.purchase_type).all()
        
        monthly_totals = db.session.query(
            extract('year', Purchase.date_collected).label('year'),
            extract('month', Purchase.date_collected).label('month'),
            func.sum(Purchase.amount * Purchase.quantity).label('total')
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        categories = Category.query.all()
        vendors = db.session.query(Purchase.vendor).distinct().all()
        
        return render_template(
            'dashboard.html',
            purchases=purchases,
            total_spend=total_spend,
            category_totals=category_totals,
            vendor_totals=vendor_totals,
            type_totals=type_totals,
            monthly_totals=monthly_totals,
            categories=categories,
            vendors=[v[0] for v in vendors],
            filters={
                'search': search_query,
                'category': category_filter,
                'vendor': vendor_filter,
                'type': type_filter,
                'date_from': date_from,
                'date_to': date_to
            }
        )
    
    @app.route('/export')
    @login_required
    @role_required('admin')
    def export():
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()
        vendor_filter = request.args.get('vendor', '').strip()
        type_filter = request.args.get('type', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        
        query = Purchase.query
        
        if search_query:
            query = query.filter(
                (Purchase.description.contains(search_query)) | 
                (Purchase.vendor.contains(search_query))
            )
        
        if category_filter:
            query = query.filter_by(category_id=int(category_filter))
        
        if vendor_filter:
            query = query.filter_by(vendor=vendor_filter)
        
        if type_filter:
            query = query.filter_by(purchase_type=type_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Purchase.date_collected >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Purchase.date_collected <= date_to_obj)
            except ValueError:
                pass
        
        purchases = query.order_by(Purchase.date_collected.desc()).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'ID', 'Date', 'Description', 'Vendor', 'Type', 'Category',
            'Quantity', 'Amount', 'Total', 'Paid on Collection', 'Notes', 'Uploaded By'
        ])
        
        for purchase in purchases:
            category_name = purchase.category.name if purchase.category else 'N/A'
            total = purchase.amount * purchase.quantity
            paid = 'Yes' if purchase.paid_on_collection else 'No'
            
            writer.writerow([
                purchase.id,
                purchase.date_collected,
                purchase.description,
                purchase.vendor,
                purchase.purchase_type,
                category_name,
                purchase.quantity,
                f'${purchase.amount:.2f}',
                f'${total:.2f}',
                paid,
                purchase.notes or '',
                purchase.user.username
            ])
        
        output.seek(0)
        return send_file(
            BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'purchases_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
