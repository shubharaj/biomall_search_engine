from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request, Blueprint
from elasticsearch import helpers
import re
import xmltodict
import json
app = Flask(__name__)
es = Elasticsearch()
cat_dict = {'General Lab Supplies': '1', 'Pipette Tips': '2', 'Lab Equipments ': '3', 'Cell Culture ': '4', 'Genomics': '5', 'Proteomics': '6', 'Glassware': '7', 'Bottles': '8', 'Multi-well Plate': '9', 'Serological Pipette': '10', 'DNA Electrophoresis': '11', 'PCR ': '12', "Kipp's Apparatus": '13', 'Desiccator': '14', 'Hot Plate': '15', 'Pipette': '16', 'Rotospin': '17', 'Shaker': '18', 'Animal Cage': '19', 'Atomic Model Set Junior': '20', 'Basket': '21', 'Beakers and Carboy': '22', 'Boxes': '23', 'Centrifuge Tubes': '24', 'Clamp and Stand': '25', 'Connector': '26', 'Cooler and Cryoware': '27', 'Energy Regulator': '28', 'Filters': '29', 'Flasks': '30', 'Funnel': '31', 'Gloves': '32', 'Magnetic Bars': '33', 'Measuring Cylinder ': '34', 'Measuring Scoop': '35', 'Membrane Filter': '36', 'Micro-Centrifuge tubes': '37', 'Micro-Test Plate': '38', 'Miscellaneous': '39', 'Petri dish': '40', 'Plant Tissue Culture': '41', 'Microtube rack': '42', 'Reservoir': '43', 'Safety Products': '44', 'Slides': '45', 'Spinix': '46', 'Syphon': '47', 'Test tube Stand': '48', 'Tip box': '49', 'Tips': '50', 'Trays': '51', 'Tubings ': '52', 'Vials': '53', 'Vortex': '54', 'Lab Consumables': '55', 'Container': '56', 'Marker': '57', 'Parafilm': '58', 'Pasteur pipette': '59', 'Tags': '60', 'Tapes':
            '61', 'Tubes': '62', 'Antibodies, proteins & ELISA kits': '63', 'Stem Cells': '64', '3D Cell Culture': '65', 'Cell Culture Media': '66', 'Sera': '67', 'Antibiotics, Buffers, Solutions & Supplements': '68', 'Cell Lines and 3D Cell culture ': '69', 'Multi-well Plates': '70', 'Cell Culture Dishes': '71', 'Cell Culture Flasks': '72', 'Serological Pipettes': '73', 'Additional Essentials': '74', 'Cell Culture Kits': '75', 'DNA Ladders': '76', 'DNA Electrphoresis Biochemicals': '77', 'DNA Electrphoresis Buffers': '78', 'DNA Electrphoresis Kits': '79', 'Nucleotides': '80', 'Polymerases': '81', 'PCR Master Mixes': '82', 'PCR Buffers, Reagents and Kits': '83', 'Chemicals': '84', 'Buffers': '85', 'Biochemicals': '86', 'Nucleic Acid Purification': '87', 'Nucleic Acid Purification Kits': '88', 'Protein Electrophoresis': '89', 'Protein Ladders': '90', 'Protein Electrophoresis Biochemicals': '91', 'Protein Electrophoresis Buffers': '92', 'Protein Electrophoresis Kits': '93', 'Protein Purification ': '94', 'Protein Purification  Kits': '95', 'PCR Plasticwares ': '96', 'PCR Plates': '97', 'PCR Tubes': '98', 'PCR Storage Plates ': '99', 'PCR Foils and Seals': '100', 'PCR Workstation': '101', 'PCR Strips and Caps': '102', 'Protein Estimation': '103', 'DNA Purification and Extraction': '104', 'RNA Purifications and Extractions': '105', 'BD Biociences': '106', 'BD Difco': '107', 'Brand Inventory': '108', 'MP Biomedicals': '109', 'Corning': '110', 'Biohit': '111', 'Protein Extraction': '112', 'Mass Spectroscopy ': '113', 'Probes and Crosslinkers': '114', 'Western Blotting': '115', 'Nucleotide': '116', 'Microbiology': '117', 'Restriction and other Enzymes': '118', 'Syringe Filter': '119', 'Coverslips': '120', 'Pipette Aids': '121', 'Plant Tissue Culture Essentials': '122', 'Cloning': '123', 'Fine Chemicals': '124', 'Acids and Solvents': '125', 'Services': '126', 'Chromatography': '127', 'Centrifuge': '128', 'Stirrer': '129', 'Lab Furniture': '130', 'Fire Safety Cabinets': '131', 'Circulating Baths': '132', 'Micro Balance Enclosure': '133', 'Fume Hood System': '134', 'Microscope': '135', 'DNA Sequencing kits': '136', 'Filtration Units': '137', 'Sonicator': '138', 'Chromatography Accessories': '139', 'Spectrometer': '140', 'Weight Rings': '141'}
brand_dict = {'MP Biomedicals': '1', 'BioPointe Scientific': '2', 'Atgen': '3', 'ProSpec Alternatives': '4', 'National Scientific Supply ': '5',
              'Tarsons': '6', 'Alfa Chemika': '7', 'Ansell': '8', 'Ansell12': '9', 'Kingfisher': '10', 'Test brand shub': '11', 'Biomall': '12'}


# Indexing
@app.route('/create_index', methods=['POST'])
def create_index():
    requestf = request.get_json()              # extracted the request body
    indexname = requestf["indexname"]          # extracted the indexname from the request body
    mapping = requestf["mapping_property"]     # extracted mapping from the request body
    request_body = {                           # settings which need to be performed is stored in this variable
        "settings": {
            "index": {
                "analysis": {
                    "analyzer": {
                        "synonym_analyzer": {
                            "tokenizer": "whitespace",
                            "filter": ["lowercase", "my_synonyms"]
                        },

                        "autocomplete": {
                            "tokenizer": "autocomplete",
                            "filter": ["lowercase"]
                        }
                    },
                    "filter": {
                        "my_synonyms": {
                            "type": "synonym",
                            "synonyms_path": "analyzers/synonym.txt",
                            "updateable": "true"
                        }
                    },
                    "tokenizer": {
                        "autocomplete": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 20,
                            "token_chars": [
                                "letter",
                                "digit"
                            ]
                        }
                    }
                }
            }
        }
    }
    print("creating"+indexname+" index...")
    es.indices.create(index=indexname, body=request_body)
    res = es.transport.perform_request(
        'PUT', '/'+indexname+'/_mappings', body={"properties": mapping})
    return res


# autocomplete
@app.route('/<indexname>/autocomplete', methods=["POST"])
def autocomplete_size(indexname):                                 
    response = request.get_json()                          # extracted the request body
    input = response["input"]                              # extracted the input from the request body
    pattern = re.compile('\W')
    sanitized_input = re.sub(pattern, '', input)           # input is passed through sanitization
    if "size" in response.keys():
        size = response["size"]
    else:
        size = 10
    res = es.search(index=indexname, body={"query": {
        "query_string": {
            "query": sanitized_input}

    },
        "aggs": {                                          # Facets feature
            "by_brand": {
                "terms": {"field": "brand_name"}
            },
            "by_category": {
                "terms": {"field": "category_name"}
            }
    }, "size": size})
    res["by_brand"] = res["aggregations"]["by_brand"]["buckets"]   
    res["by_category"] = res["aggregations"]["by_category"]["buckets"]
    return res


# search
@app.route('/search', methods=['GET', 'POST'])
def search():
    response = request.get_json()                          # extracted the request body
    indexname = response["indexname"]                      # extracted the indexname from the request body
    size = response["size"]                                # extracted the size from the request body
    input = response["input"]                              # extracted the input from the request body
    pattern = re.compile('\W')
    sanitized_input = re.sub(pattern, '', input)           # input went through sanitization
    range_fields_value = response["range_fields_value"]    # extracted dictionary of range fields and its values
    field_terms = response["filter_terms"]                 # extracted dictionary of term fields and its values
    filter_list = []                                       # initialized empty list
    for field in field_terms.keys():
        if field == "category":
            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})
        elif field == "brand":
            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    sortlist = response["sortlist"]                         # extracted dictionary of sort fields and its sorting type
    search_fields = response["search_fields"]               # extracted fields based on which search will be performed
    From = repsonse["From"]                                 # extracted "from" 
    search_response = es.search(index=indexname, body={
        "sort": sortlist,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": sanitized_input,
                                    "fields": search_fields
                                }
                            }
                        ],
                        "filter": filter_list
                    }
                }
            }
        },
        "from": From,
        "size": size,
        "suggest": {
            "mytermsuggester1": {
                "text": sanitized_input,
                "term": {
                    "field": "title"
                }
            },
            "mytermsuggester2": {
                "text": sanitized_input,
                "term": {
                    "field": "brand"
                }
            }
        },
        "aggs": {                                                 # Facets feature
            "by_brand": {
                "terms": {"field": "brand_name"}
            },
            "by_category": {
                "terms": {"field": "category_name"}
            }
        }
    }
    )
    res = {}
    if search_response["hits"]["total"]["value"] == 0 and len(search_response["suggest"]["mytermsuggester1"][0]["options"]) == 0:
        return {"Results": []}
    elif search_response["hits"]["total"]["value"] == 0:
        suggestWord = search_response["suggest"]["mytermsuggester1"][0]["options"][0]["text"]
        search_response = es.search(index=indexname, body={
            "sort": sortlist,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": suggestWord,
                                        "fields": search_fields
                                    }
                                }
                            ],
                            "filter": filter_list
                        }
                    }
                }
            },
            "from": From,
            "size": size,
            "suggest": {
                "mytermsuggester1": {
                    "text": suggestWord,
                    "term": {
                        "field": "title"
                    }
                },
                "mytermsuggester2": {
                    "text": suggestWord,
                    "term": {
                        "field": "brand"
                    }
                }
            },
            "aggs": {
                "by_brand": {
                    "terms": {"field": "brand_name"}
                },
                "by_category": {
                    "terms": {"field": "category_name"}
                }
            }
        }
        )
        suggestWord = "Did you mean "+suggestWord+" ?"
        res["suggestWord"] = suggestWord
    banner_keyword = sanitized_input
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"bannercheck": "true"}},
                    {"match": {"banner_keyword": banner_keyword}}
                ]
            }
        }
    }
    banner_response = es.transport.perform_request(
        'POST', '/'+indexname+'/_search', body=body)
    res["search_response"] = search_response
    res["banner_response"] = banner_response
    res["by_brand"] = res["search_response"]["aggregations"]["by_brand"]["buckets"]
    res["by_category"] = res["search_response"]["aggregations"]["by_category"]["buckets"]
    return (res)



# update field by query
@app.route("/update_field_by_query", methods=['POST'])
def update_field_with_query():
    requestf = request.get_json()                   # extracted the request body
    indexname = requestf["indexname"]               # extracted indexname from the request body
    querylist = requestf["query"]                   # extracted query from the request body
    updatelist = requestf["update"]                 # extracted updates which need to be performed from the request body
    query = []                                      # initialized empty list
    for queryfield in querylist:
        query.append({"term": {list(queryfield.keys())[0]: {
                      "value": queryfield[list(queryfield.keys())[0]]}}})
    update = ""
    print(querylist)
    for i in range(len(updatelist)):
        if i == len(updatelist)-1:
            update += "ctx._source." + \
                list(updatelist[i].keys())[0]+" = '" + \
                updatelist[i][list(updatelist[i].keys())[0]]+"'"
        else:
            update += "ctx._source." + \
                list(updatefield.keys())[0]+" = '" + \
                updatelist[i][list(updatelist[i].keys())[0]]+"';"
    print(query)
    print(update)
    body = {
        "script": {
            "source": update,
            "lang": "painless"
        },
        "query": {
            "bool": {
                "must": query
            }
        }
    }
    res = es.transport.perform_request(
        'POST', '/'+indexname+'/_update_by_query', body=body)
    return res



# bulk update
@app.route("/bulk_update/<indexname>", methods=['POST'])
def update(indexname):
    bulk_data_syno = dict(xmltodict.parse(request.data))                   # converted xml to dictionary
    print(bulk_data_syno["root"].keys())
    if "products" in bulk_data_syno["root"].keys():
        bulk_data = bulk_data_syno["root"]["products"]["product"]
        for data in bulk_data:
            data["list_price"] = float(data["list_price"])
            data["category_name"] = data["category"]                       # extraction of category in to new key
            data["brand_name"] = data["brand"]                             # extraction of brand in to new key
            res = es.index(index=indexname, id=data["id"], body=data)
    print(2)
    if "synonym" in bulk_data_syno["root"].keys():
        synonymlist = bulk_data_syno["root"]["synonym"]["syno"]
        try:
            file = open(
                "C:\\Users\\Win10\\Desktop\\elasticsearch-7.9.1\\config\\analysis\\synonym.txt", "a")
            file.write("\n")
            file.write("\n".join(synonymlist))
            file.close()
            print("done")
        except EOFError as ex:
            print("Caught the EOF error.")
            raise ex
        except IOError as e:
            print("Caught the I/O error.")
            raise ex
        response = es.transport.perform_request(
            'POST', '/'+indexname+'/_reload_search_analyzers')
    if "banners" in bulk_data_syno["root"].keys():
        bannerlist = bulk_data_syno["root"]["banners"]["banner"]
        print(bannerlist)
        for data in bannerlist:
            res = es. index(index=indexname, id=data["id"], body=data)
        print(3)

    print("yes")
    return "success"



# get synonym
@app.route('/get_synonym', methods=["GET"])
def get_synonym():
    path = "C:\\Users\\Win10\\Desktop\\elasticsearch-7.9.1\\config\\analysis\\synonym.txt"         # synonym.txt file path
    with open(path, "r") as f:
        lines = f.readlines()
    return {"synonyms": lines}



# delete synonym
@app.route('/delete_synonym', methods=["POST"])
def delete_synonym():
    requestf = request.get_json()                                                         # extraction of request body
    synonyms = requestf["synonyms"]                                                       # extraction of synonyms which needs to be deleted
    path = "C:\\Users\\Win10\\Desktop\\elasticsearch-7.9.1\\config\\analysis\\synonym.txt"  # synonym.txt file path
    with open(path, "r") as f:
        lines = f.readlines()
        with open(path, "w") as f:
            for line in lines:
                # print(line.strip("\n").lower())
                if line.strip("\n").lower() != synonyms:
                    f.write(line)
    return "success"


# Delete_by_query
@app.route("/<indexname>/delete_by_query", methods=['POST'])
def delete_field_with_query(indexname):
    requestf = request.get_json()                     # extraction of request body
    querylist = requestf["query"]                     # extraction of query basis which product description needs to be deleted
    query = []                                        # initialization of empty list
    for k in querylist:
        query.append({"term":k})
    body = {
        "query": {
            "bool": {
                "must": query
            }
        }
    }
    res = es.transport.perform_request(
        'POST', '/'+indexname+'/_delete_by_query', body=body)
    return res



# Delete Index
@app.route("/delete_index", methods=['POST'])
def delete_index():
    requestf = request.get_json()                      # extraction of request body
    indexname = requestf["indexname"]                  # extraction of indexname from the request body
    res = es.transport.perform_request(
        'DELETE', '/'+indexname)
    return res

if __name__ == '__main__':
    app.run(host='127.0.0.2', port=5000, debug=True)
