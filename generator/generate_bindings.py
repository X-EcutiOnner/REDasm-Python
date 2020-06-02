#! /bin/python3

from pathlib import Path
import json
import xml
import sys


def generate_category(categoryname, catobj, outputdir):
    src = [f'#include "rdapi_{categoryname}.h"',
           f'#include "rdapi_all.h"',
           "\n",
           f"void bind{categoryname.capitalize()}(pybind11::module& m) {{"]

    for f in catobj["functions"]:
        n = f["name"]

        accepted = True

        for arg in f["args"]:
            if arg["type"].endswith("**"):
                accepted = False

        if accepted:
            src.append("\t" + f'm.def("{n}", &{n});')

    src.append("}")

    with open(Path(outputdir, f"rdapi_{categoryname}.cpp"), "w") as f:
        f.write("\n".join(src))


def generate_rdpython(jsondoc, outputdir):
    with open(Path(outputdir, f"rdapi_rdpython.cpp"), "w") as f:
        f.write("#include <pybind11/pybind11.h>\n")

        for c, obj in jsondoc["categories"].items():
            if not obj["functions"]:  # Skip categories with no functions
                continue
            f.write(f'#include "rdapi_{c.lower()}.h"' + "\n")

        f.write("\n")
        f.write(f"void bindRDPython(pybind11::module& m) {{" + "\n")

        for c, obj in jsondoc["categories"].items():
            if not obj["functions"]:  # Skip categories with no functions
                continue
            f.write("\t" + f"bind{c.lower().capitalize()}(m);" + "\n")

        f.write("}")

def generate_bindings(docfilepath, outputdir):
    with open(docfilepath, "r") as f:
        jsondoc = json.load(f)

    outdir = Path(outputdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for category, obj in jsondoc["categories"].items():
        if not obj["functions"]:  # Skip categories with no functions
            continue

        lccategory = category.lower()

        with open(Path(outdir, f"rdapi_{lccategory}.h"), "w") as f:
            f.write("#pragma once\n\n")
            f.write("#include <pybind11/pybind11.h>\n\n")
            f.write(f"void bind{category}(pybind11::module& m);")

        generate_category(lccategory, obj, outputdir)

    generate_rdpython(jsondoc, outputdir)



if __name__ == "__main__":
    generate_bindings(sys.argv[1], sys.argv[2])