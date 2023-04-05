import yaml
import sys


def main(fn):
    file = open(fn, "r")
    data = yaml.safe_load(file)
    print("solid pepakura")
    for obj in data["geometry"]:
        vertices = obj["vertices"]
        indices = []
        for elem in obj["shapes"]:
            indices.append([sub["index"] for sub in elem["points"]])
        for facet in indices:
            print("facet normal 0 0 0")
            print("  outer loop")
            for elem in facet[:3]:
                print("    vertex %f %f %f" % tuple([x * 0.1 for x in vertices[elem]]))
            print("  endloop")
            print("endfacet")

            if len(facet) == 4:
                print("facet normal 0 0 0")
                print("  outer loop")
                for elem in [facet[0]] + facet[2:]:
                    print(
                        "    vertex %f %f %f" % tuple([x * 0.1 for x in vertices[elem]])
                    )
                print("  endloop")
                print("endfacet")
    print("endsolid")


if __name__ == "__main__":
    main(sys.argv[1])
