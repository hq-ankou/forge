from json import load, loads, dump
#from ujson import dump

import paths

input_file = paths.datasets + "10.5061_dryad.dd56c/classical_interatomic_potentials.json"
output_file = paths.raw_feed + "cip_all.json"
feedsack_size = 10
feedsack_file = paths.sack_feed + "cip_10.json"

#Generator to run through a JSON record and yield the data
#Data is defined as the first layer that isn't a list
#Pseudo-code examples:
#	[ {1}, {2}, {3}] yields {1} then {2} then {3}
#	[ [ {1}, {2} ], [ {[3]}, {4} ] ] yields {1} then {2} then {[3]} then {4}
#	{1} yields {1}
def find_data(record):
	if type(record) is list:
		for elem in record:
			for result in find_data(elem):
				yield result
	else: #Not list, treat as data
		yield record

#Takes a JSON file and converts it into formatter-compatible JSON
#If feed_size > 0, feed_name is required
def convert_json_to_json(in_name, out_name, feed_size=0, feed_name=None, verbose=False):
	if verbose:
		print("Converting JSON from", in_name, "\nDumping results to", out_name)
	with open(in_name, 'r') as in_file:
		if verbose:
			print("Processing")
		list_of_data = []
		try: #If input JSON is human-formatted (with newlines), this will fail
			for line in in_file:
				line_data = loads(line)
				for result in find_data(line_data):
					list_of_data.append(result)
					
		except Exception as err: #Fall back to reading the whole thing at once
			if list_of_data: #If some lines were already processed, is error in JSON
				print("Possible error in JSON:", err)
				list_of_data.clear() #Reset and try again
			if verbose:
				print("Line reading failed, falling back to whole-file processing")
			data = load(in_file)
			for result in find_data(data):
				list_of_data.append(result)

	with open(out_name, 'w') as out_file:		
		if list_of_data:
			if feed_size > 0:
				feed_file = open(feed_name, 'w')
			count = 0
			for datum in list_of_data:
				dump(datum, out_file)
				out_file.write('\n')
				if count < feed_size:
					dump(datum, feed_file)
					feed_file.write('\n')
				count += 1
			print("Data written successfully")
		else:
			print("Error: No data recovered from file")

if __name__ == "__main__":
	convert_json_to_json(input_file, output_file, feedsack_size, feedsack_file, True)


