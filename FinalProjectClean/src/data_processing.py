import pandas as pd 
import base64
import matplotlib.pyplot as plt
from collections import Counter 
from wordcloud import WordCloud
from io import BytesIO
from dash import html

df_mission_failure = pd.read_csv("assets/Space_Corrected.csv", encoding="ISO-8859-1")
#Load and preprocess data 
# Function to categorize majors based on keywords

def categorize_major(major):
    """
    Categorize the major based on specified keywords.

    Parameters:
    major (str): The major to categorize.
    keywords (list): List of keywords to determine the category.

    Returns:
    str: Category of the major.
    """

    keywords = [
        "Engineering",
        "Science",
        "Physics",
        "Mathematics",
        "Chemistry",
        "Biology",
        "Astronomy",
        "Aeronautics",
    ]

    major = str(major)  # Ensure the major is a string
    for keyword in keywords:
        if keyword in major:
            return "Typical"
    return "Wacky/Unusual"

def load_and_preprocess_data_astronauts(file_path):
    """
    Load and preprocess astronaut data.

    Parameters:
    file_path (str): Path to the CSV file.
    keywords (list): List of keywords for categorizing majors.

    Returns:
    DataFrame: Preprocessed astronaut data.
    """
    keywords = [
        "Engineering",
        "Science",
        "Physics",
        "Mathematics",
        "Chemistry",
        "Biology",
        "Astronomy",
        "Aeronautics",
    ]

    try:
        # Dataframe
        df_astronauts = pd.read_csv(file_path)
        
        # * Data pre-processing - astronauts.csv
        df_astronauts = df_astronauts[df_astronauts["Year"].notna()]
        df_astronauts["Year"] = df_astronauts["Year"].astype(int)
        # Create 5-year bins
        df_astronauts["Year Interval"] = pd.cut(
            df_astronauts["Year"], bins=range(df_astronauts["Year"].min(), df_astronauts["Year"].max() + 5, 5), right=False
        )
        df_astronauts["Year Interval"] = df_astronauts["Year Interval"].astype(str)

        # Extract state from 'Birth Place'
        df_astronauts["State"] = df_astronauts["Birth Place"].str.split(",").str[-1].str.strip()

        # Apply this function to the 'Undergraduate Major' column
        df_astronauts["Major Category"] = df_astronauts["Undergraduate Major"].apply(lambda x: categorize_major(x))
        # Count the number of astronauts in each categorized major
        major_counts = (
            df_astronauts.groupby(["Major Category", "Undergraduate Major"])
            .size()
            .reset_index(name="Number of Astronauts")
        )

        # Count the number of astronauts per state
        state_counts = df_astronauts["State"].value_counts().reset_index()
        state_counts.columns = ["State", "Astronaut Count"]

        return df_astronauts, major_counts, state_counts
    except FileNotFoundError: 
        print(f"File not found: {file_path}")
        return None

def generate_wordcloud(df):
    """
    Generate a word cloud image from the 'Missions' column of the dataframe.

    Parameters:
    df (DataFrame): Dataframe containing the 'Missions' column.

    Returns:
    html.Img: HTML image component of the word cloud.
    """
    # Split the 'Missions' column into individual missions and count them
    mission_list = df["Missions"].dropna().str.split(", ").sum()
    mission_counts = Counter(mission_list)

    # Generate the word cloud from frequencies
    wordcloud = WordCloud(
        width=800, height=400, background_color="white"
    ).generate_from_frequencies(mission_counts)

    # Convert the word cloud image to a string of base64 to display in Dash
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight", pad_inches=0)
    img.seek(0)
    wordcloud_string = base64.b64encode(img.getvalue()).decode()

    wordcloud_image = html.Img(
        src="data:image/png;base64,{}".format(wordcloud_string),
        style={"width": "100%", "height": "auto"},
    )

    return wordcloud_image

def load_and_preprocess_data_missions(file_path):
    """
    Load and preprocess space missions data.

    Parameters:
    file_path (str): Path to the CSV file.

    Returns:
    DataFrame: Preprocessed space missions data.
    """
    try:
        df_space_missions = pd.read_csv(file_path, encoding="ISO-8859-1")

        # * Data pre-processing for the space missions:
        # Convert 'Date' to datetime and extract the year
        df_space_missions["Date"] = pd.to_datetime(df_space_missions["Date"])
        df_space_missions["Year"] = df_space_missions["Date"].dt.year
        # Group by year and count the number of missions
        missions_per_year = (
            df_space_missions.groupby("Year").size().reset_index(name="Number of Missions")
        )
        # Extract country name from 'Location'
        df_space_missions["Country"] = (
            df_space_missions["Location"].str.split(",").str[-1].str.strip()
        )
        # Count the number of missions per country
        missions_per_country = df_space_missions["Country"].value_counts().reset_index()
        missions_per_country.columns = ["Country", "Number of Missions"]

        # Group by company and mission status
        grouped_df = (
            df_space_missions.groupby(["Company", "MissionStatus"])
            .size()
            .reset_index(name="Count")
        )
        # Calculate the total missions for each company
        total_missions_per_company = (
            grouped_df.groupby("Company")["Count"].sum().reset_index(name="TotalMissions")
        )
        # Merge to get total missions alongside status counts
        grouped_df = pd.merge(grouped_df, total_missions_per_company, on="Company")
        # Calculate total missions
        total_missions = grouped_df["Count"].sum()
        # Calculate the percentage for each company
        grouped_df["Percentage"] = grouped_df["Count"] / total_missions * 100
        
        return df_space_missions, missions_per_country, grouped_df
    except FileNotFoundError: 
        print(f"File not found: {file_path}")
        return None
    
#df_astronauts = load_and_preprocess_data_astronauts("assets/astronauts.csv")
#df_space_missions, missions_per_country, grouped_df = load_and_preprocess_data_missions("assets/space_missions.csv")

def load_mission_success(file_path):
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    df.drop(['Unnamed: 0.1','Unnamed: 0'], axis = 1, inplace = True)
    return df

def process_mission_success(df):

    #function to extract the name of the country from the location
    def extract_country_name(location):
        country = location.split(',')[-1]
        country = country.strip()
        return country
    
    #function to get the Launch Vehicle Name from the Details
    def getVehicles(detail):
        lv = []
        li = [x.strip() for x in detail.split('|')] #extracting the name of all launch vehicles from the Details section
        for ele in li:
            if('Cosmos' in ele):
                lv.append('Cosmos')
            elif('Vostok' in ele):
                lv.append('Vostok')
            elif('Tsyklon' in ele):
                lv.append('Tsyklon')
            elif('Ariane' in ele):
                lv.append('Ariane')
            elif('Atlas' in ele):
                lv.append('Atlas')
            elif('Soyuz' in ele):
                lv.append('Soyuz')
            elif('Delta' in ele):
                lv.append('Delta')
            elif('Titan' in ele):
                lv.append('Titan')
            elif('Molniya' in ele):
                lv.append('Molniya')
            elif('Zenit' in ele):
                lv.append('Zenit')
            elif('Falcon' in ele):
                lv.append('Falcon')
            elif('Long March' in ele):
                lv.append('Long March')
            elif('PSLV' in ele):
                lv.append('PSLV')
            elif('GSLV' in ele):
                lv.append('GSLV')
            elif('Thor' in ele):
                lv.append('Thor')
            else:
                lv.append('Other')
        return lv
    
    #dictionary to help in mapping to get consistent and correct Country Names
    countries_dict = {
        'Russia' : 'Russian Federation',
        'New Mexico' : 'USA',
        "Yellow Sea": 'China',
        "Shahrud Missile Test Site": "Iran",
        "Pacific Missile Range Facility": 'USA',
        "Barents Sea": 'Russian Federation',
        "Gran Canaria": 'USA'
    }

    df['Country'] = df['Location'].apply(lambda x: extract_country_name(x))
    df['Country'] = df['Country'].replace(countries_dict)

    #extracting date-time features
    df['Datum'] = pd.to_datetime(df['Datum'], format="%a %b %d, %Y %H:%M UTC", errors='coerce')
    df['year'] = df['Datum'].apply(lambda datetime: datetime.year)
    df['month'] = df['Datum'].apply(lambda datetime: datetime.month)
    df['weekday'] = df['Datum'].apply(lambda datetime: datetime.weekday())
    df['Launch Vehicles'] = df['Detail'].apply(lambda x:getVehicles(x))

    return df