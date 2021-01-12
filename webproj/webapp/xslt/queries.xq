module namespace games = "com.games";

declare function games:get_all_genres() as element()*{
  let $genres := doc("dataset")//genres
  for $genre in distinct-values($genres/genre)
  return <genre>{$genre}</genre>
};

declare function games:get_all_tags() as element()*{
  let $tags := doc("dataset")//tags
  for $tag in distinct-values($tags/tag)
  return <tag>{$tag}</tag>
};

declare function games:apply_filters($cat, $dev, $year, $order, $title) as element()*{
    for $games in collection('dataset')/games/game
        for $genre in $games//genre
        for $tags in $games//tag
        for $devs in $games/developers/company//name
            where contains(lower-case($games/title), lower-case($title))
            and (contains(lower-case($genre), lower-case($cat))
            or contains(lower-case($tags), lower-case($cat)))
            and contains(lower-case($games/release-date), $year)
            and contains(lower-case($devs), lower-case($dev))


    return $games



};