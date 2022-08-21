"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: We do not expect you to come up with a perfect solution. We are more interested
in how you would approach a problem like this.
"""
import json, re
from textwrap import indent

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

# specific courses, begging with COMP / numb
# completion of units of credit
# uoc in courses: specific, level 3 COMP, 
# or, and with groupings

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    

    prereq = CONDITIONS[target_course]
    # parsing
    # removing extra spaces
    prereq = re.sub(r'\s+', ' ', prereq)

    if prereq == "":
        return True
    
    # remove pre req stuff
    prereq = re.sub(r'(?i)pre(-)?(re)?q(uisite)?: ', "", prereq)

    if re.match(r'^[A-Z]{4}\d{4}$', prereq) or re.match(r'^\d{4}$', prereq):
        return prereq.upper() in courses_list

    # identifying brackets, generate groups with priorities
    stack = []

    # remove brackets for uoc required courses
    in_index = prereq.upper().find('IN')
    if prereq[in_index + 3] == '(':
        # uoc in courses mode
        prereq = prereq[:in_index] + re.sub(r'[()]', '', prereq[in_index:])

    
    while prereq.find('(') != -1:
        start = prereq.index('(')
        end = prereq.rindex(')')
        group = prereq[:start] + prereq[end+1:]
        prereq = prereq[start+1:end]
        stack.append(group)

    stack.append(prereq)
    # analysis them in stack order, FILO
    table = [False for i in range(len(stack))]

    uoc_pattern = re.compile(r'\d+ (UOC|UNITS O(F|C) CREDIT)')

    def analysis(str):
        if re.match(r'^[A-Z]{4}\d{4}$', str) or re.match(r'^\d{4}$', str):
            return str in courses_list

        elif uoc_pattern.search(str):
            search_result = uoc_pattern.search(str).group()
            uoc_min_req = int(re.findall(r'\d+', search_result)[0])
            # get uoc requirement / in what courses
            uoc = 0
            if 'IN' in str:
                # get required courses
                uoc_req_courses = str.split('IN ')[1].split(', ')
                if len(uoc_req_courses) == 1:
                    # not a list of courses, but a description for courses
                    
                    # LEVEL OR NOT
                    course_level = None
                    if 'LEVEL' in str:
                        course_level = int(str[str.find('LEVEL') + 6])
                    
                    # get courses prefix
                    course_prefix_pattern = re.compile(r'(?i)[A-Z]{4} courses?')
                    course_prefix = course_prefix_pattern.search(uoc_req_courses[0]).group()[:4]
                    
                    # make regex to search in courses_list
                    regex = re.compile(r'^' + course_prefix + (r'\d' if course_level == None else f"{course_level}") + r'\d{3}$')
                    for course in courses_list:
                        if regex.match(course):
                            uoc += 6 
                else:
                    for course in uoc_req_courses:
                        if course == "" or course == " ":
                            continue

                        if course in courses_list:
                            uoc += 6
            else:
                # calculate uoc from courses_list
                uoc = len(courses_list) * 6
            
            return uoc >= uoc_min_req
        

    def eval(str, prev_result):
        str = str.upper()
        if ('OR' in str):
            nodes = str.split(' OR ')
            for node in nodes:
                if node == "" or node == " ":
                    continue
                if analysis(node):
                    return True
            return False or prev_result
        elif ('AND' in str):
            nodes = str.split(' AND ')
            for node in nodes:
                # skip empty nodes
                if node == "" or node == " ":
                    continue
                if not analysis(node):
                    return False
            return True and prev_result
        else:
            return analysis(str)

    for i in range(len(stack)-1, -1, -1):
        table[i] = eval(stack[i], True if i >= len(table) -1 else table[i+1])
    return table[0]