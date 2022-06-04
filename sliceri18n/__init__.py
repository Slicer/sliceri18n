import os
from .functions import * 

class Extractor:
  def __init__(self):
    pass
  def extract(param):
  # if the function param is a file :
    if os.path.isfile(param):
      extracted_strings = code_to_dict(param)
      extraction_result(extracted_strings, param)
      dict_to_ts(extracted_strings, param)
    # if the function param is a folder
    elif os.path.isdir(param):
    #1. get all .py file
      py_files = get_all_py_file(param)
    #2. use code_to_dict function and get a big dictionnary
      big_dict = dict()
      for py_file in py_files:
        try:
          file_dict = code_to_dict(py_file)
          big_dict[py_file] = file_dict
        except Exception as e:
          print("error in extracting file : ",py_file)
          print("\t[–] error : ", e)
      extraction_result(extracted_strings, "testfile.py")
      dict_to_ts(big_dict, "testfile.py")
