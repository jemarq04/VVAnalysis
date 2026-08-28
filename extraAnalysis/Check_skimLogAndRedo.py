import json
import os
import sys

# Usage: python Check_skimLogAndRedo.py folder year json_file

common_err = (
    "WARNING: In non-interactive mode release checks e.g. deprecated releases, production architectures are disabled."
)
# Dir must be the root /nfs_scratch/<user>/<farmout_job_folder> for correct identification of folders
dir = sys.argv[1]
redolist = []
for root, _, files in os.walk(dir):
    for name in files:
        if "skim-" in name and ".err" in name:
            path = os.path.join(root, name)
            text = []
            with open(path) as ferr:
                for line in ferr:
                    text.append(line.rstrip())
            if (text[0] not in common_err) or len(text) > 1:
                print("\nsomething happening with", path)
                redolist.append(path.split("/")[1])
                print("Error Log:")
                print()
                for item in text:
                    print(item)

# Redo the whole dataset if one file has issue
redolist = list(set(redolist))
print("Redo needed:")
print(redolist)

year = sys.argv[2]
# should end with .json
json_name = sys.argv[3]
rm_name = "cleanFailed_" + json_name.replace(".json", ".sh")

with open(f"/hdfs/store/user/hhe62/{rm_name}", "w") as frm:
    for item in redolist:
        frm.write(f"rm -r {item}\n")

os.system(f"chmod u+x /hdfs/store/user/hhe62/{rm_name}")
print(f"/hdfs/store/user/hhe62/{rm_name} created")

with open(f"/hdfs/store/user/hehe/{json_name}") as json_file:
    obj = json.load(json_file)

# remove dataset that doesn't need resubmit from josn file
match = False
for key in obj:
    match = False
    for item in redolist:
        if key in item:
            match = True

    if not match:
        del obj[key]

with open(f"/hdfs/store/user/hehe/Resubmit_{json_name}", "w") as output_file:
    json.dump(obj, output_file, indent=4)

os.system(
    f"mv /hdfs/store/user/hehe/Resubmit_{json_name} ~/vvanalysis_skim/CMSSW_10_3_1/src/Data_manager/ZZ4lDatasetManager/FileInfo/ZZ4l{year}/ntuples.json"
)
print(
    "New json moved to ~/vvanalysis_skim/CMSSW_10_3_1/src/Data_manager/ZZ4lDatasetManager/FileInfo/ZZ4l{year}/ntuples.json"
)
