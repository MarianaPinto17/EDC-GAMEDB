import json
from random import random, randint

from django.shortcuts import redirect, render
import os
from django.contrib.admin.utils import flatten
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from SPARQLWrapper import SPARQLWrapper, JSON


# Create your views here.
def index(request):
    endpoint = "http://localhost:7200"
    repo_name = "gamesdb"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)
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
           game[gameid] = {key:res_tmp['obj']['value'] }
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
                publishers.append({value:""})
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
    tparam = {'game':game}
    return render(request, 'index.html', tparam)


def showGame(request, game_id):
    #print(game_id)
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    # session.execute("open dataset")

    single_game = "for $c in collection('dataset')//game where $c/@id='" + str(game_id) + "' return $c"
    #print(single_game)
    query = session.query(single_game)
    result = query.execute()
    result = xmltodict.parse(result)
    comments = []

    try:
        for comment in result['game']['comment']:
            #print(comment)
            if comment["@author"] == '':
                comment["@author"] = "Anonymous"
            comments.append((comment["@author"], comment["#text"]))
    except Exception as e:
        try:
            print(tuple(list(result['game']['comment'].values()))[0])
            if tuple(list(result['game']['comment'].values()))[0] == "":
                print("true")
                comments = [("Anonymous",tuple(list(result['game']['comment'].values()))[1])]
            else:
                comments = [tuple(list(result['game']['comment'].values()))]
        except:
            print("aqui")

    #print(comments)
    developers = []
    images = []
    thumbnails = []
    genres = [result['game']['genres']['genre']]
    print(result['game']['genres']['genre'])
    try:
        genres.extend(result['game']['tags']['tag'])
    except:
        pass
    flatten(genres)
    print(type(genres))
    genres = list(set(flatten(genres)))

    # print(result['game']['genres'])
    #print(result['game']['developers']['company'])


    try:
        for image in result['game']['gallery']['screenshots']['image']:
            images.append(list(image.values())[1])
            thumbnails.append(list(image.values())[0])
    except:
        pass

    #print(images)
    if len(result['game']['developers']['company']) > 1:
        for developer in result['game']['developers']['company']:
            developers.extend(list(developer.values()))
    else:
        developers = (list(result['game']['developers']['company'].values()))
        #print(developers)

    # print(genres)
    if result['game']['english_available'] == "True":
        result['game']['english_available'] = 'Yes'
    else:
        result['game']['english_available'] = 'No'

    new_params = {'game_title': result['game']['title'],
                  'game_image': result['game']['gallery']['header']['image']['full_size'],
                  'game_description': result['game']['description'],
                  'release': result['game']['release-date'],
                  'devs': developers,
                  'genres': genres,
                  'english': result['game']['english_available'],
                  'positive': result['game']['ratings']['positive'],
                  'negative': result['game']['ratings']['negative'],
                  'lower': result['game']['ownership']['lower_bound'],
                  'higher': result['game']['ownership']['upper_bound'],
                  'game_id': game_id,
                  'comments': reversed(comments),
                  'images': images,
                  'thumbnails': thumbnails,
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
                    filter regex(?name,\""""+game_id+"""\","i").
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
    tparams ={'error':False}
    if error:
        tparams['error'] = True
    return render(request, "form.html", tparams)

def newGame(request):
    print(request.POST)
    rooter = Element('games')
    root = SubElement(rooter,'game')
    id = str(randint(1,150))
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
    file = open('cenas.xml',"w")
    file.write(xml)


    xsd_name = "dataset.xsd"
    xsd_file = os.path.join(BASE_DIR,xsd_name)
    tree = ET.fromstring(xml)
    xsd_parsed = ET.parse(xsd_file)
    xsd = ET.XMLSchema(xsd_parsed)

    if xsd.validate(tree):
        session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
        session.execute("open dataset")
        query_add_game = "let $games := doc('dataset')" + "let $node := '" + tostring(root).decode('utf-8') + "' return insert node fn:parse-xml(" + "$node) as last into $games "


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
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    session.execute("open dataset")

    input1 = "import module namespace games = 'com.games' at '" \
             + os.path.join(BASE_DIR,'webapp/xslt/queries.xq') \
             + "';<genres>{games:get_all_genres()}</genres>"
    query1 = session.query(input1)
    genres = query1.execute()
    #print(genres)
    input2 = "import module namespace games = 'com.games' at '" \
             + os.path.join(BASE_DIR, 'webapp/xslt/queries.xq') \
             + "';<tags>{games:get_all_tags()}</tags>"
    query2 = session.query(input2)

    tags = query2.execute()
    #print(tags)

    generos = xmltodict.parse(genres)
    categorias = xmltodict.parse(tags)
    #print(categorias['tags']['tag'])

    #print(cenas)
    genres = generos['genres']['genre']
    genres.extend(categorias['tags']['tag'])
    genres = sorted(list(set(genres)))
    #print(genres)

    tparams = {'genres': genres}


    return render(request, 'adv_search.html', tparams)




