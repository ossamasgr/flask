import os
import asyncio
import sys
import xmltodict as xmltodict
import pandas as pd
import json
from flask import Flask, request, abort, jsonify, send_from_directory

def convert(file):
    with open(file, encoding='utf_8') as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()

        # generate the object using json.dumps()
        # corresponding to json data

        json_data = json.dumps(data_dict)

        # Write the json data to output
        # json file
        with open("CvTest.json", "w", ) as json_file:
            json_file.write(json_data)
            json_file.close()

        with open('CvTest.json') as f:
            d = json.load(f)
        df = pd.json_normalize(d)
        df = df.to_dict('records')
        df = pd.json_normalize(df)
        data = df.to_json("file.json", orient="records")

    with open('file.json', 'r') as data_file:
        data = json.load(data_file)

    for element in data:
        element.pop('cv.@xmlns', None)

    for element in data:
        element.pop('cv.binaryDocuments.document', None)
    with open('templates/data.json', 'w') as data_file:
        data = json.dump(data, data_file)

    with open('templates/data.json', 'r') as data_file:
        data = json.load(data_file)

    output = pd.DataFrame(data, columns=["cv.personalInformation.firstname",
                                         "cv.personalInformation.lastname",
                                         "cv.personalInformation.gender.code",
                                         "cv.personalInformation.gender.name",
                                         "cv.personalInformation.title",
                                         "cv.personalInformation.isced.code",
                                         "cv.personalInformation.isced.name",
                                         "cv.personalInformation.birthyear",
                                         "cv.personalInformation.civilState"
                                         "cv.personalInformation.address.street",
                                         "cv.personalInformation.address.postcode",
                                         "cv.personalInformation.address.city",
                                         "cv.personalInformation.address.country.code",
                                         "cv.personalInformation.address.country.name",
                                         "cv.personalInformation.address.state",
                                         "cv.personalInformation.email",
                                         "cv.personalInformation.phoneNumber",
                                         "cv.personalInformation.homepage",
                                         "cv.work.phase",
                                         "cv.work.additionalText",
                                         "cv.education.phase",
                                         "cv.education.additionalText",
                                         "cv.additionalInformation.language",
                                         "cv.additionalInformation.competences",
                                         "cv.additionalInformation", ])
    output.to_csv('data.csv')
    return jsonify(data)


UPLOAD_DIRECTORY = "templates"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


api = Flask(__name__)


@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)
    return convert(os.path.join(UPLOAD_DIRECTORY,filename))
    # Return 201 CREATED
    return "", 201


if __name__ == "__main__":
    api.run(debug=True)
