import json
from io import open
import glob
import nltk

files = glob.glob("question_data_english/*.json")
# iterate over the list getting each file

entity_arr = []
for fle in files:
    object_name = fle.split('_')[3]
    with open(fle) as data_file:
        data = json.load(data_file)

    list_sents = data[object_name]
    pass
    with open("normalized_data.txt","a",encoding="utf-8") as f:
        for sent in list_sents:
            sent_token = []             #list of words in sent
            sent_data = sent["data"]
            list_tup = []#list of object in sentence
            for element in sent_data:

                if element["text"] == " " or "\n" in element["text"]:
                    continue
                list_word = element["text"].strip().split(" ")
                sent_token.extend(list_word)
                if "entity" in element:
                    entity = element["entity"]
                    if entity == "location_name":
                        entity = "theatre_name"
                    if entity == "geographic_poi":
                        entity = "location"
                    entity_arr.append(entity)
                    for i in xrange(0,len(list_word)):
                        if list_word[i] == "":
                            continue
                        if i == 0:
                            list_tup.append(tuple((list_word[i],"B-"+entity + "\n")))
                            #line =u" ".join([list_word[i],"B-"+entity + "\n"])
                        else:
                            list_tup.append(tuple((list_word[i], "I-" + entity + "\n")))
                            #line = u" ".join([list_word[i], "I-" + entity + "\n"])

                        #f.write(line)
                else:
                    for word in list_word:
                        list_tup.append(tuple((word,"O\n")))
                        #line = u" ".join([word,"O\n"])
                        #f.write(line)
            sent_token = [value for value in sent_token if value!= '']
            tagged = nltk.pos_tag(sent_token)
            pass
            for i in xrange(len(tagged)):
                line = " ".join([list_tup[i][0],tagged[i][1],list_tup[i][1]])
                f.write(line)



            f.write(u"\n")
        f.close()
x = list(set(entity_arr))
print x