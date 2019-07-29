import os
from os.path import expanduser
from flask import Flask, send_file, send_from_directory, safe_join, abort
app = Flask(__name__)


upload_path = os.path.join(expanduser('~'),'Desktop','Uploads','img')
print(upload_path)
app.config["CLIENT"] = upload_path

@app.route("/get-image/<image_name>")
def get_image(image_name):

    try:
        return send_from_directory(app.config["CLIENT"], filename=image_name, as_attachment=False)
    except FileNotFoundError:
        abort(404)






if __name__ == '__main__':
    app.run()