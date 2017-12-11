import random


def load_shuffle_data():
    sen = []
    sen_list = []
    with open("normalized_data.txt","r") as f:
        for line in f:
            if line!= '\n':
                sen.append(line)
            else:
                sen_list.append(sen)
                sen = []
    print("Loaded total " + str(len(sen_list)) + " sentences.")
    random.shuffle(sen_list)
    return sen_list

def save_file(list_sent,file_name):
    with open(file_name,'w') as f:
        for sent in list_sent:
            for word in sent:
                f.write(word)
            f.write('\n')
        f.close()
def normal_split(corpus):
    test_size = len(corpus)/5
    test = corpus[:test_size]
    train = corpus[test_size:]
    save_file(test,"train_test_data/test_nor.txt")
    save_file(train,"train_test_data/train_nor.txt")


normal_split(load_shuffle_data())

def k_fold_split(corpus):
    pass





