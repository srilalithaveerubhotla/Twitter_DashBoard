
from flask import Flask ,render_template
from flask_restful import Resource, Api
import twitter_tools as tt
app = Flask(__name__,template_folder='templates')
api = Api(app)

@app.route("/")
def get():
    return render_template('templates.html', info=tt.twitter_get('srilalithaveer1'))

@app.route('/', methods=['POST'])
def my_form_post(message):
    text = request.form['text']
    processed_text = text.upper(tt.twitter_put('srilalithaveer1',message))
    return render_template('templates.html',info=processed_text)

@app.route('/', methods=['DELETE'])
def delete_post(message):
    text = request.form['text']
    processed_text = text.upper(tt.twitter_delete('srilalithaveer1',message))
    return render_template('templates.html',info=processed_text)



if __name__ == "__main__":
    app.run(debug=True)
























