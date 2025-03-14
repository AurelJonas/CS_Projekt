# let's import streamlit first
import streamlit as st

# This function is an adapted and extended version of the roll the dice
# implementation from week 2.
def roll_the_dice(rolls, sides=9, print_results=False):
    import random
    
    # face frequency counters
    # this time as a dictionary
    frequencies = {}

    # here we roll number of rolls times
    for roll in range(rolls):
        face = random.randrange(1, sides+1)
        
        # increment appropriate face counterK
        # this time as a dictionary
        #
        # fist we check, whether the the resulting face 
        # is in our dictonary already, then increase its
        # frequency by one 
        if face in frequencies:
            frequencies[face] += 1
        # otherwise insert this face and set it to one
        else:
            frequencies[face] = 1
    
    # we may print the results to the console
    # this, however, is not (very) useful in streamlit            
    if print_results:
        sides_len = len(str(sides))
        value_len = len(str(max(frequencies.values())))
        for key, value in sorted(frequencies.items()):
            print(f'{key:>{sides_len}}: {value:>{value_len}}')
    Hilfe
    # finally we return the dictionary sorted by keys
    return dict(sorted(frequencies.items()))

# and now we only need a litte bit of Python code to 
# bring it to the web 
#
# we run the code from the command line by entering
#   streamlit run <path_to_file>/streamlit_demo.py  
#

# Some title, headings, and text
st.title("Here is our first Web Application")
st.header("Let's roll the dice :sunglasses: ", divider='rainbow')
st.write("Look how easily we can build and tun a web application")

# a button to get started
# and show the results 
if st.button('Roll the dice!!'):
    st.header('Results')
    results = roll_the_dice(6000)
    st.write(results)