from flask import Flask, request, jsonify, render_template
import util 

app = Flask(__name__)

util.load_saved_artifacts()

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        price = request.form['price']
        location = request.form['location']
        carpet_area = float(request.form['carpet_area'])
        floor = request.form['floor']
        transaction = request.form['transaction']
        furnishing = request.form['furnishing']
        facing = request.form['facing']
        overlooking = request.form['overlooking']
        bathroom = int(request.form['bathroom'])
        balcony = int(request.form['balcony'])
        ownership = request.form['ownership']

        estimated_price = util.get_estimated_price(price,location, carpet_area, floor, transaction, furnishing, facing, overlooking, bathroom, balcony, ownership)

        return render_template("predict_home_price.html", result=estimated_price)
    else:
        locations = util.get_location_names()
        return render_template("app.html", locations=locations)


if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    util.load_saved_artifacts()
    app.run()