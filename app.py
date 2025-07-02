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
                reader = csv.DictReader(file_in)
                for row in reader:
                    if row["roll_call_id"] == bill:
                        roll_call_dict[bill].extend([row["bill_id"], row['yea'], row['nay'], row['nv'], row['absent'], row['total'], row['chamber']])
    # get bill information from bills.csv
        for bill in roll_call_dict.keys():
            with open(f"{session}/bills.csv", "r", newline='') as file_in:
                reader = csv.DictReader(file_in)
                for row in reader:
                    if row["bill_id"] == roll_call_dict[bill][2]:
                        roll_call_dict[bill].append(row["bill_number"])
                        roll_call_dict[bill].append(row["status_date"])
                        roll_call_dict[bill].append(row["title"])
    # add whether in a tie-breaker
        for bill in roll_call_dict.keys():
            if roll_call_dict[bill][8] == "House":
                if int(roll_call_dict[bill][3]) == 56 and roll_call_dict[bill][0] == "Yea\n":
                    roll_call_dict[bill].append("TIE BREAKER")
                elif int(roll_call_dict[bill][3]) == 56 and roll_call_dict[bill][0] != "Yea\n":
                    roll_call_dict[bill].append("NOT TIE BREAKER")
                elif int(roll_call_dict[bill][3]) == 55 and roll_call_dict[bill][0] != "Yea\n":
                    roll_call_dict[bill].append("TIE BREAKER")
            elif roll_call_dict[bill][8] == "Senate":
                if int(roll_call_dict[bill][3]) == 19 and roll_call_dict[bill][0] == "Yea\n":
                    roll_call_dict[bill].append("TIE BREAKER")
                elif int(roll_call_dict[bill][3]) == 19 and roll_call_dict[bill][0] != "Yea\n":
                    roll_call_dict[bill].append("NOT TIE BREAKER")
                elif int(roll_call_dict[bill][3]) == 18 and roll_call_dict[bill][0] != "Yea\n":
                    roll_call_dict[bill].append("TIE BREAKER")
    # add whether extreme minority
        for bill in roll_call_dict.keys():
            threshold_20 = (int(roll_call_dict[bill][3]) + int(roll_call_dict[bill][4]) + int(roll_call_dict[bill][5]) + int(roll_call_dict[bill][6])) * 0.2
            # give vote number
            if roll_call_dict[bill][0] == "Yea\n":
                vote_number = 3
            elif roll_call_dict[bill][0] == "Nay\n":
                vote_number = 4
            elif roll_call_dict[bill][0] == "NV\n":
                vote_number = 5
            elif roll_call_dict[bill][0] == "Absent\n":
                vote_number = 6
            # see if threshold
            if int(roll_call_dict[bill][vote_number]) <= threshold_20:
                roll_call_dict[bill].append("MINORITY")
            else:
                roll_call_dict[bill].append("NOT MINORITY")
            st.write(roll_call_dict[bill])
    print(roll_call_dict)
    return(roll_call_dict)


def getSponsorships(peopleID, activeSessions):
    # get list of all sponsored bill id
    sponsored_bill_ids = []
    for session in activeSessions:
        with open(f"{session}/sponsors.csv", "r", newline='') as file_in:
            reader = csv.DictReader(file_in)
            for row in reader:
                if row["people_id"] == peopleID:
                    sponsored_bill_ids.append(row["bill_id"])
    sponsored_bill_ids_dict = {}
    # Using bill_id, get bill info from bills.csv
    for session in activeSessions:
        with open(f"{session}/bills.csv", "r", newline='') as file_in:
            reader = csv.DictReader(file_in)
            for row in reader:
                if row["bill_id"] in sponsored_bill_ids:
                    sponsored_bill_ids_dict[row["bill_id"]] = [row["bill_number"], row["status_date"], row["status_desc"], row["title"], row["description"], row["url"]]
    return sponsored_bill_ids_dict

names = getListNames()

# Selectbox with autocomplete/typeahead
selected_name = st.selectbox(
    "Type a name to search and select:",
    names
)

st.write(f"You selected: {selected_name}")

votes_button = st.button(f"Get {selected_name}'s voting record")
sponsor_button = st.button(f"Get {selected_name}'s sponsored bill record")

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
            'Date': values[10],
            'Bill Number': values[9],
            'Vote': values[0].strip(),  # remove \n
            'Bill Description': values[11],
            'Yea': values[3],
            'Nay': values[4],
            'No Vote': values[5],
            'Absent': values[6],
            'Tie-breaking vote': values[12],
            'Extreme minority vote': values[13],
            'Bill ID': values[2],
            'Roll Call ID': roll_call_id
            }
            data.append(row)
        df = pd.DataFrame(data)
        st.write(df)

elif sponsor_button:
     with st.spinner("Pulling sponsored bills..."):
        # find people_id
        people_id = getPeopleID(selected_name)
        activeSessions = getSessions(people_id)
        sponsoredBills = getSponsorships(people_id, activeSessions)
        data = []
        for bill_id, values in sponsoredBills.items():
            row = {
            'Date': values[1],
            'Bill Number': values[0],
            'Status': values[2],
            'Bill Description': values[3],
            'URL': values[5],
            'Bill ID': bill_id
            }
            data.append(row)
        df = pd.DataFrame(data)
        st.write(df)
                      
    
    

