import os

from bs4 import BeautifulSoup

#missing: SCRIPT NODE

INDEX = os.path.join("..","blender_manual_v400_en.html")
NODES_EXT = {
    "shader": os.path.join("render", "shader_nodes")
}

if __name__=="__main__":

    for key, value in NODES_EXT.items():
        
        for subdir in [f.name for f in os.scandir(os.path.join(INDEX, value)) if f.is_dir()]:

            ...

            html = open(os.path.join(INDEX, value, "index.html"))
            S = BeautifulSoup(html, 'lxml')

        for T in S.recursiveChildGenerator():
            if T.name: print(T.name)