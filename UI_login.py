import ipywidgets as widgets 
from IPython.display import display, clear_output


user_database = {}

# Widgets 
# Title & Header
title = widgets.HTML("<h2>Ski Club Registration & Login</h2>")

# Login Widgets
username_input = widgets.Text(description="Username:", placeholder="Enter username")
password_input = widgets.Password(description="Password:", placeholder="Enter password")
login_btn = widgets.Button(description="Log In / Register", button_style="primary")

# Info Collection Widgets
name_input = widgets.Text(description="Full Name:", placeholder="Your Name")
age_input = widgets.IntSlider(value=25, min=1, max=100, step=1, description="Age:")
ability_input = widgets.Dropdown(
    options=["Beginner", "Intermediate", "Advanced", "Expert"],
    value="Beginner",
    description="Skiing Ability:",
)
save_btn = widgets.Button(description="Save Profile", button_style="success")

output = widgets.Output()

# Containers
login_container = widgets.VBox([username_input, password_input, login_btn])
info_container = widgets.VBox([name_input, age_input, ability_input, save_btn])

# Main UI flow
def on_login_clicked(b):
    with output:
        clear_output()
        username = username_input.value.strip()
        password = password_input.value.strip()
        
        if not username or not password:
            print("❌ Please enter both a username and password.")
            return
        
        # Simple registration/login simulation
        if username not in user_database:
            user_database[username] = {"password": password, "profile": None}
            print(f"🔑 New user '{username}' registered! Please fill out your profile below.")
        else:
            if user_database[username]["password"] != password:
                print("❌ Incorrect password for this username. Please try again.")
                return
            else:
                print(f"🔓 Logged in successfully as '{username}'!")
                profile = user_database[username]["profile"]
                if profile:
                    name_input.value = profile["name"]
                    age_input.value = profile["age"]
                    ability_input.value = profile["ability"]
                    print("✨ Loaded existing profile info.")
        
        # Show the profile form
        display(info_container)

def on_save_clicked(b):
    with output:
        clear_output()
        username = username_input.value.strip()
        name = name_input.value.strip()
        age = age_input.value
        ability = ability_input.value
        
        if not name:
            print("❌ Please enter your name.")
            display(info_container)
            return
            
        user_database[username]["profile"] = {
            "name": name,
            "age": age,
            "ability": ability
        }
        print("🎉 Profile saved successfully!")
        print(f"Summary for {username}:")
        print(f"- Name: {name}")
        print(f"- Age: {age}")
        print(f"- Skiing Ability: {ability}")

# Attach actions
login_btn.on_click(on_login_clicked)
save_btn.on_click(on_save_clicked)

# Display Initial UI
display(title, login_container, output)