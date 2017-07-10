import json
import sys
import os
from ..utils.file_utils import find_files
from ..parsers.ase_parser import parse_ase
from tqdm import tqdm
from ..validator.schema_validator import Validator

# VERSION 0.2.0

# This is the converter for: The CoMFA steroids as a benchmark dataset for development of 3D QSAR methods
# Arguments:
#   input_path (string): The file or directory where the data resides.
#       NOTE: Do not hard-code the path to the data in the converter (the filename can be hard-coded, though). The converter should be portable.
#   metadata (string or dict): The path to the JSON dataset metadata file, a dict or json.dumps string containing the dataset metadata, or None to specify the metadata here. Default None.
#   verbose (bool): Should the script print status messages to standard output? Default False.
#       NOTE: The converter should have NO output if verbose is False, unless there is an error.
def convert(input_path, metadata=None, verbose=False):
    if verbose:
        print("Begin converting")

    # Collect the metadata
    if not metadata:
        dataset_metadata = {
            "mdf-title": "The CoMFA steroids as a benchmark dataset for development of 3D QSAR methods",
            "mdf-acl": ['public'],
            "mdf-source_name": "qsar_comfa_steroids",
            "mdf-citation": ["Coats, E.A. Perspectives in Drug Discovery and Design (1998) 12: 199. doi:10.1023/A:1017050508855"],
            "mdf-data_contact": {

                "given_name": "Eugene A.",
                "family_name": "Coats",
                
                "email": "eugene.coats^q*amylin.com",
                "instituition": "Amylin Pharmaceuticals, Inc."

                },

            "mdf-author": [{
                
                "given_name": "Eugene A.",
                "family_name": "Coats",
                
                "email": "eugene.coats^q*amylin.com",
                "instituition": "Amylin Pharmaceuticals, Inc."
                
                }],

          #  "mdf-license": "",

            "mdf-collection": "QSAR CoMFA Steroids",
            "mdf-data_format": ["sdf"],
            "mdf-data_type": ["QSAR"],
            #"mdf-tags": ,

            "mdf-description": "31 Steroids with Corticosteroid Binding Globulin (CBG) receptor affinity",
            "mdf-year": 1998,

            "mdf-links": {

                "mdf-landing_page": "http://www2.chemie.uni-erlangen.de/services/steroids/",

                "mdf-publication": ["https://link.springer.com/article/10.1023%2FA%3A1017050508855"],
              #  "mdf-dataset_doi": ,

            #    "mdf-related_id": ,

                # data links: {
                
                    #"globus_endpoint": ,
                    #"http_host": ,

                    #"path": ,
                    #}
                },

#            "mdf-mrr": ,

            "mdf-data_contributor": [{
                "given_name": "Evan",
                "family_name": "Pike",
                "email": "dep78@uchicago.edu",
                "institution": "The University of Chicago",
                "github": "dep78"
                }]
            }
        
    elif type(metadata) is str:
        try:
            dataset_metadata = json.loads(metadata)
        except Exception:
            try:
                with open(metadata, 'r') as metadata_file:
                    dataset_metadata = json.load(metadata_file)
            except Exception as e:
                sys.exit("Error: Unable to read metadata: " + repr(e))
    elif type(metadata) is dict:
        dataset_metadata = metadata
    else:
        sys.exit("Error: Invalid metadata parameter")



    # Make a Validator to help write the feedstock
    # You must pass the metadata to the constructor
    # Each Validator instance can only be used for a single dataset
    # If the metadata is incorrect, the constructor will throw an exception and the program will exit
    dataset_validator = Validator(dataset_metadata)


    # Get the data
    #    Each record should be exactly one dictionary
    #    You must write your records using the Validator one at a time
    #    It is recommended that you use a parser to help with this process if one is available for your datatype
    #    Each record also needs its own metadata
    i = 0
    for data_file in tqdm(find_files(input_path, "sdf"), desc="Processing files", disable=not verbose):
        record = parse_ase(os.path.join(data_file["path"], data_file["filename"]), "sdf")
        path = data_file["path"][:-8]     #Remove the extra steroids directory
        with open(os.path.join(os.path.abspath(""), path, "activity.txt"), 'r') as raw_in:
            activity_lst = raw_in.readlines()[14:]
        activity_data = activity_lst[i].split("  ")
        record_metadata = {
            "mdf-title": "QSAR CoMFA Steroids - " + record["chemical_formula"],
            "mdf-acl": ['public'],

#            "mdf-tags": ,
#            "mdf-description": ,
            
            "mdf-composition": record["chemical_formula"],
          #  "mdf-raw": json.dumps(record),

            "mdf-links": {
#                "mdf-landing_page": ,

#                "mdf-publication": ,
#                "mdf-dataset_doi": ,

#                "mdf-related_id": ,

                "sdf": {
                    "globus_endpoint": "82f1b5c6-6e9b-11e5-ba47-22000b92c6ec",
                    "http_host": "https://data.materialsdatafacility.org",

                    "path": "/collections/qsar_comfa_steroids/" + data_file["no_root_path"] + "/" + data_file["filename"],
                    },
                "txt": {
                    "globus_endpoint": "82f1b5c6-6e9b-11e5-ba47-22000b92c6ec",
                    "http_host": "https://data.materialsdatafacility.org",

                    "path": "/collections/qsar_comfa_steroids/activity.txt",
                    }
                },

#            "mdf-citation": ,
#            "mdf-data_contact": {

#                "given_name": ,
#                "family_name": ,

#                "email": ,
#                "institution":,

#                },

#            "mdf-author": ,

#            "mdf-license": ,
#            "mdf-collection": ,
#            "mdf-data_format": ,
#            "mdf-data_type": ,
#            "mdf-year": ,

#            "mdf-mrr":

#            "mdf-processing": ,
#            "mdf-structure":,
            "other_data": {
                "pK(log_1/K)": activity_data[0],
                "activity_class": activity_data[1],
                "compound_name": activity_data[2][:-1],
                },
            }

        # Pass each individual record to the Validator
        result = dataset_validator.write_record(record_metadata)
        i+=1

        # Check if the Validator accepted the record, and print a message if it didn't
        # If the Validator returns "success" == True, the record was written successfully
        if result["success"] is not True:
            print("Error:", result["message"])

    # You're done!
    if verbose:
        print("Finished converting")