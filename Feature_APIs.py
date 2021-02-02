from elasticsearch import Elasticsearch, NotFoundError, RequestError
from flask import Flask, jsonify, request, Blueprint
from elasticsearch import helpers
import re
import xmltodict
import json
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
import pysftp
import config


app = Flask(__name__)
es = Elasticsearch([{"host":config.elasticIp,"port":config.elasticPort}],timeout=100)
# es = Elasticsearch()
# Indexing


@app.route('/create_index', methods=['POST'])
def create_index():
    requestf = request.get_json()              # extracted the request body
    # extracted the indexname from the request body
    indexname = requestf["indexname"]
    # extracted mapping from the request body
    synonym_path = config.synonymPath
    mapping = requestf["mapping_property"]
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
                        },
                        "hyphen_cas":{
                            "tokenizer":"whitespace",
                            "filter":["lowercase", "stop", "my_word_delimiter"]
                        }
                    },
                    "filter": {
                        "my_synonyms": {
                            "type": "synonym",
                            "synonyms_path": synonym_path,
                            "updateable": "true"
                        },
                        "my_word_delimiter": {
                            "type": "word_delimiter",
                            "preserve_original": "true"
                        }
                    },
                    "tokenizer": {
                        "autocomplete": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 70,
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
        return {"message": "success", "response": res}, "200"
    except RequestError as es1:
        return es1.info, es1.status_code

# autocomplete


@app.route('/<indexname>/autocomplete', methods=["POST"])
def autocomplete_size(indexname):
    # extracted the request body
    response = request.get_json()
    # extracted the input from the request body
    input = response["input"]
    pattern = re.compile('\W')
    # input is passed through sanitization
    sanitized_input = re.sub(pattern, ' ', input)
    if "size" in response.keys():
        size = response["size"]
        if size <= 0:
            return {"message": "Size should be greater than 0"}, 400
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
        return es1.info, es1.status_code

# search


@app.route('/search', methods=['GET', 'POST'])
def search():
    # extracted the request body
    response = request.get_json()
    # extracted the indexname from the request body
    indexname = response["indexname"]
    # extracted the size from the request body
    size = response["size"]
    # extracted the input from the request body
    input = response["input"]
    From = response["From"]
    banner_size = response["banner_size"]
    banner_from = response["banner_from"]

    # extracted dictionary of range fields and its values
    range_fields_value = response["range_fields_value"]
    # extracted dictionary of term fields and its values
    field_terms = response["filter_terms"]
    filter_list = []                                       # initialized empty list
    for field in field_terms.keys():
        if field == "category":
            return {"message": "Try 'category_name' instead of 'category'", "status_code": "400"}, 400
        elif field == "brand":
            return {"message": "Try 'brand_name' instead of 'brand'", "status_code": "400"}, 400
        else:
            filter_list.append({"terms": {field: field_terms[field]}})
    for range_field in range_fields_value.keys():
        filter_list.append({"range": {range_field: {
                           "gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
        print(
            {"range": {range_field: {"gte": range_fields_value[range_field]["min_val"], "lte": range_fields_value[range_field]["max_val"]}}})
    # extracted dictionary of sort fields and its sorting type
    sortlist = response["sortlist"]
    # extracted fields based on which search will be performed
    search_fields = response["search_fields"]
    if input == "*":
        res_1 = {}
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
                        {"match": {"bannercheck": "true"}}]
                }
            },
            "size": banner_size,
            "from": banner_from
        }
        banner_res = es.transport.perform_request(
            'POST', '/'+indexname+'/_search', body=body)
        res_1["search_response"] = search_res
        res_1["banner_response"] = banner_res
        res_1["by_brand"] = res_1["search_response"]["aggregations"]["by_brand"]["buckets"]
        res_1["by_category"] = res_1["search_response"]["aggregations"]["by_category"]["buckets"]
        return (res_1)
    pattern = re.compile('\W')
    # input went through sanitization
    sanitized_input = re.sub(pattern, ' ', input)
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
                                        "type": "cross_fields"
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
        if search_response["hits"]["total"]["value"] == 0 and len(search_response["suggest"]["mytermsuggester1"]) != 0 and len(search_response["suggest"]["mytermsuggester1"][0]["options"]) == 0:
            banner_keyword = sanitized_input
            body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"bannercheck": "true"}},
                            {"match": {"banner_keyword": sanitized_input}}
                        ]
                    }
                },
                "size": banner_size,
                "from": banner_from
            }
            banner_response = es.transport.perform_request(
                'POST', '/'+indexname+'/_search', body=body)
            body_null = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"bannercheck": "true"}},
                            {"match": {"banner_keyword": "null"}}
                        ]
                    }
                },
                "size": banner_size,
                "from": banner_from
            }
            banner_response_null = es.transport.perform_request(
                'POST', '/'+indexname+'/_search', body=body_null)
            print(banner_response)
            if banner_response["hits"]["total"]["value"]==0:
                banner_response["hits"]["hits"] = banner_response["hits"]["hits"] + \
                banner_response_null["hits"]["hits"]

            return {"Results": [], "banner_response": banner_response}, 404
        elif search_response["hits"]["total"]["value"] == 0 and len(search_response["suggest"]["mytermsuggester1"]) != 0:
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
                                            "type": "cross_fields"

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
            },
            "size": banner_size,
            "from": banner_from
        }
        banner_response = es.transport.perform_request(
            'POST', '/'+indexname+'/_search', body=body)
        body_null = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"bannercheck": "true"}},
                        {"match": {"banner_keyword": "null"}}
                    ]
                }
            },
            "size": banner_size,
            "from": banner_from
        }
        banner_response_null = es.transport.perform_request(
            'POST', '/'+indexname+'/_search', body=body_null)
        print(banner_response)
        if banner_response["hits"]["total"]["value"]==0:
            banner_response["hits"]["hits"] = banner_response["hits"]["hits"] + \
            banner_response_null["hits"]["hits"]

        res["search_response"] = search_response
        res["banner_response"] = banner_response
        res["by_brand"] = res["search_response"]["aggregations"]["by_brand"]["buckets"]
        res["by_category"] = res["search_response"]["aggregations"]["by_category"]["buckets"]
        return (res)
    except NotFoundError as es1:
        return es1.info, es1.status_code
    except RequestError as es2:
        return es2.info, es2.status_code


# update field by query
@app.route("/update_field_by_query", methods=['POST'])
def update_field_with_query():
    requestf = request.get_json()                   # extracted the request body
    # extracted indexname from the request body
    indexname = requestf["indexname"]
    # extracted query from the request body
    querylist = requestf["query"]
    # extracted updates which need to be performed from the request body
    updatelist = requestf["update"]
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
        if res["updated"] == 0:
            raise Exception("Doens't exist")
        return res
    except Exception as es1:
        return {"message": str(querylist)+" Products with the queries doesnt not exist"}, 404


# bulk update
@app.route("/bulk_update/<indexname>", methods=['POST'])
def update(indexname):
    # converted xml to dictionary
    bulk_data_syno = dict(xmltodict.parse(request.data))
    if "products" in bulk_data_syno["root"].keys():
        bulk_data = bulk_data_syno["root"]["products"]["product"]
        if str(type(bulk_data)) == "<class 'dict'>" or str(type(bulk_data)) == "<class 'collections.OrderedDict'>":
            bulk_data = [bulk_data]
        for data in bulk_data:
            data["list_price"] = float(data["list_price"])
            # extraction of category in to new key
            data["category_name"] = data["category"]
            # extraction of brand in to new key
            data["brand_name"] = data["brand"]
            if "seller_product" in data.keys():
                if str(type(data["seller_product"]["product"])) == "<class 'dict'>" or str(type(data["seller_product"]["product"])) == "<class 'collections.OrderedDict'>":
                    data["seller_product"]["product"] = [
                        data["seller_product"]["product"]]
            res = es.index(index=indexname, id=data["id"], body=data)
    if "synonym" in bulk_data_syno["root"].keys():
        synonymlist = bulk_data_syno["root"]["synonym"]["syno"]
        if str(type(synonymlist)) == "<class 'str'>":
            synonymlist = [synonymlist]
        try:
            file = open("synonym.txt", "a")
            file.write("\n")
            file.write("\n".join(synonymlist))
            file.close()

            with pysftp.Connection(host=config.myHostname, username=config.myUsername, password=config.myPassword) as sftp:
                print("Connection succesfully stablished ... ")
                localFilePath = 'synonym.txt'
                remoteFilePath = config.synonymPath
                sftp.put(localFilePath, remoteFilePath)
        except EOFError as ex:
            print("Caught the EOF error.")
            raise ex
        except IOError as e:
            print("Caught the I/O error.")
            raise e
        response = es.transport.perform_request(
            'POST', '/'+indexname+'/_reload_search_analyzers')
    if "banners" in bulk_data_syno["root"].keys():
        bannerlist = bulk_data_syno["root"]["banners"]["banner"]
        if str(type(bannerlist)) == "<class 'dict'>" or str(type(bannerlist)) == "<class 'collections.OrderedDict'>":
            bannerlist = [bannerlist]
        for data in bannerlist:
            if data["banner_keyword"] is None:
                data["banner_keyword"] = "null"
            res = es. index(index=indexname, id=data["id"], body=data)
    return "success"


# get synonym
@app.route('/get_synonym', methods=["GET"])
def get_synonym():
    requestf = request.get_json()                   # extracted the request body
    path = "synonym.txt"
    lines_final = []
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            syno = line.strip('\n')
            if syno != "":
                lines_final.append(syno)
    return {"synonyms": lines_final}


# delete synonym
@app.route('/delete_synonym', methods=["POST"])
def delete_synonym():
    # extraction of request body
    requestf = request.get_json()
    # extraction of synonyms which needs to be deleted
    synonyms = requestf["synonyms"]
    path = "synonym.txt"  # synonym.txt file path
    with open(path, "r") as f:
        lines = f.readlines()
        with open(path, "w") as f:
            for line in lines:
                # print(line.strip("\n").lower())
                if line.strip("\n").lower() != synonyms.lower():
                    f.write(line)
    with pysftp.Connection(host=config.myHostname, username=config.myUsername, password=config.myPassword) as sftp:
        print("Connection succesfully stablished ... ")
        localFilePath = 'synonym.txt'
        remoteFilePath = config.synonymPath
        sftp.put(localFilePath, remoteFilePath)
    return {"message": "Successfully Deleted"}


# Delete_by_query
@app.route("/<indexname>/delete_by_query", methods=['POST'])
def delete_field_with_query(indexname):
    requestf = request.get_json()                     # extraction of request body
    # extraction of query basis which product description needs to be deleted
    querylist = requestf["query"]
    query = []                                        # initialization of empty list
    for k in querylist:
        query.append({"term": k})
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
        if res["deleted"] == 0:
            return {"message": "Product with the query :"+str(querylist)+" not found"}, 404
        return {"message": "Number of products deleted:"+str(res["deleted"]), "response": res}
    except NotFoundError as es1:
        return es1.info, es1.status_code


# Delete Index
@app.route("/delete_index", methods=['POST'])
def delete_index():
    requestf = request.get_json()                      # extraction of request body
    # extraction of indexname from the request body
    indexname = requestf["indexname"]
    try:
        res = es.transport.perform_request(
            'DELETE', '/'+indexname)
        return {"message": "Successfully Deleted!", "response": res}, "200"
    except NotFoundError as es1:
        return es1.info, es1.status_code


@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr,
                 request.method, request.scheme, request.full_path, response.status)
    return response


if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)
