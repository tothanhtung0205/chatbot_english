import json
from io import open
with open("train_BookRestaurant_full.json","r") as f:
    data = json.load(f)
    xxx = data["BookRestaurant"]
    list_entity = []
    for sent in xxx:
        word_list = sent["data"]
        for word in word_list:
            if "entity" in word:
                if word["entity"] == "sort":
                    word.pop('entity')
                else:
                    list_entity.append(word["entity"])

    x = list(set(list_entity))
    print x
#with open("normalize_BR.json","w") as f:


