import json
from random import random, randint

from django.shortcuts import redirect, render
import os
from django.contrib.admin.utils import flatten
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "http://localhost:7200"
repo_name = "gamesdb"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


# Create your views here.
def index(request):
    query = """
                   PREFIX pred: <http://gamesdb.com/predicate/>
                SELECT ?game ?pred ?obj
                WHERE{
                    ?game ?pred ?obj .
                    ?game pred:positive-ratings ?ratings .
                }
                
                """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    res = res['results']['bindings']
    game = {}
    developers = []
    categories = []
    screenshots = []
    publishers = []
    for res_tmp in res:
        gameid = res_tmp['game']['value'].split("/")[-1]
        key = res_tmp['pred']['value'].split("/")[-1]
        if gameid not in game.keys():
            game[gameid] = {key: res_tmp['obj']['value']}
            developers = []
            categories = []
            screenshots = []
            publishers = []
        else:
            tmp = game[gameid]
            value = res_tmp['obj']['value']
            if key == "screenshots":
                screenshots.append(value)
                tmp_dic = {key: screenshots}
            elif key == "category":
                categories.append({value: ""})
                tmp_dic = {key: categories}
            elif key == "developers":
                developers.append({value: ""})
                tmp_dic = {key: developers}
            elif key == "publishers":
                publishers.append({value: ""})
                tmp_dic = {key: publishers}
            else:
                tmp_dic = {key: res_tmp['obj']['value']}

            tmp.update(tmp_dic)
    print(game['440'])

    for game_tmp in game.keys():
        developer_index = 0
        publisher_index = 0
        category_index = 0
        for developer_list in game[game_tmp]['developers']:
            developer = list(developer_list.keys())[0]
            query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                        prefix predicate: <http://gamesdb.com/predicate/>
                            select ?name where{
                                company:""" + developer.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['developers'][developer_index].update({developer: res[0]['name']['value']})
            developer_index = developer_index + 1

        for publisher_list in game[game_tmp]['publishers']:
            publisher = list(publisher_list.keys())[0]
            query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                        prefix predicate: <http://gamesdb.com/predicate/>
                            select ?name where{
                                company:""" + publisher.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['publishers'][publisher_index].update({publisher: res[0]['name']['value']})
            publisher_index = publisher_index + 1

        for category_list in game[game_tmp]['category']:
            category = list(category_list.keys())[0]
            query = """ PREFIX category: <http://gamesdb.com/entity/categories/>
                        prefix predicate: <http://gamesdb.com/predicate/>
                            select ?name where{
                                category:""" + category.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['category'][category_index].update({category: res[0]['name']['value']})
            category_index = category_index + 1

    print(game['440'])
    tparam = {'game': game}
    return render(request, 'index.html', tparam)


def showGame(request, game_id):
    # print(game_id)
    query = """PREFIX pred: <http://gamesdb.com/predicate/>
                   PREFIX game: <http://gamesdb.com/entity/game/>
                SELECT ?pred ?obj ?id
                WHERE{
                    game:""" + str(game_id) + """ ?pred ?obj .	 
                }
            """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    res = res['results']['bindings']
    developers = []
    categories = []
    screenshots = []
    publishers = []
    game = {}
    for res_tmp in res:
        key = res_tmp['pred']['value'].split("/")[-1]
        value = res_tmp['obj']['value']
        if key == "screenshots":
            screenshots.append(value)
            tmp_dic = {key: screenshots}
        elif key == "category":
            categories.append({value: ""})
            tmp_dic = {key: categories}
        elif key == "developers":
            developers.append({value: ""})
            tmp_dic = {key: developers}
        elif key == "publishers":
            publishers.append({value: ""})
            tmp_dic = {key: publishers}
        else:
            tmp_dic = {key: res_tmp['obj']['value']}

        game.update(tmp_dic)

    developer_index = 0
    publisher_index = 0
    category_index = 0
    for developer_list in game['developers']:
        developer = list(developer_list.keys())[0]
        query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    company:""" + developer.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        game['developers'][developer_index].update({developer: res[0]['name']['value']})
        developer_index = developer_index + 1

    for publisher_list in game['publishers']:
        publisher = list(publisher_list.keys())[0]
        query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    company:""" + publisher.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        game['publishers'][publisher_index].update({publisher: res[0]['name']['value']})
        publisher_index = publisher_index + 1

    for category_list in game['category']:
        category = list(category_list.keys())[0]
        query = """ PREFIX category: <http://gamesdb.com/entity/categories/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    category:""" + category.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        game['category'][category_index].update({category: res[0]['name']['value']})
        category_index = category_index + 1

    full_size = []
    thumbnail = []
    for i in range(0, len(screenshots), 2):
        full_size.append(screenshots[i])
    for i in range(1, len(screenshots), 2):
        thumbnail.append(screenshots[i])
    print(thumbnail)

    new_params = {'game_title': game['name'],
                  'game_image': game['header'],
                  'game_description': game['description'],
                  'release': game['date'],
                  'devs': game['developers'],
                  'genres': game['category'],
                  'english': game['english'],
                  'positive': game['positive-ratings'],
                  'negative': game['negative-ratings'],
                  'lower': game['lower-ownership'],
                  'higher': game['upper-ownership'],
                  'game_id': game_id,
                  'images': full_size,
                  'thumbnails': thumbnail
                  }

    return render(request, 'game.html', new_params)


def deleteGame(request, game_id):

    query = """ PREFIX pred: <http://gamesdb.com/predicate/>
                PREFIX game: <http://gamesdb.com/entity/game/>
                Delete
                WHERE{
    				game:"""+str(game_id)+" ?pred ?obj }"

    print(query)
    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)
    print(res)

    return redirect(index)


def searchGame_2(request):
    print(request.POST)
    pattern = request.POST['pattern']
    print(pattern)
    pattern = pattern.replace("%20", " ").replace("'", "")

    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
                    PREFIX pred: <http://gamesdb.com/predicate/>
                   PREFIX game: <http://gamesdb.com/entity/game/>
                
				SELECT ?game ?pred ?obj
				WHERE{
    				?game ?pred ?obj.
    				?game pred:name ?name .
    				?game pred:positive-ratings ?ratings.
    			filter(contains(lcase(?name), \"""" + pattern.lower() + "\"))}"

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(query)
    res = json.loads(res)
    print(res)
    res = res['results']['bindings']
    game = {}
    developers = []
    categories = []
    screenshots = []
    publishers = []
    for res_tmp in res:
        gameid = res_tmp['game']['value'].split("/")[-1]
        key = res_tmp['pred']['value'].split("/")[-1]
        if gameid not in game.keys():
            game[gameid] = {key: res_tmp['obj']['value']}
            developers = []
            categories = []
            screenshots = []
            publishers = []
        else:
            tmp = game[gameid]
            value = res_tmp['obj']['value']
            if key == "screenshots":
                screenshots.append(value)
                tmp_dic = {key: screenshots}
            elif key == "category":
                categories.append({value: ""})
                tmp_dic = {key: categories}
            elif key == "developers":
                developers.append({value: ""})
                tmp_dic = {key: developers}
            elif key == "publishers":
                publishers.append({value: ""})
                tmp_dic = {key: publishers}
            else:
                tmp_dic = {key: res_tmp['obj']['value']}

            tmp.update(tmp_dic)


    for game_tmp in game.keys():
        developer_index = 0
        publisher_index = 0
        category_index = 0
        for developer_list in game[game_tmp]['developers']:
            developer = list(developer_list.keys())[0]
            query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    company:""" + developer.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['developers'][developer_index].update({developer: res[0]['name']['value']})
            developer_index = developer_index + 1

        for publisher_list in game[game_tmp]['publishers']:
            publisher = list(publisher_list.keys())[0]
            query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    company:""" + publisher.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['publishers'][publisher_index].update({publisher: res[0]['name']['value']})
            publisher_index = publisher_index + 1

        for category_list in game[game_tmp]['category']:
            category = list(category_list.keys())[0]
            query = """ PREFIX category: <http://gamesdb.com/entity/categories/>
                            prefix predicate: <http://gamesdb.com/predicate/>
                                select ?name where{
                                    category:""" + category.split("/")[-1] + " predicate:name ?name.}"

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
            res = json.loads(res)
            res = res['results']['bindings']
            game[game_tmp]['category'][category_index].update({category: res[0]['name']['value']})
            category_index = category_index + 1

    tparam = {'game': game}
    return render(request, 'index.html', tparam)




def news_feed(request):
    xml_link = "https://metro.co.uk/entertainment/gaming/feed/"
    xml_file = requests.get(xml_link)
    xslt_name = 'rss.xsl'
    xsl_file = os.path.join(BASE_DIR, 'webapp/xslt/' + xslt_name)
    tree = ET.fromstring(xml_file.content)
    xslt = ET.parse(xsl_file)
    transform = ET.XSLT(xslt)
    newdoc = transform(tree)
    tparams = {
        'content': newdoc,
    }

    return render(request, 'news.html', tparams)


def addComment(request, game_id):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    session.execute("open dataset")
    print(request.POST)
    comment = request.POST["comment"]

    root = Element('comment')
    root.text = request.POST["comment"]
    root.set('author', request.POST['nickname'])

    query_add_comment = "let $games := doc('dataset')//game for $game in $games where $game[@id='" + str(
        game_id) + "']" + " let $node := '" + tostring(root).decode('utf-8') + "' return insert node fn:parse-xml(" \
                                                                               "$node) as last into $game "
    print(query_add_comment)
    query = session.query(query_add_comment)
    query.execute()

    return redirect(showGame, game_id=game_id)


def addGame(request, error=False):
    tparams = {'error': False}
    if error:
        tparams['error'] = True
    return render(request, "form.html", tparams)


def newGame(request):
    print(request.POST)
    id = str(randint(1, 150))
    title = request.POST['title']
    date = request.POST['year']
    if request.POST['english'] == 'Y':
        english = 'True'
    else:
        english = 'False'

    developers_post = []
    for developer in request.POST['developers'].split(';'):
        developers_post.append(developer)

    required_age = request.POST['rating']
    genres = []
    for genre in request.POST['genres'].split(";"):
        genres.append(genre)

    positive = "0"
    negative = "0"
    average = "0"

    median = "0"
    lower = "0"
    high = "0"
    price = request.POST["price"]
    description = request.POST['description']

    full_size = request.POST['url']

    query = """ PREFIX pred: <http://gamesdb.com/predicate/>
                    PREFIX game: <http://gamesdb.com/entity/game/>
                    SELECT distinct ?cat
                    WHERE{
                        ?game ?pred ?obj .
                        ?game pred:category ?cat .

                    }"""
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    res = res['results']['bindings']
    categories = {}
    for cat in res:
        category = cat['cat']['value']
        query = """ PREFIX category: <http://gamesdb.com/entity/categories/>
                                        prefix predicate: <http://gamesdb.com/predicate/>
                                            select ?name where{
                                                category:""" + category.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        categories[category] = res[0]['name']['value']


    #check if category is on db
    cat_keys = []

    for cat in genres:
        if cat in categories.values():
            cat_keys.append(list(categories.keys())[list(categories.values()).index(cat)])
    print(cat_keys)

    query = """ PREFIX pred: <http://gamesdb.com/predicate/>
                       PREFIX game: <http://gamesdb.com/entity/game/>
                       SELECT distinct ?dev
                       WHERE{
                           ?game ?pred ?obj .
                           ?game pred:developers ?dev .

                       }"""
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    res = res['results']['bindings']
    developers = {}
    for dev in res:
        developer = dev['dev']['value']
        query = """ PREFIX company: <http://gamesdb.com/entity/company/>
                                           prefix predicate: <http://gamesdb.com/predicate/>
                                               select ?name where{
                                                   company:""" + developer.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        developers[developer] = res[0]['name']['value']

    dev_keys = []

    for dev in developers_post:
        if dev in developers.values():
            dev_keys.append(list(developers.keys())[list(developers.values()).index(dev)])
    print(dev_keys)


    to_insert = []
    to_insert.append("game:"+id+ " predicate:name \"" + title + "\"")
    to_insert.append("game:"+id+ " predicate:date \"" + date + "\"")
    to_insert.append("game:"+id+ " predicate:english \"" + english + "\"")
    to_insert.append("game:"+id+ " predicate:positive-ratings \"" + positive + "\"")
    to_insert.append("game:"+id+ " predicate:negative-ratings \"" + negative + "\"")
    to_insert.append("game:"+id+ " predicate:average-playtime \"" + average + "\"")
    to_insert.append("game:"+id+ " predicate:median-playtime \"" + median + "\"")
    to_insert.append("game:"+id+ " predicate:lower-ownership \"" + lower + "\"")
    to_insert.append("game:"+id+ " predicate:upper-ownership \"" + high + "\"")
    to_insert.append("game:"+id+ " predicate:price \"" + price + "\"")
    to_insert.append("game:"+id+ " predicate:description \"" + description + "\"")
    to_insert.append("game:"+id+ " predicate:header \"" + full_size + "\"")
    to_insert.append("game:"+id+ " predicate:age " + "ages:not_available")



    for dev in dev_keys:
        to_insert.append("game:"+id+ " predicate:developers company:" + dev.split("/")[-1])
        to_insert.append("game:"+id+ " predicate:publishers company:" + dev.split("/")[-1])


    for cat in cat_keys:
        to_insert.append("game:"+id+ " predicate:category categories:" + cat.split("/")[-1])

    for query in to_insert:
        to_query = """PREFIX predicate: <http://gamesdb.com/predicate/>
                   PREFIX game: <http://gamesdb.com/entity/game/>
                   PREFIX company: <http://gamesdb.com/entity/company/>
                   PREFIX categories: <http://gamesdb.com/entity/categories/>
                   
                   INSERT DATA{
                    """ + query + "}"
        print(to_query)
        payload_query = {"update": to_query}
        print(accessor.sparql_update(body=payload_query, repo_name=repo_name))


    print(id)
    return redirect(showGame, game_id=id)


def apply_filters(request):
    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
                PREFIX pred: <http://gamesdb.com/predicate/>
                PREFIX cat: <http://gamesdb.com/entity/categories/>
                SELECT distinct ?category
                WHERE{
                    ?game ?pred ?obj .
                    ?game pred:category ?category .
   					 
                }
            """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    categories=[]
    for e in res['results']['bindings']:
        for v in e.values():
            categories.append(v['value'])

    query = """
                PREFIX pred: <http://gamesdb.com/predicate/>
                PREFIX age: <http://gamesdb.com/entity/ages/>
                SELECT distinct ?age
                WHERE {
    	            ?game ?pred ?obj .
                    ?game pred:age ?age
                } order by ?age
    
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    age = []

    for e in res['results']['bindings']:
        for v in e.values():
            age.append(v['value'])

    query = """
                    PREFIX pred: <http://gamesdb.com/predicate/>
                    PREFIX company: <http://gamesdb.com/entity/company/>
                    SELECT distinct ?company
                    WHERE {
        	            ?game ?pred ?obj .
                        ?game pred:company ?company
                    } order by ?company

                """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    companies = []

    for e in res['results']['bindings']:
        for v in e.values():
            companies.append(v['value'])

    query = """
                       PREFIX pred: <http://gamesdb.com/predicate/>
                       PREFIX game: <http://gamesdb.com/entity/game/>
                       SELECT distinct ?game
                       WHERE {
           	                ?game ?pred ?obj .
                            ?game pred:game ?game
                       } order by ?game

                   """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    games = []
    for e in res['results']['bindings']:
        for v in e.values():
            games.append(v['value'])

    query = """
                    PREFIX pred: <http://gamesdb.com/predicate/>
                    SELECT distinct ?name ?pred ?obj
                    WHERE {
                        ?game ?pred ?obj .
                        ?game pred:company ?company .
                        ?game pred:age ?age .
                        ?game pred:category ?category .
                        ?company pred:name ?company_name .
                        ?age pred:age ?age_value .
                        ?category pred:name ?category_name .
                        ?game pred:name ?game_name
                        ?game pred:date ?date .

            """


    categoriesToQuery = []

    for g in categories:
        if g in request.POST:
            categoriesToQuery.append(g)

    if len(categoriesToQuery) != 0:
        aux = ""
        for g in categoriesToQuery:
            aux += "\"" + g + "\","
        aux = aux[:-1]
        query += """FILTER(?category_name IN(""" + aux + """))"""

    if 'age' in request.POST:
        query += """FILTER (?age_value = \""""+ request.POST['age'] + """\")"""

    if 'companies'in request.POST:
        query += """FILTER (?company_name = \"""" + request.POST['companies'] + """\")"""

    if 'games' in request.POST:
        query += """FILTER (?game_name = \"""" + request.POST['games'] + """\")"""
        query += """FILTER (?date = \"""" + request.POST['games'] + """\")"""

    tparams = {
        "categories": categories,
        "age": age,
        "companies": companies,
        "games": games
    }

    return render(request, 'index.html', tparams)


def adv_search(request):
    query = """ PREFIX pred: <http://gamesdb.com/predicate/>
                PREFIX game: <http://gamesdb.com/entity/game/>
                SELECT distinct ?cat
                WHERE{
                    ?game ?pred ?obj .
                    ?game pred:category ?cat .
   					 
                }"""
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    res = res['results']['bindings']
    categories = {}
    for cat in res:
        category = cat['cat']['value']
        query = """ PREFIX category: <http://gamesdb.com/entity/categories/>
                                    prefix predicate: <http://gamesdb.com/predicate/>
                                        select ?name where{
                                            category:""" + category.split("/")[-1] + " predicate:name ?name.}"

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
        res = json.loads(res)
        res = res['results']['bindings']
        categories[category] = res[0]['name']['value']

    print(categories)

    tparams = {'genres': categories}

    return render(request, 'adv_search.html', tparams)


def searchdb(request):
    pattern = request.POST['pattern_db']
    pattern = pattern.replace("%20", " ").replace("'", "")

    endpoint = "https://dbpedia.org/sparql"

    query = """SELECT *
    WHERE
         {
            ?term rdfs:label """ + "\""+pattern+"\"@en}"
    print(query)
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()
    print(result)