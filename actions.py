from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction

import random

class CheckForm(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "check_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["yn"]
    		
    def slot_mappings(self):
        return {"yn": [self.from_intent(intent="trial_a1", value=True),
                       self.from_intent(intent="dont_know", value=False),
                       self.from_intent(not_intent=["trial_a1", "dont_know"],value='other')]}
    	
    def validate_yn(self, value, dispatcher, tracker, domain):
   		if value == 'other':
   			dispatcher.utter_message("Sorry..:( You 're wrong.")
   			return {"yn": False}
   		else:
   			return {"yn": value}
    	
    def submit(self, dispatcher, tracker, domain):
        yn = tracker.get_slot("yn")
        if yn:
            dispatcher.utter_message(template="utter_trial_correct")
            return[]
        else:
            dispatcher.utter_message(template="utter_trial_wrong")
            return []


SYS = [("What man can not live in a house?", "snowman"),
         ("What never asks questions but gets a lot of answers?", "dictionary"),
         ("What letter makes her hear?", "a"),
         ("What clothing is always sad?", "blue-jeans"),
         ("Mike is a butcher. He is 5’10” tall. What does he weigh?", "meat"),
         ("Jimmy’s mother had four children. She named the first Monday. She named the second Tuesday, and she named the third Wednesday. What is the name of the fourth child?", "jimmy"),
         ("Before Mt. Everest was discovered, what was the highest mountain in the world?", "Everest"),
         ("Which is heavier? A pound of feathers or a pound of rocks?", "Neither"),
         ("What is full of holes but can still hold water?", "sponge"),
         ("Give me food, and I will live; give me water, and I will die. What am I?", "fire"),
         ("Which travels faster? Hot or Cold?", "hot"),
         ("I left my campsite and hiked south for 3 miles. Then I turned east and hiked for 3 miles. I then turned north and hiked for 3 miles, at which time I came upon a bear inside my tent eating my food! What color was the bear?", "white"),
         ("When young, I am sweet in the sun.When middle-aged, I make you gay.When old, I am valued more than ever.", "wine"),
         ("As I was going to St. Ives,I met a man with seven wives.Each wife had seven sacks,Each sack had seven cats,Each cat had seven kits.Kits, cats, sacks and wives,How many were going to St. Ives?", "one"),
         ("What has a mouth, but cannot eat; moves, but has no legs; and has a bank, but cannot put money in it?", "river"),
         ("What 5-letter word becomes shorter when you add two letters to it?", "short"),
         ("Find a number less than 100 that is increased by one-fifth of its value when its digits are reversed.", "45"),
         ("What letter comes next in the following sequence? D R M F S L T_", "d"),
         ("Without it, I am dead. If I am not, then I am behind. What am I?", "ahead")]

class ActionQuestionSetup(Action):

    def name(self) -> Text:
        return "action_question_setup"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if len(SYS) == 0:
            dispatcher.utter_message(text="The system need to be updates and added more questions. Please be patient and wait:)")
            return[]
        else:
            jix = random.choice(range(len(SYS)))
            dispatcher.utter_message(text=SYS[jix][0])
            return [SlotSet("jix", jix)]


class ActionQuestionPunchline(Action):

    def name(self) -> Text:
        return "action_question_punchline"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if tracker.get_slot("time") is None:
            time = tracker.get_slot("time")
            correct = tracker.get_slot("correct")
            time = 0
            correct = 0
        else:
            time = int(tracker.get_slot("time"))
            correct = int(tracker.get_slot("correct"))
        
        if len(SYS) == 0:
            dispatcher.utter_message(text="The system need to be updates and added more questions. Please be patient and wait:)")
        else:
            jix = int(tracker.get_slot("jix"))
            answer = str(SYS[jix][1])
            text = tracker.latest_message.get('text')
        
        if text == answer:
            dispatcher.utter_message(text="Correct!")
            SYS.pop(jix)
            time += 1
            correct +=1
        else:
            time +=1
            dispatcher.utter_message(text="Wrong!")

        if correct==2 and time<=3:
            time = 0
            correct = 0
            dispatcher.utter_message(text="Since you have correct two in three. I decided to release you.")
        elif time==3:
            time = 0
            correct = 0
            dispatcher.utter_message(text="The next day.")
        
        tracker.slots["time"] = time
        tracker.slots["correct"] = correct
        return [SlotSet("time",time),
                SlotSet("correct",correct)]
