'''
This is the program that I made to recursivly access the api to "download"
all of the tossups that quizDb has into seperate json files. The reason I had
to do this was because the api doesn't allow you to simply ask for all 90,000
quesions (well it does, but then it unintentionally ddoses itself -- as stated
on the website -- and then the whole website is pretty much unresponsive.
'''

# Import the things we need
import requests, lxml.html, json

# Create a session instance of a request
s = requests.session()

# Before getting the jsons, we need to authenticate that we are an "admin"
# that is using the api, to do this, we have to post our credentials on the
# login page first
# Get the login page
login = s.get('https://www.quizdb.org/admin/login')

# Get the things that we need to post that we do not fill out
login_html = lxml.html.fromstring(login.text)
hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

# Fill out the parts of the form that we need to fill out
form['admin_user[password]']='ZedZedZed123'
form['admin_user[email]']='gowdaanuragr@gmail.com'

# Post the form
s.post('https://www.quizdb.org/admin/login', data=form)

'''
jsons = []
currentEvents = []
fineArts = []
geography = []
history = []
literature = []
mythology = []
philosophy = []
religion = []
science = []
socialScience = []
trash = []
'''

# Define a bunch of lists to hold the questions
jsons, currentEvents, fineArts, geography, history, \
       literature, mythology, philosophy, religion, science, \
       socialScience, trash = [[] for i in range(12)]

# Set up a dict so that we dont have to have multiple contitions later
# This dict takes in they key of the category and outputs the list that
# the category would fall under as a string
conv = {26:'currentEvents', 21:'fineArts', 20:'geography', 18:'history', \
        15:'literature', 14:'mythology', 25:'philosophy', 19:'religion', \
        17:'science', 22:'socialScience', 16:'trash'}

# There were 972 packets at the time I wrote this program
for count in range(972):
    # Go to the tossup pages which give the json objects
    data = s.get('https://www.quizdb.org/admin/tossups.json?page='+str(count+1)\
                 +'&per_page=100').text
    # Append all these json objects in our "master" json list
    jsons.append(json.loads(data))

# Now we sort the jsons and put them in individual lists so that we can
# later make files with them
for data in jsons:
    # This will enumerate trhough each question
    for question in data:
        # Here we are storing the jsons in the particular lists
        # However, I only want to keep the question and answer,
        # as everything else isn't that helpful (and we also have
        # a lot of data, so we want to get rid of as much as is
        # possible)
        # Also I had to check to see that the text was not equal to
        # [missing], becuase for some reason there were about 50
        # questions that just had [missing] as the question and
        # answer, and null as the category id       
        if question['text'] != '[missing]':
            eval(conv[question['category_id']]).append(\
            {'question':question['text'], 'answer':question['answer']})

# Now we have to create the individual json files using our lists
for i in conv:
    # Create a json file using the name of the list
    with open(conv[i]+'.json', 'w', encoding='utf-8') as f:
        # Dump the contents of the json object into the file
        json.dump(eval(conv[i]), f, ensure_ascii=False, indent=4)

