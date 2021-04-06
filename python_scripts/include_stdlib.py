# requires python >= 3.4
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pathlib import Path

def main():
    p = Path("docs/tremor-script/stdlib")
    template = Path("mkdocs.yml.in")
    output = Path("mkdocs.yml")

    # load mkdocs.yml template
    with template.open() as mkdocs_yaml_in:
        data = load(mkdocs_yaml_in, Loader=Loader)
        function_reference = []
        for nav_entry in data["nav"]:
            if "Tremor Script" in nav_entry:
                for script_nav_entry in nav_entry["Tremor Script"]:
                    fr = script_nav_entry.get("Function Reference")
                    if fr is not None:
                        function_reference = fr
        # clean function_reference
        function_reference.pop()

    # including files in nav
    files = list(p.glob('**/*.md'))
    for f in files:
        print(f"Adding file: {f}")
        f_rel = f.relative_to(p)
        pparts = list(f_rel.parent.parts)
        pparts.append(f_rel.stem)
        name = "::".join(pparts)
        filename = f.relative_to("docs")

        function_reference.append({
            name: str(filename)
        })

    # write out mkdocs.yml
    with output.open("w") as mkdocs_yaml:
        mkdocs_yaml.write(dump(data, Dumper=Dumper))



if __name__ == "__main__":
    main()
