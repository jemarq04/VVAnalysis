import json
import glob
import argparse
import datetime
from collections import OrderedDict

def readAllJson(json_file_path):
    json_info = {}
    for json_file in glob.glob(json_file_path):
        json_info.update(readJson(json_file))
    return json_info
def readJson(json_file_name):
    json_info = {}
    with open(json_file_name) as json_file:
        try:
            json_info = json.load(json_file)
        except ValueError as err:
            print("Error reading JSON file %s. The error message was:" % json_file_name) 
            print(err)
    return json_info
def getDefaultParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selection", type=str,
                        required=True, help="Name of selection to make, "
                        " as defined in Cuts/<analysis>/<selection>.json")
    parser.add_argument("-v", "--version", type=str,
                        required=False, default="1",
                        help="Version number, appended to name")
    parser.add_argument("-a", "--analysis", type=str,
                        required=False, default="ZZ4l2022",
                        help="Analysis name, used in selecting the cut json")
    parser.add_argument("-f", "--filenames", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["ZZ4l2022"], help="List of input file names, "
                        "as defined in ZZ4lDatasetManager, separated "
                        "by commas")
    return parser
