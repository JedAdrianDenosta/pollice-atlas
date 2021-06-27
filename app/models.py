import pymongo
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    make_response,
    abort,
    jsonify,
    session,
    flash)

    
class Models:
    def __init__(self) -> None:
        # self.client = pymongo.MongoClient('localhost', 27017)
        # self.client = pymongo.MongoClient("mongodb://fynmn:October05@cluster0-shard-00-00.2fb7q.mongodb.net:27017,cluster0-shard-00-01.2fb7q.mongodb.net:27017,cluster0-shard-00-02.2fb7q.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-192j1z-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client.get_database('election-system-test')
        self.candidates_records = self.db.candidates
        self.users_records = self.db.users
        self.votes_records = self.db.votes
        self.posts_records = self.db.posts

    # A Function that gets candidates from database and returns them in dictionary format
    def getCandidates(self):
        
        # db = self.client.get_database('election-system-test')
        # self.candidates_records = db.candidates 
        chairperson = self.candidates_records.distinct("chairperson")
        secretary = self.candidates_records.distinct("secretary")
        treasurer = self.candidates_records.distinct("treasurer")
        auditor = self.candidates_records.distinct("auditor")
        business_manager = self.candidates_records.distinct("business_manager")
        representative = self.candidates_records.distinct("representative")

        candidates = {"chairperson": chairperson, "secretary": secretary, "treasurer": treasurer, "auditor": auditor, "business_manager": business_manager, "representative": representative}

        return candidates

    # A Function that gets candidates from database
    def pullCandidates(self):
        
        db = self.client.get_database('election-system-test')
        self.candidates_records = db.candidates
        result = self.candidates_records.find()

        listOfCandidates = []
                    
        for i in result:
            candidate = {k: i[k] for k in i.keys() - {'_id'} - {'id'} - {'course'} - {'section'}}
            listOfCandidates.append(candidate)
            
        
        candidates_list = []

        for i in range(len(listOfCandidates)):
            candidateItem = [listOfCandidates[i]["name"], listOfCandidates[i]["position"], listOfCandidates[i]["party"]]
            candidates_list.append(candidateItem)
            
        return candidates_list


    # A Function that returns name and position of candidates from 2B
    def get2BList(self):
        
        # db = self.client.get_database('election-system-test')
        # self.candidates_records = db.candidates

        result = self.candidates_records.find()

        candidateB = []
                    
        for i in result:
            if i.get("section") == "2B":
                candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'} - {'id'}}
                candidateB.append(candidate)
            
            candidateB_list = []

        for i in range(len(candidateB)):
            candidateBItem = [candidateB[i]["name"], candidateB[i]["position"]]
            candidateB_list.append(candidateBItem)
            
        return candidateB_list
    

    def get2AList(self):
        
        # db = self.client.get_database('election-system-test')
        # self.candidates_records = db.candidates

        result = self.candidates_records.find()

        candidateA = []
                    
        for i in result:
            if i.get("section") == "2A":
                candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'} - {'id'}}
                candidateA.append(candidate)
            
        candidateA_list = []

        for i in range(len(candidateA)):
            candidateAItem = [candidateA[i]["name"], candidateA[i]["position"]]
            candidateA_list.append(candidateAItem)
            
        return candidateA_list
    
    # A Function that gets the voted value from the databse and returns it
    def getVoted(self, name):
        
        # db = self.client.get_database('election-system-test')
        # users_records = db.users

        voted = self.users_records.find_one({'name': name})

        for i,j in voted.items():
            if i == 'voted':
                if j == False:
                    # print("False")
                    return False
                elif j == True:
                    # print("True")
                    return True
                else:
                    pass
                    # print("can't find value")
    
    # A Function that gets object id by name
    def getIDbyName(self, name):
        
        # db = self.client.get_database('election-system-test')
        # user_records = db.users

        record = self.users_records.find_one({'name' : name})

        return record.get('_id')

    
    def pullListOfCandidates(self):
        
        db = self.client.get_database('election-system-test')
        self.candidates_records = db.candidates

        result = self.candidates_records.find()

        return result

    
    # A Function that grabs the votes documents and
    # candidates documents in or database and then
    # returns a dictionary of votes
    # {position: [name, party, votes], position : [name, party, votes]}



    def getVotes(self):
        
        # db = self.client.get_database('election-system-test')
        # votes_records = db.votes
        self.candidates_records = self.db.candidates

        candidate_list = self.candidates_records.find()
        # candidate_description = [] #[name, party, votes]
        total = [] # [{position: [name, party, votes], position : [name, party, votes]}]

        votes = {} # {position: [name, party, votes], position : [name, party, votes]}

        for i in candidate_list:
            for key, value in i.items():
                if key == "name":
                    
                    if i["position"] == "pio":
                        position = "P.I.O."
                    elif i["position"] == "assistant_pio":
                        position = "Assistant P.I.O."
                    elif i["position"] == "representative1":
                        position = "Representative 1"
                    elif i["position"] == "representative2":
                        position = "Representative 2"
    
                    else:
                        list_position = i["position"].split("_")
                        position = " ".join(list_position).title()

                    # candidate_description = [i["name"], i["party"]]
                    # candidate_description.append(votes_records.count_documents({i["position"] : i["name"]})/float(votes_records.count_documents({}))*100)
                    
                    # votes = {position: []}
                    # votes[position].append(candidate_description)
                    votes = {position: []}
                    # votes[position].append(i["position"])
                    votes[position].append(i["name"])
                    votes[position].append(i["party"])
                    if self.votes_records.count_documents({}) != 0:
                        # votes[position].append(str(round(float((votes_records.count_documents({i["position"] : i["name"]})/float(votes_records.count_documents({}))*100)),1)) + "%")

                        votes[position].append(int(self.votes_records.count_documents({i["position"] : i["name"]})))
                        
                    else:
                        pass
                    # print(type(votes[position][2]))
                    total.append(votes)
        
        # print(total)
            
                
        return total
    

    def getPositions(self):
        
        # db = self.client.get_database('election-system-test')
        # self.candidates_records = db.candidates

        candidates = self.candidates_records.find()

        positions = []
        positions_parsed = []

        for i in candidates:
            if i["position"] not in positions:
                # list_position = i["position"].split("_")
                # position = " ".join(list_position).title()
                # positions.append(position)
                positions.append(i["position"])
            else:
                pass
        
        for i in positions:
            if i == "pio":
                pos1 = "P.I.O."
                positions_parsed.append(pos1)
            elif i == "assistant_pio":
                pos = "Assistant P.I.O."
                positions_parsed.append(pos)
            elif i == "representative1":
                pos1 = "Representative 1"
                positions_parsed.append(pos1)
            elif i == "representative2":
                pos = "Representative 2"
                positions_parsed.append(pos)
            else:
                list_positions = i.split("_")
                parsed_list = " ".join(list_positions).title()
                positions_parsed.append(parsed_list)

        return positions_parsed

    
    def getPosts(self):
        
        # db = self.client.get_database('election-system-test')
        # posts_records = db.posts

        records = self.posts_records.find()

        posts_list = [] # [[p1],[p2]]

        for i in records:
            post = {k: i[k] for k in i.keys() - {'_id'}}
            posts_list.append(post)


        sorted_list = sorted(posts_list, key = lambda i: i['post_id'])
        # print(sorted_list)

        return sorted_list




    

    

