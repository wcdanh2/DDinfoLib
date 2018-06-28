import json
import os


def get_json(DDPath):
    """ Return full JSON data for diseases

    Args:
        DDPath (str): path to the Darkest Dungeon data files


    Returns:
        fulljson (json): entire JSON data from specified file
    """

    quirklib = "SHARED/QUIRK/quirk_library.json"
    libpath = os.path.join(DDPath, quirklib)
    if os.path.exists(libpath):
        fulljson = {}
        with open(libpath, "r") as libfile:
            fulljson = json.loads(libfile.read())
        return fulljson
    else:
        return {}


def get_disease_info(path):
    dlist = [d for d in get_json(path).get("quirks", None) if d["is_disease"]]
    if len(dlist) > 0:
        dinfo = {}
        for disease in dlist:
            dinfo[disease.get("id", None)] = disease.get("buffs", None)
        return dinfo
    else:
        return {}


if __name__ == "__main__":
    DDPath = ""
    with open("diseases.json", "w") as outfile:
        json.dump(get_disease_info(DDPath), outfile, indent=4)
