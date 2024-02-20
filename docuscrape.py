import os

from bs4 import BeautifulSoup

#missing: SCRIPT NODE

INDEX = os.path.join("..","blender_manual_v400_en.html")
NODES_EXT = {
    "shader": os.path.join("render", "shader_nodes")
}

if __name__=="__main__":

    nodes = []

    for key, value in NODES_EXT.items():
        
        for subdir in [f.name for f in os.scandir(os.path.join(INDEX, value)) if f.is_dir()]:

            for file in os.scandir(os.path.join(INDEX, value, subdir)):
                fn = file.name
                if fn == "index.html": continue
                bs = BeautifulSoup(open(os.path.join(INDEX, value, subdir, fn)), 'lxml')
                for T in bs.recursiveChildGenerator():
                    if T.name == "h1":
                        print(key, subdir, T.text[:-1])

                        