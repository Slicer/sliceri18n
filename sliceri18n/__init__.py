import ast
import os
import pathlib

class Extractor:
  def __init__(self):
    pass
  def extract(myfile):
    text_extracted=""
    line_of_text=0
    with open(myfile, "r") as code:
      tree = ast.parse(code.read())
      classes = [node.name for node in walk(tree) if isinstance(node, ast.ClassDef)]
      path = pathlib.PurePath(os.path.realpath(myfile))
      package_name = str(path.parent.name)
      if len(classes)!=0: context_name = package_name+"."+classes[0]
      else: context_name = myfile[:-3]
      file_location = os.path.relpath(str(path))
    with open(context_name+".ts", "w") as info:
      info.write("""
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE TS>
        <TS version="2.1">
          <context>
            <name>"""+context_name+"""</name>
      """)
      for node in walk(tree):
        if isinstance(node, ast.Call):
          # if the Call node is directly the call node of the _() function
          if isinstance(node.func, ast.Name):
              if node.func.id == "_":
                text_extracted = node.args[0].value
                line_of_text = node.lineno
                print(text_extracted, " ligne ", node.lineno)
                info.write("""
                <message>
                    <location filename='"""+file_location+"""' line='"""+str(line_of_text)+"""'/>
                    <source>"""+text_extracted+"""</source>
                    <translation type="unfinished">"""+"""</translation>
                </message>
                """)
              elif len(node.args)==1 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
                if node.args[0].func.id=="_":
                  text_extracted = node.args[0].args[0].value
                  line_of_text = node.lineno
                  print(text_extracted, " ligne ", node.lineno)
                  info.write("""
                  <message>
                      <location filename='"""+file_location+"""' line='"""+str(line_of_text)+"""'/>
                      <source>"""+text_extracted+"""</source>
                      <translation type="unfinished">"""+"""</translation>
                  </message>
                  """)
          # if the node is an Attribute and the call node of the _() function is in this node
          if isinstance(node.func, ast.Attribute) and len(node.args)>=1: 
            if isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
              if node.args[0].func.id=="_":
                text_extracted = node.args[0].args[0].value
                line_of_text = node.lineno
                print(text_extracted, " ligne ", node.lineno)
                info.write("""
                <message>
                    <location filename='"""+file_location+"""' line='"""+str(line_of_text)+"""'/>
                    <source>"""+text_extracted+"""</source>
                    <translation type="unfinished">"""+"""</translation>
                </message>
                """)
      info.write("""
          </context>
        </TS>
      """)

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