from typing import List
import json
import docx2python
import docxlatex


def convert(path: str) -> List:
    document = docx2python.docx2python(path)

    texts: str = document.text

    questions = texts.split('^^')
    del questions[0]

    new_questions: List = [question.replace(
        '\n', '') for question in questions]
    new_questions: List = [question.replace(
        '<latex>', '\[') for question in new_questions]

    # my_str = my_str.replace('\\', raw)
    new_questions: List = [question.replace(
        '</latex>', '\]') for question in new_questions]
    # print(new_questions)

    return new_questions


path = r'C:\Users\abdllahi\Desktop\computer.docx'

# print(convert(path))


def remove_slashes(_str):
    string = ''
    raw = '\ '
    raw.strip()
    string = _str.replace(r'\\', raw)

    return string


def convert_to_format(path):
    quests = convert(path)

    final_bank = [question.split('@@') for question in quests]

    q = []

    for question in final_bank:
        a = []
        b = []
        z = 0
        for comp in question:
            if z == 0:
                a.append(comp.strip())
            else:
                # print(comp)
                if comp.strip().startswith('~'):
                    b.append(comp.strip()[1:])
                else:
                    b.append(comp.strip())

            if comp.strip().startswith('~'):
                a.append(comp.strip()[1:])
            z += 1
        a.insert(1, b)
        q.append(a)

    print(len(q))
    q = {"banks": q}
    print(q)
    return q


def save_to_json(question_list):
    with open('mathematics_jss_3.json', 'w') as f_obj:
        json.dump(question_list, f_obj)


path = r'C:\Users\abdllahi\Desktop\Mathematics Testing question.docx'

# save_to_json(question_list=convert_to_format(path))
# print(convert_to_format(path=path))