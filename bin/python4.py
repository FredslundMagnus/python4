import re
from sys import argv, exit
from os.path import join
args = argv[1:]

def pattern2regex(pattern: str) -> tuple[str, list[str]]:
    result = ""
    is_in_capture = False
    captures = []
    for char in pattern:
        if is_in_capture:
            if char == ")":
                result += "\w*"
                result += char
                is_in_capture = False
            else:
                captures[-1] += char

        else:
            if char != "(":
                result += "[" + char + "]"
            else:
                captures.append("")
                result += char
                is_in_capture = True

    return f"({result})", captures

if len(args) == 0:
    print("""
--- Welcome to Python 4!
--- Please enter a file name when running the command fx: 'python4 main.py4'
""")
    quit(1)

macros = {}
infixes = {}

def compile(filename: str, folder: str):
    with open(join(folder, filename), "r", encoding="utf8") as f:
        file = f.readlines()

    with open(join(folder, filename[:-1]), "w", encoding="utf8") as f:
        for line in file:
            words = line.split(" ")
            if words[0] == "from" and words[2] == "import" and words[3].startswith("*"):
                *folders, file = words[1].split(".")
                new_folder = join(folder, *folders)
                try:
                    compile(f"{file}.py4", new_folder)
                except FileNotFoundError as e:
                    print(e)
                f.write(line)
                continue

            if words[0] == 'macro':
                if words[1].endswith(":") or words[1].endswith(":\n"):
                    f.write(f"def macro_{len(macros)}(x: str):\n")
                    pattern, captures = pattern2regex(words[1].split(":")[0])
                else:
                    f.write(f"def macro_{len(macros)}(x: str) " + " ".join(words[2:]))
                    pattern, captures = pattern2regex(words[1])
                n = f"macro_{len(macros)}"
                
                def __(n):
                    def _(x):
                        y = [f"'{v}'" for v in x]
                        return n + f"({', '.join(y)})"
                    return _
                macros[pattern] = __(n)
                continue
            if words[0] == 'infix':
                symbol = words[1].split("(")[0]
                if words[1].split("("):
                    pass
                infixes[symbol] = lambda a, b: f"{a}.__circle_cross__({b})"
                continue
            for pattern, fun in macros.items():
                for concrete, *args in re.findall(pattern, line):
                    line = line.replace(concrete, fun(args))
            for symbol, fun in infixes.items():
                if line[-1] == "\n":
                    line = line[:-1]
                while symbol in line:
                    parts = line.split(" ")
                    i = parts.index(symbol)
                    line = line.replace(" ".join(parts[i-1:i+2]), fun(parts[i-1], parts[i+1]))
                    # print("sdfsd", line)
                line += "\n"
            
            f.write(line)
*folders, filename = args[0].split("/")
compile(filename, "/".join(folders))