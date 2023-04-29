# This file contains the trip generation from the original project
import numpy as np
import pandas as pd
import random

# importing Data
df_house = pd.read_csv(r'households.csv', sep=',')
df_trips = pd.read_csv(r'trips.csv', sep=',')
df_persons = pd.read_csv(r'persons(1).csv', sep=',')

#displaying full data frames
pd.set_option("display.max_rows", None)
pd.set_option('display.max_columns', None)

# zones
zones = ("75", "77", "78", "91", "92", "93", "94", "95")

# PERSONS.CSV
# makes columns data into strings
df_persons = df_persons.astype({"household_id": "string"})
df_persons = df_persons.astype({"person_id": "string"})

# removes households outside zones
df_persons = df_persons[df_persons.household_id.str.startswith(zones)]

# remove useless columns
df_persons = df_persons.drop(columns=["has_driving_license", "census_person_id", "has_pt_subscription", "hts_id",
                                      "employed", "sex", "socioprofessional_class"])

# sorts according to person id
df_persons.sort_values("person_id")

# TRIPS.CSV
# removing all irrelevant data (Assumption of home based trips only - work, education, home and no bike/walking trips)

# defines what kind of trips are taken into account
home_based = ("home", "education", "work")
modes = ("car", "car_passenger", "pt")

# changes data types according to what they're needed for
person_ids = tuple(df_persons["person_id"])
df_trips = df_trips.astype({"preceding_purpose": "string"})
df_trips = df_trips.astype({"following_purpose": "string"})
df_trips = df_trips.astype({"mode": "string"})
df_trips = df_trips.astype({"person_id": "string"})

# filters out non home based trips and with different modes of transport
df_trips = df_trips[df_trips.preceding_purpose.str.startswith(home_based)]
df_trips = df_trips[df_trips.following_purpose.str.startswith(home_based)]
df_trips = df_trips[df_trips["mode"].str.startswith(modes)]

# drops trips from education to work and work to education
df_trips = df_trips.drop(df_trips[df_trips["preceding_purpose"] == df_trips["following_purpose"]].index)
df_trips = df_trips.drop(df_trips[(df_trips["following_purpose"] == "education") &
                                  (df_trips["preceding_purpose"] == "work")].index)
df_trips = df_trips.drop(df_trips[(df_trips["preceding_purpose"] == "education") &
                                  (df_trips["following_purpose"] == "work")].index)



# remove useless columns
df_trips = df_trips.drop(columns=["preceding_activity_index", "following_activity_index", "is_first", "is_last",
                                  "departure_time", "arrival_time"])

# filters out trips with person ids not present in persons.csv
df_trips = df_trips[df_trips["person_id"].str.startswith(person_ids)]

# sorts rows by person id
df_trips.sort_values("person_id")

# counter for nr trips
value_counts = df_trips["person_id"].value_counts(ascending=True).to_frame()
df_value_counts = pd.DataFrame(value_counts)
df_value_counts = df_value_counts.reset_index()
df_value_counts.columns = ['person_id', 'nr_trips'] # change column names
df_value_counts = df_value_counts.astype({"person_id": "string"})

# keeps only first trips
df_trips = df_trips.drop(df_trips[df_trips["trip_index"] != 0].index)

# HOUSEHOLD.CSV
# Establishing zones, converting to strings and dropping columns
df_house = df_house.astype({"household_id": "string"})
df_house = df_house.drop(columns=["bike_availability", "census_household_id"])

# eliminating household id's that don't belong to any of the zones,
# assuming that the first 2 digits of the id are the department
df_house = df_house[df_house.household_id.str.startswith(zones)]

# assign household_id column to separate data frame
household_id = df_house["household_id"]

# Creating dataframe
# Data frames to be used
data = [df_persons["household_id"], df_persons["person_id"], df_persons["age"]]
headers = ["household_id", "person_id", "age"]

# Creating new dataframe from above dataframes
df3 = pd.concat(data, axis=1, keys=headers)

# obtaining zone from household id
df3["zone"] = df3["household_id"].str[:2]

# adding trips to our dataframe and dropping not needed columns
df3 = pd.merge(df3, df_trips, on="person_id", how="inner")
df3 = df3.drop(columns=["mode", "trip_index"])

# people that live in Paris or Hauts de Seine, work there
df3.loc[(df3["zone"] == "75") & ((df3["following_purpose"] == "work") |
                                 (df3["preceding_purpose"] == "work")), "workplace"] = "75"
df3.loc[(df3["zone"] == "92") & ((df3["following_purpose"] == "work") |
                                 (df3["preceding_purpose"] == "work")), "workplace"] = "92"

# zones of regions for reference
# main = ['75', '92']
# petite_others = ["77", "93"]
# grande = ["78", "91", "94", "95"]

# change datatype
df3 = df3.astype(({"zone": "string"}))

df3 = pd.merge(df3, df_value_counts, on="person_id", how="inner")
df3 = pd.merge(df3, df_house, on="household_id", how="inner")

df3.reset_index()

# Zone 93
frac_93 = 0.28
work_93 = np.array(["75", "92", "94", "93"])
p_93 = (0.28*0.5, 0.28*0.3, 0.28*0.2, 1-0.28)
for i in range(len(((df3["zone"] == "93") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_93, replace=False, p=p_93)
    if (df3.loc[i, "zone"] == "93") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a

# Zone 94
frac_94 = 0.24
work_94 = np.array(["75", "92", "93", "94"])
p_94 = (0.24*0.5, 0.24*0.3, 0.24*0.2, 1-0.24)
for i in range(len(((df3["zone"] == "94") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_94, replace=False, p=p_94)
    if (df3.loc[i, "zone"] == "94") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a

# Zone 77 - Seine et Marne
frac_77 = 0.34
work_77 = np.array(["75", "92", "94", "93", "91", "95", "77"])
p_77 = (0.06, 0.04, 0.05, 0.05, (0.34-0.2)/2, (0.34-0.2)/2, 1-0.34)
# df3.loc[((df3["zone"] == "77") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))),
#             "workplace"] = np.random.choice(work_77, replace=False, p=p_77)
for i in range(len(((df3["zone"] == "77") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_77, replace=False, p=p_77)
    if (df3.loc[i, "zone"] == "77") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a

# Zone 78
frac_78 = 0.21
work_78 = np.array(["75", "92", "91", "95", "78"])
p_78 = (0.06, 0.04, (0.21-0.1)/2, (0.21-0.1)/2, 1-0.21)
for i in range(len(((df3["zone"] == "78") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_78, replace=False, p=p_78)
    if (df3.loc[i, "zone"] == "78") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a


# Zone 91 -
frac_91 = 0.29
work_91 = np.array(["75", "92", "94", "77", "78", "91"])
p_91 = (0.06, 0.05, 0.04,  (0.29-0.15)/2, (0.29-0.15)/2, 1-0.29)
for i in range(len(((df3["zone"] == "91") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_91, replace=False, p=p_91)
    if (df3.loc[i, "zone"] == "91") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a

# Zone 95 -
frac_95 = 0.26
work_95 = np.array(["75", "92", "93", "78", "77", "95"])
p_95 = (0.06, 0.05, 0.04, (0.26-0.15)/2, (0.26-0.15)/2, 1-0.26)
for i in range(len(((df3["zone"] == "95") & ((df3["following_purpose"] == "work") | (df3["preceding_purpose"] == "work"))))):
    a = np.random.choice(work_95, replace=False, p=p_95)
    if (df3.loc[i, "zone"] == "95") & ((df3.loc[i, "following_purpose"] == "work") | (df3.loc[i, "preceding_purpose"] == "work")):
        df3.loc[i, "workplace"] = a

# inputting location of education/uni for each person
# assumption1 - if they are above 18, university, paris
# assumption2 - below 18, school, home zone
df3.loc[(df3["age"] > 18) & (df3["following_purpose"] == "education"), "workplace"] = "75"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "94") & (df3["following_purpose"] == "education"), "workplace"] = "94"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "77") & (df3["following_purpose"] == "education"), "workplace"] = "77"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "78") & (df3["following_purpose"] == "education"), "workplace"] = "78"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "91") & (df3["following_purpose"] == "education"), "workplace"] = "91"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "92") & (df3["following_purpose"] == "education"), "workplace"] = "92"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "93") & (df3["following_purpose"] == "education"), "workplace"] = "93"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "95") & (df3["following_purpose"] == "education"), "workplace"] = "95"
df3.loc[(df3["age"] <= 18) & (df3["zone"] == "75") & (df3["following_purpose"] == "education"), "workplace"] = "75"


# people in Paris travel an average of 2.5 [km] (refer to French data-sheet) so assumed that people who live in paris
# work in paris
# remove trips inside zones
df3 = df3.drop(df3[(df3["zone"] == df3["workplace"])].index)
#
attraction_75 = df3.loc[(df3['workplace'] == "75"), 'nr_trips'].sum()
attraction_77 = df3.loc[(df3['workplace'] == "77"), 'nr_trips'].sum()
attraction_78 = df3.loc[(df3['workplace'] == "78"), 'nr_trips'].sum()
attraction_91 = df3.loc[(df3['workplace'] == "91"), 'nr_trips'].sum()
attraction_92 = df3.loc[(df3['workplace'] == "92"), 'nr_trips'].sum()
attraction_93 = df3.loc[(df3['workplace'] == "93"), 'nr_trips'].sum()
attraction_94 = df3.loc[(df3['workplace'] == "94"), 'nr_trips'].sum()
attraction_95 = df3.loc[(df3['workplace'] == "95"), 'nr_trips'].sum()

production_75 = df3.loc[(df3['zone'] == "75"), 'nr_trips'].sum()
production_77 = df3.loc[(df3['zone'] == "77"), 'nr_trips'].sum()
production_78 = df3.loc[(df3['zone'] == "78"), 'nr_trips'].sum()
production_91 = df3.loc[(df3['zone'] == "91"), 'nr_trips'].sum()
production_92 = df3.loc[(df3['zone'] == "92"), 'nr_trips'].sum()
production_93 = df3.loc[(df3['zone'] == "93"), 'nr_trips'].sum()
production_94 = df3.loc[(df3['zone'] == "94"), 'nr_trips'].sum()
production_95 = df3.loc[(df3['zone'] == "95"), 'nr_trips'].sum()

#print(attraction_75, attraction_77, attraction_78, attraction_91, attraction_92, attraction_93, attraction_94, attraction_95)
#print(production_75, production_77, production_78, production_91, production_92, production_93, production_94, production_95)