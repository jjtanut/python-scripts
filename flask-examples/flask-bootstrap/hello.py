from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return '<h1>Hello world!</h1>'

@app.route('/user/<name>')
def user(name):
    # dynamically generated route
    return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(debug=True) # ensures that dev server is started only when script is executed directly
