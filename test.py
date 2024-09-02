import streamlit as st

# Title of the app
st.title("Simple Streamlit App")

# Text input for user's name
name = st.text_input("Enter your name:")

# Number input for user's favorite number
favorite_number = st.number_input("Select your favorite number:", min_value=1, max_value=100)

# Button to submit the inputs
if st.button("Submit"):
    st.write(f"Hello, {name}!")
    st.write(f"Your favorite number is {favorite_number}.")

# A simple plot
import numpy as np
import matplotlib.pyplot as plt

# Generate random data
data = np.random.randn(100)

# Create a histogram
fig, ax = plt.subplots()
ax.hist(data, bins=20)

# Display the plot
st.pyplot(fig)
