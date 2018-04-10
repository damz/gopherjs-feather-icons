import os
import glob
import lxml.etree
import subprocess

if __name__ == "__main__":
    parser = lxml.etree.XMLParser(remove_blank_text=True)

    def normalize_xml(data):
        root = lxml.etree.XML(data, parser=parser)
        root.insert(
            0,
            root.makeelement("path", {
                "visibility": "hidden",
                "fill": "none",
                "stroke": "none",
                "d": "M0 0 H 24 V 24 H 0 Z",
            })
        )
        return lxml.etree.tostring(root)

    camelize_exceptions = {
        "cpu": "CPU",
    }

    def _camelize(part):
        try:
            return camelize_exceptions[part]
        except KeyError:
            return part[0].upper() + part[1:]

    def camelize(name):
        return "".join(
            _camelize(part)
            for part in name.split("_")
            if part != ""
        )

    with open("icons.go", "wb") as f:
        f.write("package icons\n\n")
        f.write("const (\n")
        for filepath in sorted(glob.glob("feather/icons/*.svg")):
            name = os.path.basename(filepath)[:-len(".svg")].replace("-", "_")
            go_name = camelize(name)

            with open(filepath, "rb") as icon_f:
                data = icon_f.read()

            f.write("\t%s = `%s`\n" % (
                go_name,
                normalize_xml(data),
            ))
        f.write(")\n")

    subprocess.check_call([
        "gofmt", "-w",
        "icons.go",
    ])
