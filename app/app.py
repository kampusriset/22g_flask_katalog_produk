from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from config import Config
from models import mysql, bcrypt, login_manager, User, Product
from forms import RegistrationForm
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mysql.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Route untuk dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    
    # Ambil statistik jumlah barang per kategori
    cur.execute("SELECT category, COUNT(*) as total FROM products GROUP BY category")
    stats = cur.fetchall()
    
    # Ambil semua produk
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    
    cur.close()
    
    return render_template('dashboard.html', stats=stats, products=products)

# Route untuk tambah barang
@app.route('/tambah-barang', methods=['GET', 'POST'])
@login_required
def tambah_barang():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        
        # Proses unggah file
        if 'image' not in request.files:
            flash('Tidak ada file yang diunggah', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('Nama file kosong!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Simpan ke database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO products (name, description, price, image, category) VALUES (%s, %s, %s, %s, %s)", 
                        (name, description, price, filename, category))
            mysql.connection.commit()
            cur.close()
            
            flash('Barang berhasil ditambahkan!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Format file tidak didukung!', 'danger')
    
    return render_template('tambah_barang.html')

# Route untuk registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User()
            user_obj.id = user[0]
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal, periksa username dan password', 'danger')
    
    return render_template('login.html')

@app.route('/edit-barang/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_barang(id):
    cur = mysql.connection.cursor()
    
    # Ambil data barang berdasarkan ID
    cur.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cur.fetchone()
    
    if not product:
        flash("Barang tidak ditemukan!", "danger")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        
        # Jika user mengunggah gambar baru, update gambarnya
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image = filename
            else:
                flash('Format file tidak didukung!', 'danger')
                return redirect(request.url)
        else:
            image = product[4]  # Gunakan gambar lama jika tidak diunggah baru
        
        # Update database
        cur.execute("""
            UPDATE products 
            SET name=%s, description=%s, price=%s, image=%s, category=%s 
            WHERE id=%s
        """, (name, description, price, image, category, id))
        
        mysql.connection.commit()
        cur.close()
        
        flash("Barang berhasil diperbarui!", "success")
        return redirect(url_for('dashboard'))
    
    cur.close()
    return render_template('edit_barang.html', product=product)

@app.route('/hapus-barang/<int:id>', methods=['POST'])
@login_required
def hapus_barang(id):
    cur = mysql.connection.cursor()
    
    # Ambil data barang berdasarkan ID
    cur.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cur.fetchone()
    
    if not product:
        flash("Barang tidak ditemukan!", "danger")
        return redirect(url_for('dashboard'))
    
    # Hapus barang dari database
    cur.execute("DELETE FROM products WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash("Barang berhasil dihapus!", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)