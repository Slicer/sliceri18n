import os
from .functions import * 

class Extractor:
  def __init__(self):
    pass
  def extract(param):
    context_name = get_context(param)
    if os.path.isfile(param): # if the function param is a file
      extracted_strings = code_to_dict(param)
      extraction_result(extracted_strings, context_name)
      dict_to_ts(extracted_strings, param)
    elif os.path.isdir(param): # if the function param is a folder
      py_files = get_all_py_file(param) # get all .py file
      big_dict = dict()
      for py_file in py_files:
        try:
          file_dict = code_to_dict(py_file)
          big_dict[py_file] = file_dict
        except Exception as e:
          print("error in extracting file : ",py_file)
          print("\t[–] error : ", e)
      extraction_result(extracted_strings, context_name)
      dict_to_ts(big_dict, context_name)
