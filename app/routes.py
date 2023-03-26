from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import PhoneForm, SignUpForm, LoginForm
from app.models import Phone, User
from flask_login import login_user, logout_user, login_required, current_user
from flask_login import UserMixin

@app.route('/', methods = ["GET","POST"])
def index():
    phone = Phone.query.all()
    

    
           
     
    return render_template('index.html', phone=phone)



@app.route('/signup', methods=["GET","POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():

        email = form.email.data
        username = form.username.data
        password = form.password.data

        check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
        if check_user:
            flash("A user with that username or email already exists","warning")
            return redirect(url_for('signup'))
        new_user = User(email=email, username=username, password=password)
        flash(f"Thank you {new_user.username} for signing up!", "success")
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)
        
                            
    


@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            flash (f"You have logged in as {username}",'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password is invalid', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out", "info")
    return redirect(url_for('index'))


@app.route('/enterphone', methods=["GET","POST"])
@login_required
def enterphone():

    form = PhoneForm()

    if form.validate_on_submit():
        
        first_name = form.first_name.data 
        last_name = form.last_name.data
        phone = form.phone.data
        address = form.address.data
        
        check_phone = db.session.execute(db.select(User).filter(Phone.phone == phone)).scalars().all()
        if check_phone:
            flash('That number already exists in our databse')
            return redirect(url_for('enterphone'))
        newnum = Phone(first_name = first_name, last_name = last_name, phone = phone, address = address,user_id=current_user.id)
        flash(f'Thank you for adding {newnum.phone} to the matrix')
        return redirect(url_for('index'))   
    
    return render_template('enterphone.html', form = form)



@app.route('/edit/<phone_id>', methods=["GET","POST"])
@login_required
def edit(phone_id):
    form = PhoneForm()

    editphone = Phone.query.get_or_404(phone_id)

    if editphone.author != current_user:
        flash("You do not have permission to edit this entry", "danger")
        return redirect(url_for('index')) 

    if form.validate_on_submit():
        #print out form info in terminal and redirect to home page
        editphone.first_name = form.first_name.data 
        editphone.last_name = form.last_name.data
        editphone.phone = form.phone.data
        editphone.address = form.address.data
        db.session.commit()

        flash (f'The entry for {editphone.phone} has been updated')
        return redirect(url_for('index'))

    
    form.first_name.data = editphone.first_name 
    form.last_name.data = editphone.last_name
    form.phone.data = editphone.phone
    form.address.data = editphone.address

    return render_template('edit.html', form = form, phone = editphone)

@app.route('/delete/<phone_id>')
@login_required
def delete(phone_id):
    deletephone = Phone.query.get_or_404(phone_id)
    if deletephone.author != current_user:
        flash("You do not have permission to delete this entry","danger")
        return redirect(url_for('index'))
    
    db.session.delete(deletephone)
    db.session.commit()
    flash(f"{deletephone.phone} has been deleted", "info")
    return redirect(url_for('index'))