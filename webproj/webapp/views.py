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
                    game:440 pred:positive-ratings ?ratings .
   					 
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
    for i in range(0, len(screenshots),2):
        full_size.append(screenshots[i])
    for i in range(1, len(screenshots),2):
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
    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
                 PREFIX pred: <http://gamesdb.com/predicate/>
                 DELETE {?game ?pred ?obj.}
                 WHERE{
                    ?game ?pred ?obj .
                    ?game pred:name ?name.
                    filter regex(?name,\"""" + game_id + """\","i").
                 }

            """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    return redirect(index)


def searchGame(request, pattern):
    print("here")
    pattern = pattern.replace("%20", " ").replace("'", "")
    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
                
            """
    """session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    session.execute("open dataset")
    search_query = "for $games in collection('dataset')/games/game for $genre in $games//genre where contains(lower-case(" \
                   "$games/title), lower-case('" + pattern + "')) or contains(lower-case($genre), lower-case('" + pattern \
                   + "')) return $games "
    query = session.query(search_query)

    result = "<?xml version=\"1.0\"?>" + "\n\r<games>\n" + query.execute() + "\n</games>\n"
    xsl_file = os.path.join(BASE_DIR, 'webapp/xslt/' + 'homepage.xsl')

    tree = ET.fromstring(result)

    visited = set()
    for el in tree.iter('game'):
        print(el)
        if 'id' in el.keys():
            current = el.get('id')
            if current in visited:
                el.getparent().remove(el)
            else:
                visited.add(current)

    xslt = ET.parse(xsl_file)
    transform = ET.XSLT(xslt)
    newdoc = transform(tree)

    session.close()
    tparams = {
        'content': newdoc
    }"""
    return render(request, 'index.html', tparams)


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

                """

    """session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    session.execute("open dataset")
    search_query = "for $games in collection('dataset')/games/game for $genre in $games//genre for $tags in " + "$games//tag where contains(lower-case(" +"$games/title), lower-case('" + pattern + "')) or contains(lower-case($genre), lower-case('" + pattern +  "'))" + " or contains(lower-case($tags), lower-case('" + pattern + "')) return $games "
    print(search_query)
    query = session.query(search_query)

    result = "<?xml version=\"1.0\"?>" + "\n\r<games>\n" + query.execute() + "\n</games>\n"
    xsl_file = os.path.join(BASE_DIR, 'webapp/xslt/' + 'homepage.xsl')

    tree = ET.fromstring(result)

    visited = set()
    for el in tree.iter('game'):

        if 'id' in el.keys():
            current = el.get('id')
            if current in visited:
                el.getparent().remove(el)
            else:
                visited.add(current)

    xslt = ET.parse(xsl_file)
    transform = ET.XSLT(xslt)
    newdoc = transform(tree)

    session.close()
    tparams = {
        'content': newdoc
    }"""
    return render(request, 'index.html')


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
    rooter = Element('games')
    root = SubElement(rooter, 'game')
    id = str(randint(1, 150))
    root.set('id', id)
    title = SubElement(root, 'title')
    title.text = request.POST['title']
    date = SubElement(root, 'release-date')
    date.text = request.POST['year']
    english = SubElement(root, 'english_available')
    if request.POST['english'] == 'Y':
        english.text = 'True'
    else:
        english.text = 'False'
    developers = SubElement(root, 'developers')
    for developer in request.POST['developers'].split(';'):
        devnode = SubElement(developers, 'company')
        devname = SubElement(devnode, 'name')
        devname.text = developer
    publishers = SubElement(root, 'publishers')
    required_age = SubElement(root, 'required_age')
    required_age.text = request.POST['rating']
    categories = SubElement(root, 'categories')
    genres = SubElement(root, 'genres')
    for genre in request.POST['genres'].split(";"):
        genrenode = SubElement(genres, 'genre')
        genrenode.text = genre
    tags = SubElement(root, 'tags')
    ratings = SubElement(root, 'ratings')
    positive = SubElement(ratings, 'positive')
    positive.text = "0"
    negative = SubElement(ratings, 'negative')
    negative.text = "0"
    playtime = SubElement(root, 'playtime')
    average = SubElement(playtime, 'average')
    average.text = "0"
    median = SubElement(playtime, 'median')
    median.text = "0"

    owner = SubElement(root, 'ownership')
    lower = SubElement(owner, 'lower_bound')
    lower.text = "0"
    high = SubElement(owner, 'upper_bound')
    high.text = "0"
    price = SubElement(root, 'price')
    price.text = request.POST["price"]
    description = SubElement(root, 'description')
    description.text = request.POST['description']
    gallery = SubElement(root, 'gallery')
    header = SubElement(gallery, 'header')
    image = SubElement(header, 'image')
    full_size = SubElement(image, 'full_size')
    full_size.text = request.POST['url']

    xml = tostring(rooter).decode('utf-8')
    file = open('cenas.xml', "w")
    file.write(xml)

    xsd_name = "dataset.xsd"
    xsd_file = os.path.join(BASE_DIR, xsd_name)
    tree = ET.fromstring(xml)
    xsd_parsed = ET.parse(xsd_file)
    xsd = ET.XMLSchema(xsd_parsed)

    if xsd.validate(tree):
        session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
        session.execute("open dataset")
        query_add_game = "let $games := doc('dataset')" + "let $node := '" + tostring(root).decode(
            'utf-8') + "' return insert node fn:parse-xml(" + "$node) as last into $games "

        try:
            query = session.query(query_add_game)
            query.execute()
        except:
            return redirect(addGame, error=True)
        return redirect(showGame, game_id=id)
    else:
        return redirect(addGame, error=True)


def apply_filters(request):
    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
    query = """
                PREFIX mov: <http://gamesDB.com/predicate/>
                SELECT distinct 
                WHERE { 
                    
                """

    return render(request, 'index.html', tparams)


def adv_search(request):
    query = """PREFIX pred: <http://gamesdb.com/predicate/>
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
