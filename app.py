import streamlit as st
import pandas as pd
import csv


def getListNames():
    nameList = ['Enter name']
    # combined file with all the peopleIDs
    with open("AllPeopleID.csv",
              "r") as file_in:
        reader = csv.reader(file_in)
        next(reader)  # skip header
        for row in file_in:
            row = row.split(',')
            if row[1] not in nameList:
                nameList.append(row[1])
    return nameList

def getPeopleID(legislatorName):
    # combined file with all the peopleIDs
    with open("AllPeopleID.csv",
              "r") as file_in:
        reader = csv.reader(file_in)
        next(reader)  # skip header
        for row in file_in:
            row = row.split(',')
            if row[1] == legislatorName:
                return row[0]

def getSessions(peopleID):
    activeSessionList = []
    sessionList = ['2009-2010', '2011-2012', '2013-2014', '2015-2016','2017-2018','2019-2020','2021-2022','2023-2024','2025-2026']
    for session in sessionList:
        with open(f"{session}/people.csv",
                  "r") as file_in:
            for row in file_in:
                row = row.split(',')
                # print(row[0])
                if row[0] == peopleID:
                    activeSessionList.append(session)
    return activeSessionList

def getVotes(peopleID, activeSessions):
    roll_call_dict = {}
    for session in activeSessions:
        with open(f"{session}/votes.csv",
                  "r") as file_in:
            for row in file_in:
                row = row.split(',')
                if row[1] == peopleID:
                    roll_call_dict[row[0]] = [row[3], f"{session} Session"]
        # print("roll_call_dict", roll_call_dict)
    # get bill id from rollcalls.csv
        for bill in roll_call_dict.keys():
            with open(
                    f"{session}/rollcalls.csv",
                    "r") as file_in:
                for row in file_in:
                    row = row.split(',')
                    if row[1] == bill:
                        roll_call_dict[bill].append(row[0])
    # get bill information from bills.csv
        for bill in roll_call_dict.keys():
            with open(f"{session}/bills.csv", "r", newline='') as file_in:
                reader = csv.reader(file_in)
                for row in reader:
                    if row[0] == roll_call_dict[bill][2]:
                        roll_call_dict[bill].append(row[2])
                        roll_call_dict[bill].append(row[5])
                        roll_call_dict[bill].append(row[6])

    return(roll_call_dict)



names = getListNames()

# Selectbox with autocomplete/typeahead
selected_name = st.selectbox(
    "Type a name to search and select:",
    names
)

st.write(f"You selected: {selected_name}")

votes_button = st.button(f"Get {selected_name}'s voting record")

if votes_button:
    with st.spinner("Pulling voting records..."):
        # find people_id
        people_id = getPeopleID(selected_name)
        activeSessions = getSessions(people_id)
        votingRecord = getVotes(people_id, activeSessions)
        data = []
        for roll_call_id, values in votingRecord.items():
            row = {
            'Session': values[1],
            'Date': values[4],
            'Bill Number': values[3],
            'Vote': values[0].strip(),  # remove \n
            'Bill Description': values[5],
            'Bill ID': values[2],
            'Roll Call ID': roll_call_id
            }
            data.append(row)
        df = pd.DataFrame(data)
        st.write(df)
                      
    
    

