from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
from elasticsearch import helpers
app = Flask(__name__)
es = Elasticsearch()
cat_dict = {'General Lab Supplies': '1', 'Pipette Tips': '2', 'Lab Equipments ': '3', 'Cell Culture ': '4', 'Genomics': '5', 'Proteomics': '6', 'Glassware': '7', 'Bottles': '8', 'Multi-well Plate': '9', 'Serological Pipette': '10', 'DNA Electrophoresis': '11', 'PCR ': '12', "Kipp's Apparatus": '13', 'Desiccator': '14', 'Hot Plate': '15', 'Pipette': '16', 'Rotospin': '17', 'Shaker': '18', 'Animal Cage': '19', 'Atomic Model Set Junior': '20', 'Basket': '21', 'Beakers and Carboy': '22', 'Boxes': '23', 'Centrifuge Tubes': '24', 'Clamp and Stand': '25', 'Connector': '26', 'Cooler and Cryoware': '27', 'Energy Regulator': '28', 'Filters': '29', 'Flasks': '30', 'Funnel': '31', 'Gloves': '32', 'Magnetic Bars': '33', 'Measuring Cylinder ': '34', 'Measuring Scoop': '35', 'Membrane Filter': '36', 'Micro-Centrifuge tubes': '37', 'Micro-Test Plate': '38', 'Miscellaneous': '39', 'Petri dish': '40', 'Plant Tissue Culture': '41', 'Microtube rack': '42', 'Reservoir': '43', 'Safety Products': '44', 'Slides': '45', 'Spinix': '46', 'Syphon': '47', 'Test tube Stand': '48', 'Tip box': '49', 'Tips': '50', 'Trays': '51', 'Tubings ': '52', 'Vials': '53', 'Vortex': '54', 'Lab Consumables': '55', 'Container': '56', 'Marker': '57', 'Parafilm': '58', 'Pasteur pipette': '59', 'Tags': '60', 'Tapes':
            '61', 'Tubes': '62', 'Antibodies, proteins & ELISA kits': '63', 'Stem Cells': '64', '3D Cell Culture': '65', 'Cell Culture Media': '66', 'Sera': '67', 'Antibiotics, Buffers, Solutions & Supplements': '68', 'Cell Lines and 3D Cell culture ': '69', 'Multi-well Plates': '70', 'Cell Culture Dishes': '71', 'Cell Culture Flasks': '72', 'Serological Pipettes': '73', 'Additional Essentials': '74', 'Cell Culture Kits': '75', 'DNA Ladders': '76', 'DNA Electrphoresis Biochemicals': '77', 'DNA Electrphoresis Buffers': '78', 'DNA Electrphoresis Kits': '79', 'Nucleotides': '80', 'Polymerases': '81', 'PCR Master Mixes': '82', 'PCR Buffers, Reagents and Kits': '83', 'Chemicals': '84', 'Buffers': '85', 'Biochemicals': '86', 'Nucleic Acid Purification': '87', 'Nucleic Acid Purification Kits': '88', 'Protein Electrophoresis': '89', 'Protein Ladders': '90', 'Protein Electrophoresis Biochemicals': '91', 'Protein Electrophoresis Buffers': '92', 'Protein Electrophoresis Kits': '93', 'Protein Purification ': '94', 'Protein Purification  Kits': '95', 'PCR Plasticwares ': '96', 'PCR Plates': '97', 'PCR Tubes': '98', 'PCR Storage Plates ': '99', 'PCR Foils and Seals': '100', 'PCR Workstation': '101', 'PCR Strips and Caps': '102', 'Protein Estimation': '103', 'DNA Purification and Extraction': '104', 'RNA Purifications and Extractions': '105', 'BD Biociences': '106', 'BD Difco': '107', 'Brand Inventory': '108', 'MP Biomedicals': '109', 'Corning': '110', 'Biohit': '111', 'Protein Extraction': '112', 'Mass Spectroscopy ': '113', 'Probes and Crosslinkers': '114', 'Western Blotting': '115', 'Nucleotide': '116', 'Microbiology': '117', 'Restriction and other Enzymes': '118', 'Syringe Filter': '119', 'Coverslips': '120', 'Pipette Aids': '121', 'Plant Tissue Culture Essentials': '122', 'Cloning': '123', 'Fine Chemicals': '124', 'Acids and Solvents': '125', 'Services': '126', 'Chromatography': '127', 'Centrifuge': '128', 'Stirrer': '129', 'Lab Furniture': '130', 'Fire Safety Cabinets': '131', 'Circulating Baths': '132', 'Micro Balance Enclosure': '133', 'Fume Hood System': '134', 'Microscope': '135', 'DNA Sequencing kits': '136', 'Filtration Units': '137', 'Sonicator': '138', 'Chromatography Accessories': '139', 'Spectrometer': '140', 'Weight Rings': '141'}
brand_dict = {'MP Biomedicals': '1', 'BioPointe Scientific': '2', 'Atgen': '3', 'ProSpec Alternatives': '4', 'National Scientific Supply ': '5',
              'Tarsons': '6', 'Alfa Chemika': '7', 'Ansell': '8', 'Ansell12': '9', 'Kingfisher': '10', 'Test brand shub': '11', 'Biomall': '12'}


@app.route('/autocomplete', methods=["POST"])
def autocomplete():
    response = request.get_json()
    input = response["input"]
    res = es.search(index='biomall', body={"query": {
        "query_string": {
            "query": input}}})
    return jsonify(res)


@app.route('/autocomplete_size', methods=["POST"])
def autocomplete_size():
    response = request.get_json()
    input = response["input"]
    size = response["size"]
    res = es.search(index='biomall', body={"query": {
        "query_string": {
            "query": input}}, "size": size})
    return jsonify(res)


@app.route('/autocomplete_highlight', methods=["POST"])
def autocomplete_highlight():
    requestf = request.get_json()
    input = requestf["input"]
    input_field = requestf["input_field"]
    res = es.search(index='biomall', body={
        "query": {
            "query_string": {
                "query": input
            }
        },
        "highlight": {
            "fields": {
                input_field: {}
            }
        }})
    return jsonify(res)


@app.route('/autocomplete_highlight_size', methods=["POST"])
def autocomplete_highlight_size():
    requestf = request.get_json()
    input = requestf["input"]
    input_field = requestf["input_field"]
    size = requestf["size"]
    res = es.search(index='biomall', body={
        "query": {
            "query_string": {
                "query": input
            }
        },
        "highlight": {
            "fields": {
                input_field: {}
            }
        },
        "size": size})
    return jsonify(res)


@app.route('/search_query_by_string', methods=['POST'])
def search_query_by_string():
    requestf = request.get_json()
    input = requestf["input"]
    res = es.search(index='biomall', body={
        "query": {
            "query_string": {
                "query": input
            }
        }
    })
    return res


@app.route('/search_query_by_string_spellchecker', methods=['POST'])
def search_query_by_string_spellchecker():
    requestf = request.get_json()
    input = requestf["input"]
    input_field = requestf["input_field"]
    res = es.search(index='biomall', body={
        "query": {
            "fuzzy": {
                input_field: {
                    "value": "lecd",
                    "fuzziness": 4
                }
            }
        },
        "highlight": {
            "fields": {
                input_field: {}
            }
        }
    })
    if len(res['hits']['hits']) >= 1:
        firstresponse = res['hits']['hits'][0]["hightlight"]["title"][0]
        response = {"suggest": firstresponse, "data": res}
    else:
        response = res
    return response


@app.route('/filter_range', methods=["POST"])
def filter_range():
    requestf = request.get_json()
    print(requestf)
    search_field = requestf["search_field"]
    input = requestf["input"]
    range_field = requestf["range_field"]
    range_min_val = requestf["range_min_val"]
    range_max_val = requestf["range_max_val"]
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [
                    {"range": {range_field: {"gte": range_min_val}}}

                ]
            }
        }})
    return res


@app.route('/filter_range_mul', methods=["POST"])
def filter_range_mul():
    requestf = request.get_json()
    search_field = requestf["search_field"]
    input = requestf["input"]
    range_fields_value = requestf["range_fields_value"]
    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }})
    return res


@app.route('/filter_term', methods=["POST"])
def filter_term():
    requestf = request.get_json()
    search_field = requestf["search_field"]
    search_input = requestf["search_input"]
    filter_term = requestf["filter_term"]
    filter_term_name = requestf["filter_term_name"]
    if filter_term == "category":
        filter_term_name = cat_dict[filter_term_name]
        filter_term = "cat_id"
    if filter_term == "brand":
        filter_term_name = brand_dict[filter_term_name]
        filter_term = "brand_id"
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: search_input}}
                ],
                "filter": [
                    {"term":  {filter_term: filter_term_name}}

                ]
            }
        }})
    return res


@app.route('/filter_term_mul', methods=["POST"])
def filter_term_mul():
    requestf = request.get_json()
    search_field = requestf["search_field"]
    search_input = requestf["search_input"]
    field_terms = requestf["filter_terms"]
    filter_list = []
    for field in field_terms.keys():
        if field == "category":
            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})
        elif field == "brand":
            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: search_input}}
                ],
                "filter": filter_list
            }
        }})
    return res


@app.route('/filter_range_size', methods=["POST"])
def filter_range_size():
    requestf = request.get_json()
    print(requestf)
    search_field = requestf["search_field"]
    input = requestf["input"]
    range_field = requestf["range_field"]
    range_min_val = requestf["range_min_val"]
    range_max_val = requestf["range_max_val"]
    size = requestf["size"]
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [
                    {"range": {range_field: {"gte": range_min_val}}}

                ]
            }
        }, "size": size})
    return res


@app.route('/filter_range_mul_size', methods=["POST"])
def filter_range_mul_size():
    requestf = request.get_json()
    size = requestf["size"]
    search_field = requestf["search_field"]
    input = requestf["input"]
    range_fields_value = requestf["range_fields_value"]
    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})

    print(filter_list)
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }, "size": size})
    return res


@app.route('/filter_term_size', methods=["POST"])
def filter_term_size():
    requestf = request.get_json()
    search_field = requestf["search_field"]
    search_input = requestf["search_input"]
    filter_term = requestf["filter_term"]
    filter_term_name = requestf["filter_term_name"]
    size = requestf["size"]
    if filter_term == "category":
        filter_term_name = cat_dict[filter_term_name]
        filter_term = "cat_id"
    if filter_term == "brand":
        filter_term_name = brand_dict[filter_term_name]
        filter_term = "brand_id"
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: search_input}}
                ],
                "filter": [
                    {"term":  {filter_term: filter_term_name}}

                ]
            }
        }, "size": size})
    return res


@app.route('/filter_term_mul_size', methods=["POST"])
def filter_term_mul_size():
    requestf = request.get_json()
    search_field = requestf["search_field"]
    search_input = requestf["search_input"]
    field_terms = requestf["filter_terms"]
    filter_list = []
    size = requestf["size"]
    for field in field_terms.keys():
        if field == "category":
            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})
        elif field == "brand":
            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: search_input}}
                ],
                "filter": filter_list
            }
        }, "size": size})
    return res


@app.route('/filter')
def filter():
    res = es.search(index='biomall', body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "Pipet"}}
                ],
                "filter": [
                    {"term":  {"brand_id": 1}}

                ]
            }
        }})
    return res


@app.route('/insert_one_product', methods=["POST"])
def insert_one_product():
    requestf = request.get_json()
    data = requestf["data"]
    id = requestf["id"]
    res = es.index(index="biomall", id=id, body=data)
    return "success"


@app.route('/search_by_index_and_id', methods=['POST'])
def search_by_index_and_id():
    requestf = request.get_json()
    index = requestf["index"]
    id = requestf["id"]
    res = es.get(
        index=index,
        id=id
    )
    return res


@app.route('/filter_range_sort', methods=['GET', 'POST'])
def filter_range_sort():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    sort_parameter = response["sort"]
    sort_type = response["sort_type"]
    range_fields_value = response["range_field_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "sort": [
            {sort_parameter: sort_type}

        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list

            }
        }}
    )
    return (res)


@app.route('/filter_range_multiple_variable_sort', methods=['GET', 'POST'])
def filter_range_multiple_variable_sort():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    range_fields_value = response["range_fields_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)

    res = es.search(index='biomall', body={
        "sort": [
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }}
    )
    return (res)


@app.route('/filter_term_sort', methods=['GET', 'POST'])
def filter_term_sort():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    term_field = response["term"]
    term_value = response["term_value"]
    sort_parameter = response["sort"]

    sort_type = response["sort_type"]
    if term_field == "category":
        term_value = cat_dict[term_value]
        term_field = "cat_id"
    if term_field == "brand":
        term_value = brand_dict[term_value]
        term_field = "brand_id"
    res = es.search(index='biomall', body={
        "sort": [
            {sort_parameter: sort_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [

                    {"term":  {term_field: term_value}}

                ]


            }
        }}
    )
    return (res)


@app.route('/filter_multiple_variable_term_sort', methods=['GET', 'POST'])
def filter_multiple_variable_term_sort():
    response = request.get_json()
    search_field = response["search_field"]
    field_terms = response["filter_terms"]
    print(response)

    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    filter_list = []
    for field in field_terms.keys():
        if field == "category":

            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})

        elif field == "brand":

            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})
    res = es.search(index='biomall', body={
        "sort": [
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list


            }
        }}
    )
    return (res)


@app.route('/filter_range_sort_size', methods=['GET', 'POST'])
def filter_range_sort_size():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    size = response["size"]

    sort_parameter = response["sort"]
    sort_type = response["sort_type"]
    range_fields_value = response["range_field_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "sort": [
            {sort_parameter: sort_type}

        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list

            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_range_multiple_variable_sort_size', methods=['GET', 'POST'])
def filter_range_multiple_variable_sort_size():
    response = request.get_json()
    print(response)
    size = response["size"]
    search_field = response["search_field"]
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    range_fields_value = response["range_fields_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)

    res = es.search(index='biomall', body={
        "sort": [
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_term_sort_size', methods=['GET', 'POST'])
def filter_term_sort_size():
    response = request.get_json()
    print(response)
    size = response["size"]
    search_field = response["search_field"]
    input = response["input"]
    term_field = response["term"]
    term_value = response["term_value"]
    sort_parameter = response["sort"]

    sort_type = response["sort_type"]
    if term_field == "category":
        term_value = cat_dict[term_value]
        term_field = "cat_id"
    if term_field == "brand":
        term_value = brand_dict[term_value]
        term_field = "brand_id"
    res = es.search(index='biomall', body={
        "sort": [
            {sort_parameter: sort_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [

                    {"term":  {term_field: term_value}}

                ]


            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_multiple_variable_term_sort_size', methods=['GET', 'POST'])
def filter_multiple_variable_term_sort_size():
    response = request.get_json()
    size = response["size"]
    search_field = response["search_field"]
    field_terms = response["filter_terms"]
    print(response)
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    filter_list = []
    for field in field_terms.keys():
        if field == "category":

            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})

        elif field == "brand":

            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})

    res = es.search(index='biomall', body={
        "sort": [
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list


            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_range_sort_sponsored', methods=['GET', 'POST'])
def filter_range_sort_sponsored():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    sort_parameter = response["sort"]
    sort_type = response["sort_type"]
    range_fields_value = response["range_field_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort_parameter: sort_type}

        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list

            }
        }}
    )
    return (res)


@app.route('/filter_range_multiple_variable_sort_sponsored', methods=['GET', 'POST'])
def filter_range_multiple_variable_sort_sponsored():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    range_fields_value = response["range_fields_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)

    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }}
    )
    return (res)


@app.route('/filter_term_sort_sponsored', methods=['GET', 'POST'])
def filter_term_sort_sponsored():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    term_field = response["term"]
    term_value = response["term_value"]
    sort_parameter = response["sort"]

    sort_type = response["sort_type"]
    if term_field == "category":
        term_value = cat_dict[term_value]
        term_field = "cat_id"
    if term_field == "brand":
        term_value = brand_dict[term_value]
        term_field = "brand_id"
    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort_parameter: sort_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [

                    {"term":  {term_field: term_value}}

                ]


            }
        }}
    )
    return (res)


@app.route('/filter_multiple_variable_term_sort_sponsored', methods=['GET', 'POST'])
def filter_multiple_variable_term_sort_sponsored():
    response = request.get_json()
    search_field = response["search_field"]
    field_terms = response["filter_terms"]
    print(response)
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    filter_list = []
    for field in field_terms.keys():
        if field == "category":

            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})

        elif field == "brand":

            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})

    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list


            }
        }}
    )
    return (res)


@app.route('/filter_range_sort_size_sponsored', methods=['GET', 'POST'])
def filter_range_sort_size_sponsored():
    response = request.get_json()
    print(response)
    search_field = response["search_field"]
    input = response["input"]
    size = response["size"]

    sort_parameter = response["sort"]
    sort_type = response["sort_type"]
    range_fields_value = response["range_field_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)
    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort_parameter: sort_type}

        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list

            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_range_multiple_variable_sort_size_sponsored', methods=['GET', 'POST'])
def filter_range_multiple_variable_sort_size_sponsored():
    response = request.get_json()
    print(response)
    size = response["size"]
    search_field = response["search_field"]
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    range_fields_value = response["range_fields_value"]

    filter_list = []
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    print(filter_list)

    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list
            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_term_sort_size_sponsored', methods=['GET', 'POST'])
def filter_term_sort_size_sponsored():
    response = request.get_json()
    print(response)
    size = response["size"]
    search_field = response["search_field"]
    input = response["input"]
    term_field = response["term"]
    term_value = response["term_value"]
    sort_parameter = response["sort"]

    sort_type = response["sort_type"]
    if term_field == "category":
        term_value = cat_dict[term_value]
        term_field = "cat_id"
    if term_field == "brand":
        term_value = brand_dict[term_value]
        term_field = "brand_id"
    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort_parameter: sort_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": [

                    {"term":  {term_field: term_value}}

                ]


            }
        }, "size": size
    }
    )
    return (res)


@app.route('/filter_multiple_variable_term_sort_size_sponsored', methods=['GET', 'POST'])
def filter_multiple_variable_term_sort_size_sponsored():
    response = request.get_json()
    size = response["size"]
    search_field = response["search_field"]
    field_terms = response["filter_terms"]
    print(response)
    input = response["input"]
    sort1_parameter = response["sort1"]
    sort2_parameter = response["sort2"]
    sort1_type = response["sort1_type"]
    sort2_type = response["sort2_type"]
    filter_list = []
    for field in field_terms.keys():
        if field == "category":

            filter_list.append(
                {"term": {"cat_id": cat_dict[field_terms[field]]}})

        elif field == "brand":

            filter_list.append(
                {"term": {"brand_id": brand_dict[field_terms[field]]}})
        else:
            filter_list.append({"term": {field: field_terms[field]}})

    res = es.search(index='biomall', body={
        "sort": [
            {"sponsored_value": "desc"},
            {sort1_parameter: sort1_type},
            {sort2_parameter: sort2_type}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {search_field: input}}
                ],
                "filter": filter_list


            }
        }, "size": size
    }
    )
    return (res)


if __name__ == '__main__':
    app.run(host='127.0.0.2', port=5000, debug=True)
