import glob
import os.path
from io import BytesIO
from zipfile import ZipFile

from flask import Flask, send_file, request
from flask_restful import Resource, Api
from flask_restful import reqparse

from data.csv2pkl_api import generate_csv2pkl
from geotracknet_api import get_results
from helpers import generate_csvs

app = Flask(__name__)
app.config["OUTPUT_FOLDER"] = "./output"

api = Api(app, prefix="/api/v1")


parser = reqparse.RequestParser()
parser.add_argument("tracks", type=list, location="json", required=True)


class Track(Resource):
    def get(self):
        return {"message": "Welcome to Tracker API", "status": 200}

    def post(self):
        args = parser.parse_args()
        if args["tracks"] and isinstance(args["tracks"], list):
            # generate csv
            generate_csvs(args["tracks"])
            # generate pkls
            generate_csv2pkl()
            # get files, csv and png
            get_results()
            stream = BytesIO()
            csv = os.path.join("./results/", "*.csv")
            pngs = os.path.join("./results/", "*.png")
            download = glob.glob(csv)
            download.extend(glob.glob(pngs))
            with ZipFile(stream, 'w') as zf:
                for file in download:
                    zf.write(file, os.path.basename(file))
            stream.seek(0)

            return send_file(
                stream,
                as_attachment=True,
                download_name='output.zip'
            )

        else:
            return {"Error": "File not supported or file has issues."}


api.add_resource(Track, "/track")


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=False)
