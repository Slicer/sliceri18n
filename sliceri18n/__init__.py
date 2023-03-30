import os
from .functions import * 

class Extractor:
  def __init__(self):
    pass
  def extract(self, source_path):
    context_name = get_context(source_path)
    """ extraction is doing on a .py file or 
        on a folder that contain .py files"""
    if os.path.isfile(source_path): # if the function parameter is a file
      extracted_strings = code_to_dict(source_path)
      extraction_result(extracted_strings, context_name)
      dict_to_ts(extracted_strings, source_path)
    elif os.path.isdir(source_path): # if the function parameter is a folder
      py_files = get_all_py_file(source_path) # get all .py file
      big_dict = dict()
      for py_file in py_files:
        try:
          file_dict = code_to_dict(py_file)
          big_dict[py_file] = file_dict
        except Exception as e:
          print("error in extracting file : ",py_file)
          print("\t[–] error : ", e)
      extraction_result(file_dict, context_name)
      dict_to_ts(big_dict, source_path)
