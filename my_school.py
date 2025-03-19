########################### SCHOOL INFORMATIONS #################################
class School():
    def __init__(self) -> None:
        self.name = "KHULAFA'U INTERNATIONAL SCHOOL"
        self.sections = "Nursery, Primary and Secondary School"
        self.sections_list = ["Nursey", "Primary", "Secondary"]
        self.address = "No. 53 Jae Road, Shika-Zaria"
        self.contact_number = ["08037327006", "08145174744"]
        self.motto = "KNOWLEDGE AND MORALITY"
        self.email = "khulafa'u@gmail.com"
        self._session = "2023/2024"
        self.terms = ["first_term", "second_term", "third_term"]
        self.current_term = self.terms[2]
        self.term = self.terms[2]
        self.logo = "AlhikmaLogo.jpg"
        self.term_begin = "16/09/2024"
        self.term_ended = "31/07/2024"
        self.tests = ["first_ca", "second_ca", "exam", "ppt"]
        self.current_test = self.tests[0]
        self.junior_subjects = ["English_Language", "Mathematics", "Civic_Education", "Agric_Science", "Social_Studies",
                                "Business_Studies", "Basic_Studies", "Computer", "IRK", "Arabic_Language", "Hausa_Language"]
        
        self.primary_subjects = ["Mathematics", "English_Language", "Basic_Science", "Social_Studies", "Hausa_Language",
                                    "IRK", "Jolly_Phonics_Writing", "Computer"]
        
        self.overall_subjects = list(set(self.junior_subjects + self.primary_subjects))

        self.classes = ["primary_4", "primary_5", "jss_1", "jss_2", "jss_3"]


# ["Mathematics", "English_Language", "Basic_Science", "Social_Studies", "Hausa_Language",
#                                     "IRK", "Jolly_Phonics_Writing", "Computer"]

# ["English", "Mathematics", "Civic_Education", "Agric_Science", "Social_Studies",
#                      "Business_Studies", "Basic_Studies", "Computer", "IRK", "Arabic_Language", "Hausa_Language"]

# my_schooll = School()
# print(my_schooll.overall_subjects)

# quests = [
#     ["A business letter contains all the following except", ["story", "date", "salutation", "all of the options"], "story"],
#     ["The first paragraph states the reason for writing the letter, means", ["true", "false", "optional", "i don't know"], "true"],
#     ["Your signature is necessary required in business letter", ["true", "false", "optional", "both"], "true"],
#     ["Refrences line is necessary required in business letter", ["true", "its optional", "none of the option", "i don't know"], "its optional"],
#     ["Salutation means the opening greetings, example", ["good morning", "well done", "dear sir", "how are you"], "dear sir"],
#     ["The second paragraph gives the facts of the _________ inquiry ", ["reciever's", "sender's", "title", "salutation"], "sender's"],
#     ["There could be more than one paragraph", ["true", "false", "optional", "both"], "true"],
#     ["The last paragraph is the ___________", ["salutation", "conclusion", "closing", "meeting"], "closing"],
#     ["Traditional closing statement includes ", ["see you soon", "see you later", "yours faithfully", "lovely friend"], "yours faithfully"],
#     ["The writer's name/title should be typed or printed under this closing, with enough between for the writer to _________ the letter", ["sign", "look", "colour", "match"], "sign"],
#     ["If a business organization is running with the aid of computers, it is said to be __________ ", ["monitored", "computerized", "technology", "sociology"], "computerized"],
#     ["A computerized network system is used by ___________", ["bank", "cooking", "playing", "eationg"], "bank"],
#     ["Computer makes business operation ________", ["harder", "faster", "destroyed", "all are correct"], "faster"],
#     ["Computer ensures the keeping of accurate results", ["true", "false", "optional", "both"], "true"],
#     ["International business transactions have became easier and faster", ["true", "false", "optional", "none of the options"], "true"],
#     ["Computer makes communication easier and faster", ["true", "false", "optional", "none of the options"], "true"],
#     ["One of the following is among the problems of computerization", ["it makes business easier and faster", "it makes communication easier and faster", "the use of computer has reduced the number of workers in many business", "all are correct"], "the use of computer has reduced the number of workers in many business"],
#     ["The full meaning of GSM is", ["Global Satellite for Mobile", "Global System for Movie", "Global System for Mobile", "Global Satellite for Mobiles"], "Global System for Mobile"],
#     ["The SIM card comes with an _____________ digit coded phone number", ["twelve", "eleven", "nine", "ten"], "eleven"],
#     ["To make a call, the phone has to be ___________", ["not recharged", "recharged", "boost", "saturated"], "recharged"]
# ]

# for quest in quests:
#     print(quest[-1])
    # print(len(quests))
