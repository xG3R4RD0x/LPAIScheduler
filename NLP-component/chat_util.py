# contexts represents the context of the last input of the user
# This is the context Hierarchy, I use this to give a direction to the conversation
# For Example If I start with Subject, then I have to go to Name and then Unit
# after Unit comes Unit Time and I have to check if there are any more subjects
# if there are more subjects then I go back to Name and keep filling the subjects
# if not then I go back to main to fill the rest of the problem Data

hierarchy = [{
    "context": "All", "subcontext": ["Confirmation"]
}, {
    "context": "Main", "subcontext": ["Subject"]
},
    {
        "context": "Subject", "subcontext": ["Name", "All"]
},
    {
        "context": "Unit Time", "subcontext": ["Name", "All"]
},
    {
        "context": "Name", "subcontext": ["Unit", "All"]
},
    {
        "context": "Unit", "subcontext": ["Unit Time", "All"]
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

    return False


def generate_response(missing_fields):
    if missing_fields is True:
        # insert a response that says that everything is correctly filled
        return "everything is fine"
    else:
        # insert a response that analizes what do I have left to full fill
        # and asks the user for that information
        return "can u fill up the information missing please?"
