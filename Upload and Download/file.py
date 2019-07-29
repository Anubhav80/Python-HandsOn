import os
from os.path import expanduser
from flask import Flask, render_template,request ,redirect
from werkzeug.utils import secure_filename
app = Flask(__name__)

upload_path = os.path.join(expanduser('~'),'Desktop','Uploads','img')
print(upload_path)
app.config["UPLOADS"] = upload_path
app.config["ALLOWED_FILE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","jpg"]


def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    
    if request.method == "POST":

        if request.files:

            f = request.files["res-file"]

            if f.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_file(f.filename):
                filename = secure_filename(f.filename)

                f.save(os.path.join(app.config["UPLOADS"], filename))

                print("File saved")

                return redirect(request.url)

            else:
                print("That file extension is not allowed")
                return redirect(request.url)
    return render_template("/Upload.html")




if __name__ == '__main__':
    app.run()