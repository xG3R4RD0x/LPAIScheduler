# contexts represents the context of the last input of the user
# This is the context Hierarchy, I use this to give a direction to the conversation
# For Example If I start with Subject, then I have to go to Name and then Unit
# after Unit comes Unit Time and I have to check if there are any more subjects
# if there are more subjects then I go back to Name and keep filling the subjects
# if not then I go back to main to fill the rest of the problem Data

hierarchy = [{"context": "Main",
              "subcontext": ["Subject"]},
             {
    "context": "Subject", "subcontext": ["Name"]
},
    {
    "context": "Unit Time", "subcontext": ["Name"]
},
    {
    "context": "Name", "subcontext": ["Unit"]
},
    {
    "context": "Unit", "subcontext": ["Unit Time"]
}
]

# check if the input is inside the context rules


def check_context(current_context, new_context):
    for c in hierarchy:
        if current_context == c["context"]:
            if new_context in c["subcontext"]:
                return True
            else:
                return False
        else:
            return False
