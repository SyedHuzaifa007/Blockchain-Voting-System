import pyodbc

# Connect with SQL Server database - Host Name - PORT No. - UserName - Password - Database name
mydb = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=103.31.104.114;"
    "UID=user;"
    "PWD=12345678;"
    "Database=voting_system;"
)

def connect():
    try:
        print("--------------------------------------------------")
        mycursor = mydb.cursor()
        mycursor.execute("""CREATE TABLE admin (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                registration_id VARCHAR(20) NOT NULL UNIQUE, 
                                name VARCHAR(50) NOT NULL, 
                                cnic VARCHAR(12) NOT NULL UNIQUE, 
                                phone VARCHAR(10) NOT NULL UNIQUE, 
                                gender VARCHAR(7) NOT NULL)""")
        mycursor = mydb.cursor()
        mycursor.execute("""CREATE TABLE vote (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                voter_id VARCHAR(20) NOT NULL UNIQUE, 
                                poll VARCHAR(50) NOT NULL, 
                                district VARCHAR(50) NOT NULL)""")
        mycursor = mydb.cursor()
        mycursor.execute("""CREATE TABLE voters (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                voter_id VARCHAR(20) NOT NULL UNIQUE, 
                                name VARCHAR(50) NOT NULL, 
                                cnic VARCHAR(12) NOT NULL UNIQUE, 
                                phone VARCHAR(10) NOT NULL UNIQUE, 
                                gender VARCHAR(7) NOT NULL)""")
        print("[DONE]   BUILD SUCCESSFULLY!!")
        print("--------------------------------------------------")
    except Exception as e:
        print("[DONE]   CONNECTED SUCCESSFULLY!!")
        print("--------------------------------------------------")


def findBycnic(cnic):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC FindUserBycnic @cnic=?", (cnic,))
        result = mycursor.fetchone()
        return result
    except Exception as e:
        print("[WARN]   Failed to find user by cnic")


def findByVoterId(voterId):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC FindUserByVoterId @VoterId=?", (voterId,))
        result = mycursor.fetchone()
        return result
    except Exception as e:
        print("[WARN]   Failed to find user by Voter ID")


def audit_log(table_name, action, changed_by):
    try:
        mycursor = mydb.cursor()
        sql = "INSERT INTO AuditTrail (TableName, Action, ChangedBy, ChangeTime) VALUES (?, ?, ?, GETDATE())"
        mycursor.execute(sql, (table_name, action, changed_by))
        mydb.commit()
    except Exception as e:
        print("[WARN]   Failed to log audit trail:", e)
    
def addVoter(voterId, name, cnic, phone, gender):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC AddVoter @VoterId=?, @Name=?, @cnic=?, @Phone=?, @Gender=?", (voterId, name, cnic, phone, gender))
        mydb.commit()
        audit_log('voters', 'Insert', 'Admin')
        return True
    except Exception as e:
        print("[WARN]   User Record failed to register")
        return False

def submitVote(voterId, poll, district):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC SubmitVote @VoterId=?, @Poll=?, @District=?", (voterId, poll, district))
        mydb.commit()
        return True
    except Exception as e:
        print("[WARN]   Unable to submit Vote")
        return False

def findByVoterIdinVote(voterId):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC FindVoteByVoterId @VoterId=?", (voterId,))
        result = mycursor.fetchone()
        return result
    except Exception as e:
        print("[WARN]   Error during finding voter from vote entity")


def findByRegId(regId):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC FindAdminByRegId @RegId=?", (regId,))
        result = mycursor.fetchone()
        return result
    except Exception as e:
        print("[WARN]   Failed to find admin using Registered ID")


def findByCNICinAdmin(cnic):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC FindAdminBycnic @cnic=?", (cnic,))
        result = mycursor.fetchone()
        return result
    except Exception as e:
        print("[WARN]   Failed to find admin using cnic No.")

def addAdmin(regId, name, cnic, phone, gender):
    try:
        mycursor = mydb.cursor()
        sql = "EXEC AddAdmin ?, ?, ?, ?, ?"
        mycursor.execute(sql, (regId, name, cnic, phone, gender))
        mydb.commit()
        return True
    except Exception as e:
        print("[WARN] Unable to register admin")
        return False


def getTotalCount():
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC GetTotalVoteCount")
        result = mycursor.fetchone()
        return result['TotalCount']
    except Exception as e:
        print("[WARN]   Error while fetching total vote count")

def getTotalUserCount():
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC GetTotalUserCount")
        result = mycursor.fetchone()
        return result[0]  # Returning the total user count
    except Exception as e:
        print("[WARN]   Error while fetching total user count:", e)
        return None


def getPartyCount(party):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC GetPartyCount @Party=?", (party,))
        result = mycursor.fetchone()
        return result[0]  # Returning the party count
    except Exception as e:
        print("[WARN]   Error while fetching party count:", e)
        return None


def getallVoters():
    try:
        mycursor = mydb.cursor()
        mycursor.execute("EXEC GetAllVoters")
        result = mycursor.fetchall()
        return result
    except Exception as e:
        print("[WARN]   Failed to fetch all Voters record:", e)
        return None



def getUserBycnic(cnic):
    try:
        mycursor = mydb.cursor()
        sql ="""SELECT voters.name, voters.phone, voters.gender, vote.district
                FROM voters
                LEFT JOIN vote ON voters.voter_id=vote.voter_id
                WHERE cnic = '{0}'""".format(cnic)
        mycursor.execute(sql)
        result = mycursor.fetchone()
        return result
    except:
        print("[WARN]   Failed to fetch user by cnic")


def updateUserBycnic(name, phone, gender, cnic):
    try:
        mycursor = mydb.cursor()
        sql ="""UPDATE voters SET name='{0}', phone='{1}', gender='{2}' 
                WHERE cnic='{3}'""".format(name, phone, gender, cnic)
        mycursor.execute(sql)
        mydb.commit()
        return True
    except:
        print("[WARN]   Failed to update user record")
        return False


def deleteUserBycnic(cnic):
    try:
        mycursor = mydb.cursor()
        sql ="""DELETE FROM voters
                WHERE cnic = '{0}'""".format(cnic)
        mycursor.execute(sql)
        mydb.commit()
        return True
    except:
        print("[WARN]   Failed to delete user")
        return False
