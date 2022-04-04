import ast
import os

# tree = ast.parse(code)
scriptname = os.path.basename(__file__)
scriptlocation = os.path.realpath(__file__)

def walk (node):
    """ast.walk() skips the order, just walks, so tracing is not possible with it."""
    end = []
    end.append(node)
    for n in ast.iter_child_nodes(node):
        # Consider it a leaf:
        if isinstance(n, ast.Call):
            end.append(n)
            continue
        end += walk(n)
    return end

def extractor(myfile):
  text_extracted=""
  with open(myfile, "r") as code:
    tree = ast.parse(code.read())
  with open("tsfile.ts", "w") as info:
    info.write("""
      <?xml version="1.0" encoding="utf-8"?>
      <!DOCTYPE TS>
      <TS version="2.1">
        <context>
          <name>"""+scriptname[:-3]+"""</name>
    """)
    for node in walk(tree):
      if isinstance(node, ast.Call):
        # if the Call node is directly the call node of the _() function
        if isinstance(node.func, ast.Name):
            if node.func.id == "_":
              text_extracted = node.args[0].value
              print(text_extracted, " ligne ", node.lineno)
            elif len(node.args)==1 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
              if node.args[0].func.id=="_":
                text_extracted = node.args[0].args[0].value
            print(text_extracted, " ligne ", node.lineno)
        # if the node is an Attribute and the call node of the _() function is in this node
      if isinstance(node.func, ast.Attribute) and len(node.args)>=1: 
        if isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
            if node.args[0].func.id=="_":
              text_extracted = node.args[0].args[0].value
              print(text_extracted, " ligne ", node.lineno)
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
# extractor("your_python_file.py")