import ast
import os
import pathlib

class Extractor:
  def __init__(self):
    pass
  def extract(source_file):
    extracted_strings = code_to_dict(source_file)
    dict_to_ts(extracted_strings, source_file)
  
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

def code_to_dict(source_file):
  words_table = dict()
  with open(source_file, "r") as code:
    tree = ast.parse(code.read())
    path = pathlib.PurePath(os.path.realpath(source_file))
    file_location = os.path.relpath(str(path))

    for node in walk(tree):
      line_of_text = 0
      if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
        # if the Call node is directly the call node of the _() function
          if node.func.id == "_":
            text_extracted = node.args[0].value
            line_of_text = node.lineno
          elif len(node.args)==1 and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
            if node.args[0].func.id=="_":
              text_extracted = node.args[0].args[0].value
              line_of_text = node.lineno
        # if the node is an Attribute and the call node of the _() function is in this node
        if isinstance(node.func, ast.Attribute) and len(node.args)>=1: 
          if isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Name):
            if node.args[0].func.id=="_":
              text_extracted = node.args[0].args[0].value
              line_of_text = node.lineno

        if line_of_text!=0 and line_of_text not in words_table.keys():
          words_table[line_of_text]= [{
            "line": line_of_text,
            "filename": file_location,
            "source": text_extracted
          }]
        elif line_of_text!=0:
          words_table[line_of_text].append({
            "line": line_of_text,
            "filename": file_location,
            "source": text_extracted
          })
  return words_table

def dict_to_ts(dico, source_file):
  context_name = get_context(source_file)
  tsfile_start_template = """<?xml version="1.0" encoding="utf-8"?>
      <!DOCTYPE TS>
      <TS version="2.1">
        <context>
          <name>"""+context_name+"""</name>"""
  tsfile_end_template = """
        </context>
      </TS>"""
  with open(context_name+".ts", "w") as f:
    f.write(tsfile_start_template)
    for msg in dico.values():
      for msg_item in msg:
        message_template = """
          <message>
              <location filename='"""+msg_item['filename']+"""' line='"""+str(msg_item['line'])+"""'/>
              <source>"""+msg_item['source']+"""</source>
              <translation type="unfinished">"""+"""</translation>
          </message>"""
        f.write(message_template)
    f.write(tsfile_end_template)
  
def ts_to_dict(tsfile):
  document = minidom.parse(tsfile)
  messages = document.getElementsByTagName('message')
  words_table = dict()
  for message in messages:
    location = message.getElementsByTagName('location')[0]
    line = location.getAttribute('line')
    filename = location.getAttribute('filename')
    source = message.getElementsByTagName('source')[0].firstChild.data

    if line not in words_table.keys():
      words_table[line] = [{
        "line": line,
        "filename": filename,
        "source": source
      }]
    else:
      words_table[line].append({
        "line": line,
        "filename": filename,
        "source": source
      })
  return words_table

def dict_values_length(dico):
  longueur=0
  for values in dico.values(): longueur+=len(values)
  return longueur

def get_context(source_file):
  with open(source_file, "r") as code:
    tree = ast.parse(code.read())
    classes = [node.name for node in walk(tree) if isinstance(node, ast.ClassDef)]
    path = pathlib.PurePath(os.path.realpath(source_file))
    package_name = str(path.parent.name)
    if len(classes)!=0: context_name = package_name+"."+classes[0]
    else: context_name = source_file[:-3]
  return context_name
