# Recommender System

The New York Public Library provides an enormous collection of digital items, such as images, maps, sound recordings, or videos. At the beginning of this project, there were in total 765,395 items, about 52% of which were tagged with topics. The recommender system is implemented as a website that allows the user to enter a query and suggests tags of the New York Public Library Digital Collections similar to the query.

### Three different approaches are used in the recommender system:

- a graph of topics where topics are its nodes, and the co-occurrence of topics in items' descriptions are its edges. All the edges received a weight representing the number of topics' co-occurences. Topics matching the user's query are found, and their neighbors with the edges that have the biggest weight are used as recommendations.

- a vector space model trained on the English Wikipedia. With the help of the model, the words that are semantically closest to the query are determined, and the topics that match these words are recommended to the user.

- the WordNet. With the WordNet, the synonyms, antonyms, hypernyms and hyponyms of the query are found, and the topics corresponding to these words serve as recommendations for the user.

### Example:

- for the “jazz”, the system suggests the following topics: “Violinists”, “African American composers”, “Pianists”, “Trumpet players”, “Saxophonists”, “Special events”, “Blacks”, “Popular music”, “Music”, “Bands (Music)”
