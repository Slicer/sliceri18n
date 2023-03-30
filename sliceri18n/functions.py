from xml.dom import minidom
import ast
import os
import pathlib


def code_to_dict(source_file):
  """ Transform source code (extracted strings, line numbers,  location) 
  to dictionnary after parsing it with ast module. """
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

def ts_context_item(context_name, source_file, dico):
  message_template = \
  '\t<context>\n' \
  '\t\t<name>' + context_name + '</name>\n'

  for msg in dico.values():
    for msg_item in msg:
      relative_path = get_relative_path(source_file, msg_item['filename'])
      message_template += \
        '\t\t<message>\n' \
            '\t\t\t<location filename="' + relative_path + '" line="' + str(msg_item['line']) + '"/>\n' \
            '\t\t\t<source><![CDATA[' + msg_item['source'] + ']]></source>\n' \
            '\t\t\t<translation type="unfinished"></translation>\n' \
        '\t\t</message>\n'
  message_template +=  '\t</context>\n'

  return message_template

def dict_to_ts(dico, source_file, filename="slicer.ts"):
  if not dico:
    print("Error : the specified file doesn't contain any marked string")
    return

  tsfile_start_template = \
    '<?xml version="1.0" encoding="utf-8"?>\n' \
    '<!DOCTYPE TS>\n' \
    '<TS version="2.1">\n'

  tsfile_end_template = '</TS>'

  with open(filename, "w") as f:
    f.write(tsfile_start_template)
    message_template = ''
    if not is_big(dico):
      context_name = get_context(source_file)
      message_template = ts_context_item(context_name, source_file, dico)
    else:
      for py_file in dico.keys():
        minidico = dico[py_file]
        if minidico:
          context_name = get_context(py_file)
          message_template += ts_context_item(context_name, source_file, minidico)
    f.write(message_template)
    f.write(tsfile_end_template)

def ts_to_dict(tsfile):
  """ transform .ts file containing extracted strings to a dictionnary"""
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
  """ get dictionnary values length (values are lists)"""
  longueur=0
  if not is_big(dico):
    for values in dico.values(): longueur+=len(values)
  else :
    for minidict in dico.values():
      for values in minidict.values(): longueur+=len(values)
  return longueur

def get_context(source_file):
  """ get context name based on source code file/folder"""
  if os.path.isfile(source_file):
    parent_folder = os.path.dirname(source_file)
    init_file_path = parent_folder + os.path.sep + '__init__.py'

    if os.path.isfile(init_file_path):
      context_name = os.path.basename(parent_folder)
      context_name += '.' + os.path.basename(source_file).replace('.py', '');
      return context_name
    else:
      return os.path.basename(source_file).replace('.py', '')
  else:
    return os.path.basename(source_file)

def get_all_py_file(folder):
  """get all .py file in a folder"""
  all_py_files = list()
  for dirpath, dirnames, filenames in os.walk(folder):
    for filename in [f for f in filenames if f.endswith(".py")]:
      f = os.path.join(dirpath, filename)
      all_py_files.append(f)
  return all_py_files 

def is_big(dico):
  """ verify if the parameter is a big dictionnary 
  (when the dictionnary values is other dictionnaries) or not"""
  for i in dico.values():
    if isinstance(i, dict):
      return True
    else:
      return False

def extraction_result(dico, context_name):
  """show the extraction results 
  (number of extracted strings, deleted strings, new added strings)"""
  tsfile = context_name+".ts"
  current_length = dict_values_length(dico)
  current_val = getValues(dico)
  added = 0
  deleted = 0
  if os.path.exists(tsfile):
    previous_dict = ts_to_dict(tsfile)
    previous_length = dict_values_length(previous_dict)
    old_val = getValues(previous_dict)
    if previous_length > current_length:
      deleted = previous_length - current_length
    elif previous_length < current_length:
      added = current_length - previous_length
    else:
      for val in old_val:
        if not val in current_val:
          deleted+=1
      for val in current_val:
        if not val in old_val:
          added+=1
    print(added," new string(s)\n", deleted, "string(s) deleted")
    print("total : ", current_length, "string(s)")
  else : # .ts file not already exist
    added = current_length
    print(added," new string(s)")

def getValues(dico):
  """ get dictionary values"""
  val_liste = []
  if not is_big(dico):
    for val in dico.values():
      val_liste+=[item for item in val]
  else:
    for minidico in dico.values():
      for val in minidico.values():
        val_liste+=[item for item in val]
  return val_liste

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

def get_relative_path(root_path, full_path):
  root_path = os.path.abspath(root_path)
  full_path = os.path.abspath(full_path)

  relative_path = full_path.replace(root_path, '').replace('\\', '/')
  relative_path = relative_path[1:] if relative_path.startswith('/') else relative_path

  # print('rel', relative_path, '=>', root_path, ':', full_path)

  return relative_path if relative_path != '' else full_path
