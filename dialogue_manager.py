from ner_model import nlu

def get_sematics(sent):
    sematics = nlu(sent)
    intent = sematics["intent"]
    if intent == "ATP":
        frame = weather_frame()
    elif intent == "WEATHER":
        frame = weather_frame()
    elif intent == "BR":
        pass
    elif intent == "PM":
        pass
    elif intent == "RB":
        pass
    elif intent == "SCW":
        pass
    elif intent == "SSE":
        pass
    else:
        pass
    return frame

class weather_frame:
    def __init__(self):
        self.time = "current"
        self.loc = ""

    def receive(seft,sent):
        sematics = nlu(sent)
        if "timeRange" in sematics["entities"]:
            seft.time = sematics["entities"]["timeRange"]
        if "city" in sematics["entities"]:
            seft.loc = sematics["entities"]["city"]
        else:
            count = 0
            while(True):
                print("Missing loc...")
                loc =raw_input("Where do you want to ask weather ?")
                loc = nlu(loc)
                if "city" in loc["entities"]:
                    seft.loc = loc["entities"]["city"]
                    break
                count +=1
                if count == 3:
                    print("I don't understand!!\n")
                    break

        print("Receive complety information!!")

    def get_weather(self):
        if self.loc == "Hanoi":
            return "sunny"
        else:
            return "rainy"

    def generate(self):
        loc = self.loc
        time = self.time
        response = "The weather in "+loc + " " + time + " is "+ self.get_weather()
        print response
        self.__init__()
        return response

print("Hello. What can i help you ?")
while(1):
    input_sen = raw_input("\n")
    new_frame = get_sematics(input_sen)
    new_frame.receive(input_sen)
    new_frame.generate()
    print("Finish session!!!")
