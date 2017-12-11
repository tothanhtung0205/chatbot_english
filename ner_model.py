import random
from io import open
from lib2to3.pgen2 import token

import nltk

import sklearn_crfsuite
from sklearn.externals import joblib
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn_crfsuite import metrics
from intent import predict_ex,load_model

vectorizer = load_model('model_intent/vectorizer.pkl')
uni_big = load_model('model_intent/uni_big.pkl')


def contains_digit(str):
    for char in str:
        if char.isdigit():
            return True
    return False

def is_full_name(word):
    # To_Thanh_Tung return true
    # To_thanh_tung return false

    if '_' not in word:
        return  False

    temp = word.split('_')
    for token in temp:
        if token.istitle() == False:
            return False
    return True

def get_shape(word):
    shape = ""
    if word.isdigit():      # 123,33,52123
        shape = "so"
    elif contains_digit(word):      #a12,15B,2231XXX
        shape = "ma"
    elif word.isupper():            #UBND,CLGT,...
        shape = "viet hoa"
    elif word.istitle():            #Nam,An,Huy.....
        shape = 'title'
    elif word.islower():            #abc,xyz
        shape = 'viet thuong'
    else:
        shape = 'other'             #mEo,iPhone
    return shape

def single_features(sent, i):

    raw_word_0 = sent[i][0]
    word_0 = sent[i][0].lower()
    postag_0 = sent[i][1]

    word_minus_1 = sent[i-1][0].lower() if i>0 else "BOS"
    postag_minus_1 = sent[i-1][1] if i>0 else "BOS"

    word_minus_2 = sent[i-2][0].lower() if i>1 else "BOS"
    postag_minus_2 = sent[i-2][1] if i>1 else "BOS"

    word_add_1 = sent[i+1][0].lower() if i<len(sent)-1 else "EOS"
    postag_add_1 = sent[i+1][1] if i < len(sent)-1 else "EOS"


    word_add_2 = sent[i + 2][0].lower() if i < len(sent)-2  else "EOS"
    postag_add_2 = sent[i + 2][1] if i < len(sent)-2 else "EOS"

    O_0 = get_shape(raw_word_0)


    features = {
        # co the them chunk va regular express


        'bias': 1.0,
        'W(0)': word_0,  # W_0,
        'P(0)': postag_0,  # P_0
        'O(0)': O_0,

        #"gazette":get_gazette_type(word_0),
        'L2(0)':len(word_0),                 #do dai tu
        #'w2v':w2v,

        'W(-1)':word_minus_1,
        'P(-1)':postag_minus_1,
        #'G(-1)':get_gazette_type(word_minus_1),

        'W(-2)':word_minus_2,
        'P(-2)':postag_minus_2,
        #'G(-2)':get_gazette_type(word_minus_2),


        'W(+1)':word_add_1,
        'P(+1)':postag_add_1,
        #'G(+1)': get_gazette_type(word_add_1),


        'W(+2)':word_add_2,
        'P(+2)':postag_add_2,
        #'G(+2)':get_gazette_type(word_add_2),

        'W(-1)+W(0)':word_minus_1+"+"+word_0,
        'W(0)+W(1)' :word_0+"+"+word_add_1,


        'P(-1)+P(0)':postag_minus_1+'+'+postag_0,
        'P(0)+P(1)':postag_0+'+' +postag_add_1,

        'W(0)+P(0)':word_0+'+'+postag_0,
        'W(0)+P(1)':word_0+'+'+postag_add_1,
        'W(0)+P(-1)': word_0 + '+' + postag_minus_1,

        'W(0)+O(0)':word_0+'+'+O_0,
    }
    return features

def word2features(sent, i):
    features = {}
    features.update(single_features(sent,i))
    return features

def sent2features(sent):

    sent_text = " ".join([tup[0] for tup in sent])
    intent = predict_ex(sent_text,vectorizer,uni_big)
    list = []
    for i in xrange(len(sent)):
        word_i =  word2features(sent,i)
        word_i.update({"intent":intent})
        list.append(word_i)
    return list

def sent2labels(sent):
    labels = []
    for tup in sent:
        try:
            labels.append(tup[2])
        except:
            labels.append('O\n')
    return labels

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def read_file(file_name):
    sents = []
    sequence = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                sents.append(sequence)
                sequence = []
            else:
                line = line.encode('utf-8')
                word_pos_label = tuple(filter(None, line.split(' ')))
                sequence.append(word_pos_label)
    return sents


def fit(model,train_path):
    #training phase
    try:
        crf = joblib.load(model)
        print 'load model completed !!!'
        return crf
    except: crf = None
    print "read train_data..."
    train_sents = read_file(train_path)
    print "featuring sentence..."
    X_train = []
    i = 0
    for s in train_sents:
        X_train.append(sent2features(s))
        i+=1
        print("featuring sentence " + str(i))
    y_train = [sent2labels(s) for s in train_sents]


    c2_rs =  0.1
    c1_rs = 0.1
    if crf == None:
        print ("Training CRFs model.....")
        crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=c1_rs,
            c2=c2_rs,
            max_iterations=100,
            all_possible_transitions=True,
        )

        crf.fit(X_train, y_train)
        joblib.dump(crf, model)
        print "Training completed!!!"
        return crf
        #estimate model_intent...




def estimate(model,test_path):
    print ("Estimate model.. : \n")
    crf = joblib.load(model)
    test_sents = read_file(test_path)
    X_test = []
    i = 0
    for s in test_sents:
        X_test.append(sent2features(s))
        i += 1
        print("featuring sentence test " + str(i))

    #X_test = [sent2features(s) for s in test_sents]

    y_test = [sent2labels(s) for s in test_sents]
    labels = list(crf.classes_)
    pass
    labels.remove('O\n')
    y_pred = crf.predict(X_test)
    kq = metrics.flat_f1_score(y_test, y_pred,
                          average='weighted', labels=labels)
    print kq
    # group B and I results
    sorted_labels = sorted(
        labels,
        key=lambda name: (name[1:], name[0])
    )
    print(metrics.flat_classification_report(
        y_test, y_pred, labels=sorted_labels, digits=3
    ))

def predict(crf,query):
    nlu_dict = {}
    arr_featurized_sent = []
    list_word = query.split(" ")
    tagged = nltk.pos_tag(list_word)
    test_arr = []
    for i in xrange(len(tagged)):
        test_arr.append((tagged[i][0], tagged[i][1]))
    featurized_sent = sent2features(test_arr)
    arr_featurized_sent.append(featurized_sent)
    predict = crf.predict(arr_featurized_sent)

    intent = predict_ex(query,vectorizer,uni_big)
    nlu_dict.update({"intent":intent})
    entities = []
    for i in xrange(len(test_arr)):
        entities.append((test_arr[i][0], predict[0][i]))
    nlu_dict["entities"] = entities
    return nlu_dict



crf = fit("model3.pkl","processing_data/train_test_data/train_nor.txt")
#estimate("model3.pkl","processing_data/train_test_data/test_nor.txt")

def nlu(sent):
    nlu_dict = predict(crf,sent)
    entities = nlu_dict["entities"]
    list_word = [tup[0] for tup in entities]
    list_entity = [tup[1] for tup in entities]
    dict = {}
    for i in xrange(len(list_entity)):
        if list_entity[i] == "O\n":
            continue
        else:
            try:
                x = list_entity[i+1]
                y = list_word[i+1]
            except:
                x = "eos"
                y = "eos"
            if 'B-' in list_entity[i]:
                if 'I-' in x:
                    token_entity = list_word[i] + '_'+ y
                else:
                    token_entity = list_word[i]
                    dict.update({list_entity[i][2:-1]:token_entity})
                    token_entity = ""
            elif 'I-' in list_entity[i]:
                if 'I-' in x:
                    token_entity = token_entity + '_' + y
                else:
                    dict.update({list_entity[i][2:-1]: token_entity})
                    token_entity = ""
    sematics = {"intent":nlu_dict["intent"],"entities":dict}
    return sematics

# while(1):
#     mes = raw_input("Nhap 1 cau: ")
#     mes = mes.strip(" ")
#     sem = nlu(mes)
#     print sem