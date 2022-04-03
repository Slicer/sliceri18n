import ast
import os

# tree = ast.parse(code)
scriptname = os.path.basename(__file__)
scriptlocation = os.path.realpath(__file__)

def walk (node):
    """the walk() function of ast module skips the order, just walks, 
    so tracing is not possible with it, that's why we I redifined it"""
    end = []
    end.append(node)
    for n in ast.iter_child_nodes(node):
        # Consider it a leaf:
        if isinstance(n, ast.Call) and n.func.id=="_":
            end.append(n)
            continue
        end += walk(n)
    return end

def extractor(myfile):
  with open(myfile, "r") as code:
    tree = ast.parse(code.read())
  with open("tsfile.ts", "a") as info:
    info.write("""
      <?xml version="1.0" encoding="utf-8"?>
      <!DOCTYPE TS>
      <TS version="2.1">
        <context>
          <name>"""+scriptname[:-3]+"""</name>
    """)
    for node in walk(tree):
      if isinstance(node, ast.Call):
        if node.func.id=="_":
          text_extracted = node.args[0].value
          line_of_text = str(node.lineno)
          info.write("""
          <message>
              <location filename='"""+scriptlocation+"""' line='"""+line_of_text+"""'/>
              <source>"""+text_extracted+"""</source>
              <translation type="unfinished">"""+"""</translation>
          </message>
          """)
    info.write("""
        </context>
      </TS>
    """)
# call the funcion here
# extractor("your_python_file_name.py")