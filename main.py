import flask
from flask_restful import Resource, Api, request
import concrete_column

app = flask.Flask(__name__)
api = Api(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        x = {}
        x.update(request.json)

        x = concrete(x)
        print(x)
        print(request.json)
        print('test2')
        return x
    else:
        x = {'sectionType': 'Circular', 'Diameter': '200', 'Breadth': '1000', 'Depth': '15', 'Reinforcement': '8N20',
             'output': ['Test'], 'fc':'32','fsy':'500','cover':'30'}
        print('test1')
        return x
def concrete(x):
    try:
        if x['sectionType'] == 'Circular':
            print('hello')
            C = concrete_column.Column(x['sectionType'],int(x['Diameter']),0,0,x['Reinforcement'],int(x['fc']),int(x['fsy']),int(x['cover']))
            print('success')
            x['output'] = C.values
            print(C.Squash_point())
            print(C.Ag)
    except:
        x['output'] = 'Provide values'
        print('yes')
    return x


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)