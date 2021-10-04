# init.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

from flask_login import UserMixin
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect,url_for,request
from flask_login import login_required, current_user


###########
from predictor import predict
###########


db = SQLAlchemy()


app = Flask(__name__)

app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql5440104:hCstjdZk4x@54.84.79.252/sql5440104'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# from models import Users

'''

'''


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))    

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	topic = db.Column(db.String(100), unique=True)
	text = db.Column(db.String(100))
	user_id = db.Column(db.String(1000))
	comments = db.Column(db.String(100000))

@login_manager.user_loader
def load_user(user_id):
    
    return Users.query.get(int(user_id))

# from auth import auth as auth_blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    try:
        alt = current_user.id

        return redirect(url_for('main.profile'))

    except:
        return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Users.query.filter_by(username=email).first()

    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = Users.query.filter_by(username=email).first() 

    if user: 
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))


    new_user = Users(username=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



app.register_blueprint(auth)

# from main import main as main_blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
	# print(current_user.name)
	# return redirect(url_for('main.discuss'))
	return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
	userID = int(current_user.id)
	result = db.engine.execute("SELECT * FROM posts WHERE posts.user_id ="+str(userID))
	posts_list = [[row[1],row[2]] for row in result]
	
	return render_template('profile.html', name=current_user.name,user_posts = posts_list)


####################################

@main.route('/discuss')
def discuss():
	result = db.engine.execute("SELECT * FROM posts")
	posts_list = [[row[0],row[1],row[2]] for row in result]
	comments = db.engine.execute("SELECT * FROM comments")
	comment_list = [[com[1],com[3],com[4]] for com in comments]
	return render_template('discuss.html',posts=posts_list,comments = comment_list)


@main.route('/storepost', methods=['POST'])
@login_required
def storePost():
	question = request.form.get('query')
	question_topic = request.form.get('heading')
	userID = int(current_user.id)
	result = db.engine.execute("INSERT into posts(topic,text,user_id) VALUES('"+question_topic+"','"+question+"','"+str(userID)+"')")
	# db.session.commit()
	return redirect(url_for('main.discuss'))

@main.route('/postcomment', methods=['POST'])
@login_required
def postComment():
	comment = request.form.get('comment')
	post_id = request.form.get('postID')
	userID = int(current_user.id)
	username = current_user.name
	ml_score = predict(str(comment))
	print(ml_score)
	if ml_score['score'] > 0.7:
		result = db.engine.execute("INSERT into comments(comments,userid,username,postid) VALUES('"+str(comment)+"','"+str(userID)+"','"+username+"','"+post_id+"')")
		# db.session.commit()
	else:
		with open('negative_comments.txt', 'a') as fd:
			fd.write(f'\n{str(comment)}')
		flash('The comment is inappropriate and would affect the morale of the Individual and positivity of the Forum')
	return redirect(url_for('main.discuss'))

#####################################################


@main.route("/flowchart")
def flowchart():
	return render_template("flowchart.html")

app.register_blueprint(main)





if __name__ == '__main__':
    app.run(debug=True)    