from sliceri18n import Extractor;
import sliceri18n as s

import sys;

if __name__ == '__main__':
	if len(sys.argv) == 2:
		slicer_path = sys.argv[1];
		extractor = Extractor();
		extractor.extract(slicer_path);

		print("\nExtraction process finished");
	else:
		print("Error: you must specify the slicer root path or the filename as argument");