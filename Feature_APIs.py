from elasticsearch import Elasticsearch,NotFoundError,RequestError
from flask import Flask, jsonify, request, Blueprint
from elasticsearch import helpers
import re
import xmltodict
import json
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback

app = Flask(__name__)
es = Elasticsearch()


# Indexing
@app.route('/create_index', methods=['POST'])
def create_index():
    requestf = request.get_json()              # extracted the request body
    indexname = requestf["indexname"]          # extracted the indexname from the request body
    synonym_path = requestf["synonym_path"]
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
                            "synonyms_path": synonym_path,
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
                                "digit",
                                "symbol"
                            ]
                        }
                    }
                }
            }
        }
    }
    print("creating"+indexname+" index...")
    try:
        es.indices.create(index=indexname, body=request_body)
        res = es.transport.perform_request(
            'PUT', '/'+indexname+'/_mappings', body={"properties": mapping})
        return {"message":"success","response":res},"200"
    except RequestError as es1:
        return es1.info,es1.status_code

# autocomplete
@app.route('/<indexname>/autocomplete', methods=["POST"])
def autocomplete_size(indexname):                                 
    response = request.get_json()                          # extracted the request body
    input = response["input"]                              # extracted the input from the request body
    pattern = re.compile('\W')
    sanitized_input = re.sub(pattern, ' ', input)           # input is passed through sanitization
    if "size" in response.keys():
        size = response["size"] 
        if size <= 0:
            return {"message":"Size should be greater than 0"},400
    else:
        size = 10
    try:
            
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
    except NotFoundError as es1:
        return es1.info,es1.status_code

# search
@app.route('/search', methods=['GET', 'POST'])
def search():
    response = request.get_json()                          # extracted the request body
    indexname = response["indexname"]                      # extracted the indexname from the request body
    size = response["size"]                                # extracted the size from the request body
    input = response["input"]                              # extracted the input from the request body
    From = response["From"]
    
    range_fields_value = response["range_fields_value"]    # extracted dictionary of range fields and its values
    field_terms = response["filter_terms"]                 # extracted dictionary of term fields and its values
    filter_list = []                                       # initialized empty list
    for field in field_terms.keys():
        if field == "category":
            return {"message":"Try 'category_name' instead of 'category'","status_code":"400"},400
        elif field == "brand":
            return {"message":"Try 'brand_name' instead of 'brand'","status_code":"400"},400
        else:
            filter_list.append({"terms": {field: field_terms[field]}})
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    sortlist = response["sortlist"]                         # extracted dictionary of sort fields and its sorting type
    search_fields = response["search_fields"]               # extracted fields based on which search will be performed
    if input == "*":
        res_1={}
        search_res = es.transport.perform_request(
            'POST', '/'+indexname+'/_search', body={"size": size, "from": From, "sort": sortlist, "query": {
                "function_score": {
                    "query": {
                        "bool": {

                            "filter": filter_list
                        }
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
            }})
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"bannercheck": "true"}}                    ]
                }
            }
        }
        banner_res = es.transport.perform_request(
            'POST', '/'+indexname+'/_search', body=body)
        res_1["search_response"] = search_res
        res_1["banner_response"] = banner_res
        res_1["by_brand"] = res_1["search_response"]["aggregations"]["by_brand"]["buckets"]
        res_1["by_category"] = res_1["search_response"]["aggregations"]["by_category"]["buckets"]
        return (res_1)

    pattern = re.compile('\W')
    sanitized_input = re.sub(pattern, ' ', input)           # input went through sanitization
    print(sanitized_input)
    try:
            
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
                                        "fields": search_fields,
                                        "type":"cross_fields"
                                        
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
        if search_response["hits"]["total"]["value"] == 0 and len(search_response["suggest"]["mytermsuggester1"])!=0 and len(search_response["suggest"]["mytermsuggester1"][0]["options"]) == 0:
            return {"Results": []},404
        elif search_response["hits"]["total"]["value"] == 0 and len(search_response["suggest"]["mytermsuggester1"])!=0:
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
                                            "fields": search_fields,
                                            "type":"cross_fields"
                                        
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
    except NotFoundError as es1:
        return es1.info,es1.status_code
    except RequestError as es2:
        return es2.info,es2.status_code
    

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
    for i in range(len(updatelist)):
        if i == len(updatelist)-1:
            update += "ctx._source." + \
                list(updatelist[i].keys())[0]+" = '" + \
                updatelist[i][list(updatelist[i].keys())[0]]+"'"
        else:
            update += "ctx._source." + \
                list(updatefield.keys())[0]+" = '" + \
                updatelist[i][list(updatelist[i].keys())[0]]+"';"
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
    try:
        res = es.transport.perform_request(
            'POST', '/'+indexname+'/_update_by_query', body=body)
        if res["updated"]==0:
            raise Exception("Doens't exist")
        return res
    except Exception as es1:
        return {"message":str(querylist)+" Products with the queries doesnt not exist"},404


# bulk update
@app.route("/bulk_update/<indexname>", methods=['POST'])
def update(indexname):
    bulk_data_syno = dict(xmltodict.parse(request.data))                   # converted xml to dictionary
    if "products" in bulk_data_syno["root"].keys():
        bulk_data = bulk_data_syno["root"]["products"]["product"]
        if str(type(bulk_data))=="<class 'dict'>" or str(type(bulk_data))=="<class 'collections.OrderedDict'>":
            bulk_data=[bulk_data]
        for data in bulk_data:
            data["list_price"] = float(data["list_price"])
            data["category_name"] = data["category"]                       # extraction of category in to new key
            data["brand_name"] = data["brand"]                             # extraction of brand in to new key
            if "seller_product" in data.keys():
                if str(type(data["seller_product"]["product"]))=="<class 'dict'>" or str(type(data["seller_product"]["product"]))=="<class 'collections.OrderedDict'>":
                    data["seller_product"]["product"]=[data["seller_product"]["product"]]
            res = es.index(index=indexname, id=data["id"], body=data)
    if "synonym" in bulk_data_syno["root"].keys():
        synonymlist = bulk_data_syno["root"]["synonym"]["syno"]
        try:
            file = open(
                "C:\\Users\\Win10\\Desktop\\elasticsearch-7.9.1\\config\\analysis\\synonym.txt", "a")
            file.write("\n")
            file.write("\n".join(synonymlist))
            file.close()
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
        for data in bannerlist:
            res = es. index(index=indexname, id=data["id"], body=data)
    return "success"



# get synonym
@app.route('/get_synonym', methods=["POST"])
def get_synonym():
    requestf = request.get_json()                   # extracted the request body
    path = requestf["path"]         # synonym.txt file path
    with open(path, "r") as f:
        lines = f.readlines()
    return {"synonyms": lines}



# delete synonym
@app.route('/delete_synonym', methods=["POST"])
def delete_synonym():
    requestf = request.get_json()                                                         # extraction of request body
    synonyms = requestf["synonyms"]                                                       # extraction of synonyms which needs to be deleted
    path = requestf["path"]  # synonym.txt file path
    with open(path, "r") as f:
        lines = f.readlines()
        with open(path, "w") as f:
            for line in lines:
                # print(line.strip("\n").lower())
                if line.strip("\n").lower() != synonyms:
                    f.write(line)
    return {"message":"Successfully Deleted"}


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
    try:    
        res = es.transport.perform_request(
            'POST', '/'+indexname+'/_delete_by_query', body=body)
        if res["deleted"]==0:
            return {"message":"Product with the query :"+str(querylist)+" not found"},404
        return {"message":"Number of products deleted:"+str(res["deleted"]),"response":res}
    except NotFoundError as es1:
        return es1.info,es1.status_code


# Delete Index
@app.route("/delete_index", methods=['POST'])
def delete_index():
    requestf = request.get_json()                      # extraction of request body
    indexname = requestf["indexname"]                  # extraction of indexname from the request body
    try:    
        res = es.transport.perform_request(
            'DELETE', '/'+indexname)
        return {"message":"Successfully Deleted!","response":res},"200"
    except NotFoundError as es1:
        return es1.info,es1.status_code
    

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response


if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(host='127.0.0.2', port=5000, debug=True)
