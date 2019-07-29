import requests
from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=a7d180a81b6355ec075fa4a6a22521da'
        r   =  requests.get(url.format(new_city)).json()
        print(r)
        if r["cod"]=="404":
                return jsonify({"Message":"{}".format(r['message'])})
        else:
        
                return jsonify({"City":"{}".format(new_city),"Temp":"{}".format(r['main']['temp']) 
                        ,"Description":"{}".format(r['weather'][0]['description'])
                         })

if __name__ == '__main__':
    app.run()