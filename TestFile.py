import unittest
import datetime
from datetime import datetime as dt
from prettytable import PrettyTable

valid_tags = ["0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB", "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"]
indiv_tags = {"NAME":"Name", "SEX":"Gender", "BIRT":"Birthday", "DEAT":"Death", "FAMC":"Child", "FAMS":"Spouse"}
fam_tags = {"MARR":"Married","DIV":"Divorced","HUSB":"Husband ID","WIFE":"Wife ID","CHIL":"Children"}
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

# Open gedcom file
gedcom_filename = "sprint2test.ged"
with open(gedcom_filename, 'r') as fp:
    gedcom_data = fp.readlines()


# Parse instructions by line and store each as dictionary
instructions = []
for line in gedcom_data:
  line = line.strip()
  words = line.split()
  level = words[0]
  if len(words)>2 and words[2] in ["INDI", "FAM"]:
    tag = words[2]
    arg = words[1]
  else:
    tag = words[1]
    arg = ' '.join(words[2:])
  full_tag = (f"{level} {tag}")
  is_valid = "Y" if full_tag in valid_tags else "N"
  # print(f"--> {line}")
  # print(f"<-- {level}|{tag}|{is_valid}|{arg}")
  instruction = {}
  instruction["line"] = line
  instruction["level"] = level
  instruction["tag"] = tag
  instruction["is_valid"] = is_valid
  instruction["arg"] = arg
  instructions.append(instruction)


# Sort individual and fam data into lists
indivs = []
fams = []
# Go through each instruction
index = 0
while index<len(instructions):
  instruction = instructions[index]
  # print(instruction)

  # Add individual to indivs
  if instruction["tag"] == "INDI":
    indiv = {}
    indiv["ID"] = instruction["arg"]
    # print(indiv["ID"])
    base_level = instruction["level"]
    index+=1
    instruction = instructions[index]
    # Loop through all instructions between the INDI and the next base_level instruction
    while index<len(instructions) and instructions[index]["level"]!=base_level:
      instruction = instructions[index]
      if instruction["tag"] in indiv_tags:
        tag = instruction["tag"]
        if tag == "BIRT" or tag == "DEAT":
          index+=1
          instruction = instructions[index]
          indiv[indiv_tags[tag]] = instruction["arg"]
        elif tag == "FAMC" or tag == "FAMS":
          if indiv_tags[tag] in indiv:
            indiv[indiv_tags[tag]].append(instruction["arg"])
          else:
            indiv[indiv_tags[tag]] = [instruction["arg"]]
        else:
          indiv[indiv_tags[tag]] = instruction["arg"]
      index+=1
    
    # Get "Death", "Alive", and "Age" attributes
    if "Death" in indiv:
      indiv["Alive"] = "False"
      full_bday = indiv["Birthday"].split()
      full_dday = indiv["Death"].split()
      age = int(full_dday[2]) - int(full_bday[2])
      if ((months.index(full_bday[1])+1 > months.index(full_dday[1])+1) or
          (months.index(full_bday[1])+1 == months.index(full_dday[1])+1 and int(full_bday[0]) > int(full_dday[0]))):
        age -= 1
      indiv["Age"] = age
    else:
      indiv["Death"] = "N/A"
      indiv["Alive"] = "True"
      full_bday = indiv["Birthday"].split()
      full_today = datetime.datetime.now()
      age = full_today.year - int(full_bday[2])
      if ((months.index(full_bday[1])+1 > int(full_today.month)) or
          (months.index(full_bday[1])+1 == int(full_today.month) and int(full_bday[0]) > int(full_today.day))):
        age -= 1
      indiv["Age"] = age

    # Make sure "Child" and "Spouse" attributes exist
    if "Child" not in indiv:
      indiv["Child"] = "N/A"
    if "Spouse" not in indiv:
      indiv["Spouse"] = "N/A"

    indivs.append(indiv)

  # Add family to fams
  elif instruction["tag"] == "FAM":
    fam = {}
    fam["ID"] = instruction["arg"]
    # print(fam["ID"])
    base_level = instruction["level"]
    index+=1
    instruction = instructions[index]
    # Loop through all instructions between the FAM and the next base_level instruction
    while index<len(instructions) and instructions[index]["level"]!=base_level:
      instruction = instructions[index]
      if instruction["tag"] in fam_tags:
        tag = instruction["tag"]
        if tag == "MARR" or tag == "DIV":
          index+=1
          instruction = instructions[index]
          fam[fam_tags[tag]] = instruction["arg"]
        elif tag == "CHIL":
          if fam_tags[tag] in fam:
            fam[fam_tags[tag]].append(instruction["arg"])
          else:
            fam[fam_tags[tag]] = [instruction["arg"]]
        else:
          fam[fam_tags[tag]] = instruction["arg"]
      index+=1

    # Make sure "Divorced" and "Children" attributes exist
    if "Divorced" not in fam:
      fam["Divorced"] = "N/A"
    if "Children" not in fam:
      fam["Children"] = "N/A"

    fams.append(fam)

  else:
    index+=1


# Get husband and wife names from their IDs
for fam in fams:
  husb_id = fam["Husband ID"]
  wife_id = fam["Wife ID"]
  for indiv in indivs:
    if indiv["ID"] == husb_id:
      fam["Husband Name"] = indiv["Name"]
    if indiv["ID"] == wife_id:
      fam["Wife Name"] = indiv["Name"]


# Format tables and output
output = ""

indiv_table = PrettyTable()
indiv_table.field_names = ["ID","Name","Gender","Birthday","Age","Alive","Death","Child","Spouse"]
for indiv in indivs:
  indiv_table.add_row([indiv["ID"],indiv["Name"],indiv["Gender"],indiv["Birthday"],indiv["Age"],indiv["Alive"],indiv["Death"],indiv["Child"],indiv["Spouse"]])

# print("Individuals")
# print(indiv_table)
output += "Individuals\n"
output += str(indiv_table)
output += "\n"

fam_table = PrettyTable()
fam_table.field_names = ["ID","Married","Divorced","Husband ID","Husband Name","Wife ID","Wife Name","Children"]
for fam in fams:
  fam_table.add_row([fam["ID"],fam["Married"],fam["Divorced"],fam["Husband ID"],fam["Husband Name"],fam["Wife ID"],fam["Wife Name"],fam["Children"]])

# print("Families")
# print(fam_table)
output += "Families \n"
output += str(fam_table)
output += " \n"

# Giovanni Sprint 1

# Checks if birth is before death.   
for indiv in indivs:
    if indiv['Death'] != "N/A":
        full_bday = indiv["Birthday"].split()
        full_dday = indiv["Death"].split()
        if (int(full_dday[2]) < int(full_bday[2]) and
           (months.index(full_dday[1])+1 < months.index(full_bday[1])+1 and 
            int(full_dday[0]) < int(full_bday[0]))):
            output += ("ERROR: INDIVIDUAL: US03: " + indiv["ID"] + ": Death, " + indiv["Death"] + " occurs before birth, " + indiv["Birthday"] + ".\n")

# Checks if birth is before marriage. 
for fam in fams:
    husb_id = fam["Husband ID"]
    wife_id = fam["Wife ID"]
    for indiv in indivs:
        full_bday = indiv["Birthday"].split()
        full_mday = fam["Married"].split()
        if indiv["ID"] == husb_id:
            if (int(full_mday[2]) < int(full_bday[2]) and
           (months.index(full_mday[1])+1 < months.index(full_bday[1])+1 and 
            int(full_mday[0]) < int(full_bday[0]))):
                output += ("ERROR: INDIVIDUAL: US02:" + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before birth, " + indiv["Birthday"] + "\n")
        if indiv["ID"] == wife_id:
            if (int(full_mday[2]) < int(full_bday[2]) and
           (months.index(full_mday[1])+1 < months.index(full_bday[1])+1 and 
            int(full_mday[0]) < int(full_bday[0]))):
                output += ("ERROR: INDIVIDUAL: US02:" + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before birth, " + indiv["Birthday"] + "\n")
    
# Daly Sprint 1

# Check if marriage is before death
for fam in fams:
    for indiv in indivs:
        if indiv['ID'] == fam["Husband ID"]:
            if indiv['Death'] != "N/A":
                if dt.strptime(indiv['Death'], '%d %b %Y') < dt.strptime(fam['Married'], '%d %b %Y'):
                    output += ("ERROR: INDIVIDUAL: US05: " + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before death, " + indiv["Death"] + "\n")
        if indiv['ID'] == fam["Wife ID"]:
            if indiv['Death'] != "N/A":
                if dt.strptime(indiv['Death'], '%d %b %Y') < dt.strptime(fam['Married'], '%d %b %Y'):
                    output += ("ERROR: INDIVIDUAL: US05: " + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before death, " + indiv["Death"] + "\n")   
                    
# Check if marriage is before divorce
for fam in fams:
    if fam['Divorced'] != "N/A":
        if dt.strptime(fam['Married'], '%d %b %Y') > dt.strptime(fam['Divorced'], '%d %b %Y'):
            output += ("ERROR: FAMILY: US04: " + fam["ID"] + ": Marriage date, " + fam["Married"] + " occurs after divorce, " + fam["Divorced"] + "\n")

# Anton Sprint 1

# Check if all ages are less than 150 years old
for indiv in indivs:
  if indiv["Age"] >= 150:
    output += ("ERROR: INDIVIDUAL: US07: " + indiv["ID"] + ": Age, " + str(indiv["Age"]) + " is not less than 150 years old\n")

# Check if all dates are before current date
full_today = datetime.datetime.now()
for indiv in indivs:
  full_bday = indiv["Birthday"].split()
  if (full_today.year < int(full_bday[2]) or
      (full_today.year == int(full_bday[2]) and 
       (full_today.month < months.index(full_bday[1])+1 or 
        (full_today.month == months.index(full_bday[1])+1 and full_today.day < int(full_bday[0]))))):
    output += ("ERROR: INDIVIDUAL: US01: " + indiv["ID"] + ": Birthday, " + indiv["Birthday"] + " is after the current date\n")
  full_dday = indiv["Death"]
  if full_dday != "N/A":
    full_dday = full_dday.split()
    if (full_today.year < int(full_dday[2]) or
        (full_today.year == int(full_dday[2]) and 
        (full_today.month < months.index(full_dday[1])+1 or 
          (full_today.month == months.index(full_dday[1])+1 and full_today.day < int(full_dday[0]))))):
      output += ("ERROR: INDIVIDUAL: US01: " + indiv["ID"] + ": Death date, " + indiv["Death"] + " is after the current date\n")
for fam in fams:
  married_date = fam["Married"].split()
  if (full_today.year < int(married_date[2]) or
      (full_today.year == int(married_date[2]) and 
       (full_today.month < months.index(married_date[1])+1 or 
        (full_today.month == months.index(married_date[1])+1 and full_today.day < int(married_date[0]))))):
    output += ("ERROR: FAMILY: US01: " + fam["ID"] + ": Marriage date, " + fam["Married"] + " is after the current date\n")
  divorced_date = fam["Divorced"]
  if divorced_date != "N/A":
    divorced_date = divorced_date.split()
    if (full_today.year < int(divorced_date[2]) or
        (full_today.year == int(divorced_date[2]) and 
         (full_today.month < months.index(divorced_date[1])+1 or 
          (full_today.month == months.index(divorced_date[1])+1 and full_today.day < int(divorced_date[0]))))):
      output += ("ERROR: FAMILY: US01: " + fam["ID"] + ": Divorce date, " + fam["Divorced"] + " is after the current date\n")

#Giovanni Sprint 2

# check if birth is before marriage of parents
for fam in fams:
    husb_id = fam["Husband ID"]
    wife_id = fam["Wife ID"]
    child_id = fam["Children"]
    for indiv in indivs:
        if indiv["ID"] in child_id:
          full_child_bday = indiv["Birthday"].split()
          full_mday = fam["Married"].split()
          if (int(full_mday[2]) > int(full_child_bday[2]) and
             (months.index(full_mday[1])+1 > months.index(full_child_bday[1])+1 and 
             int(full_mday[0]) > int(full_child_bday[0]))):
              output += ("ERROR: INDIVIDUAL: US08: " + indiv["ID"] + ": Parents marriage date, " + fam["Married"] + " occurs after birth of child, " + indiv["Birthday"] + "\n")
            
#check if birth is after death of parents
for fam in fams:
    husb_id = fam["Husband ID"]
    wife_id = fam["Wife ID"]
    child_id = fam["Children"]
    child_bdays = []
    dad_dday = []
    wife_dday = []
    for indiv in indivs:
        if indiv["ID"] in child_id:
            child_bdays.append(indiv["Birthday"].split())
        if husb_id == indiv["ID"]:
            dad_dday = indiv["Death"].split()
        if wife_id == indiv["ID"]:
            wife_dday = indiv["Death"].split()
    for child_bday in child_bdays:
      if (len(dad_dday) != 1 and
        int(dad_dday[2]) < int(child_bday[2]) and
        (months.index(dad_dday[1])+1 < months.index(child_bday[1])+1 and 
        int(dad_dday[0]) < int(child_bday[0]))):
        output += ("ERROR: INDIVIDUAL: US09: " + indiv["ID"] + ": Fathers Death date, " + dad_dday + " occurs before birth of child, " + child_bdays + "\n")
      if (len(wife_dday) != 1 and
        int(wife_dday[2]) < int(child_bday[2]) and
        (months.index(wife_dday[1])+1 < months.index(child_bday[1])+1 and 
        int(wife_dday[0]) < int(child_bday[0]))):
        output += ("ERROR: INDIVIDUAL: US09: " + indiv["ID"] + ": Mothers Death date, " + wife_dday + " occurs before birth of child, " + child_bdays + "\n")
            
            
# Maris Sprint 2

# Check if multiple births are <5
for fam in fams:
    birthdays = []
    for indiv in indivs:
        if indiv['ID'] in fam['Children']:
            birthdays.append(indiv['Birthday'])
    for birthday in birthdays:
        x = birthdays.count(birthday)
        if x >= 5:
            print(("ERROR: FAMILY: US14: " + fam["ID"] + ": Multiple Births >= 5 \n"))
            break

# Check if families have fewer than 15 siblings
for fam in fams:
    numChildren = 0
    for child in fam['Children']:
        numChildren += 1
    if numChildren > 14:
        output += ("ERROR: FAMILY: US15: " + fam["ID"] + ": Number of siblings Not fewer than 15 \n")
    
    
    
# Anton Sprint 2

# Check if all marriages occur at least 14 years after birth of both spouses
for fam in fams:
  married_date = fam["Married"].split()
  husb_id = fam["Husband ID"]
  wife_id = fam["Wife ID"]
  for indiv in indivs:
    if indiv["ID"] == husb_id or indiv["ID"] == wife_id:
      full_bday = indiv["Birthday"].split()
      if (int(full_bday[2])+14 > int(married_date[2]) or
          (int(full_bday[2])+14 == int(married_date[2]) and 
           (months.index(full_bday[1])+1 > months.index(married_date[1])+1 or 
            (months.index(full_bday[1])+1 == months.index(married_date[1])+1 and int(full_bday[0]) > int(married_date[0]))))):
        output += ("ERROR: FAMILY: US10: " + fam["ID"] + ": Marriage date, " + fam["Married"] + " not at least 14 years after birth of both spouses\n")

# Check that no marriage should occur during marriage to another
for fam in fams:
  married_date = fam["Married"].split()
  husb_id = fam["Husband ID"]
  wife_id = fam["Wife ID"]
  divorce_date = "N/A"
  if fam["Divorced"] == "N/A":
    for indiv in indivs:
      if ((indiv["ID"] == husb_id or indiv["ID"] == wife_id) and
          indiv["Death"] != "N/A"):
        if divorce_date == "N/A":
          divorce_date = indiv["Death"].split()
        elif (int(indiv["Death"].split()[2]) < int(divorce_date[2]) or
              (int(indiv["Death"].split()[2]) == int(divorce_date[2]) and 
               (months.index(indiv["Death"].split()[1])+1 < months.index(divorce_date[1])+1 or 
                (months.index(indiv["Death"].split()[1])+1 == months.index(divorce_date[1])+1 and int(indiv["Death"].split()[0]) < int(divorce_date[0]))))):
            divorce_date = indiv["Death"].split()
    if divorce_date == "N/A":
      divorce_date = [full_today.day, months[full_today.month-1], full_today.year]
  else:
    divorce_date = fam["Divorced"].split()
  for other_fam in fams:
    if other_fam["ID"] != fam["ID"] and (husb_id == other_fam["Husband ID"] or wife_id == other_fam["Wife ID"]):
      other_married_date = other_fam["Married"].split()
      if ((int(married_date[2]) < int(other_married_date[2]) or
           (int(married_date[2]) == int(other_married_date[2]) and 
            (months.index(married_date[1])+1 < months.index(other_married_date[1])+1 or 
             (months.index(married_date[1])+1 == months.index(other_married_date[1])+1 and int(married_date[0]) < int(other_married_date[0]))))) and
          (int(other_married_date[2]) < int(divorce_date[2]) or
           (int(other_married_date[2]) == int(divorce_date[2]) and 
            (months.index(other_married_date[1])+1 < months.index(divorce_date[1])+1 or 
             (months.index(other_married_date[1])+1 == months.index(divorce_date[1])+1 and int(other_married_date[0]) < int(divorce_date[0])))))):
        output += ("ERROR: FAMILY: US11: " + other_fam["ID"] + ": Marriage date, " + other_fam["Married"] + " occurs within marriage of " + fam["ID"] + "\n")
        
        
class testUserStory(unittest.TestCase):
    # check if birth is before marriage of parents
    def test_trueUS08(self): 
      for fam in fams:
        husb_id = fam["Husband ID"]
        wife_id = fam["Wife ID"]
        child_id = fam["Children"]
        for indiv in indivs:
            message = "Marriage of parents must be before birth of child!"
            testValue = True
            if indiv["ID"] in child_id:
                full_child_bday = indiv["Birthday"].split()
                full_mday = fam["Married"].split()
                if (int(full_mday[2]) > int(full_child_bday[2]) and
               (months.index(full_mday[1])+1 > months.index(full_child_bday[1])+1 and 
                int(full_mday[0]) > int(full_child_bday[0]))):
                    testValue = False
        self.assertTrue(testValue, message) 

    #check if birth is after death of parents 
    def test_trueUS09(self):
        message = "Birth must be before the death of parents"
        testValue = True
        for fam in fams:
          husb_id = fam["Husband ID"]
          wife_id = fam["Wife ID"]
          child_id = fam["Children"]
          child_bdays = []
          dad_dday = []
          wife_dday = []
          for indiv in indivs:
              if indiv["ID"] in child_id:
                  child_bdays.append(indiv["Birthday"].split())
              if husb_id == indiv["ID"]:
                  dad_dday = indiv["Death"].split()
              if wife_id == indiv["ID"]:
                  wife_dday = indiv["Death"].split()
          for child_bday in child_bdays:
            if (len(dad_dday) != 1 and
              int(dad_dday[2]) < int(child_bday[2]) and
              (months.index(dad_dday[1])+1 < months.index(child_bday[1])+1 and 
              int(dad_dday[0]) < int(child_bday[0]))):
              testValue = False
            if (len(wife_dday) != 1 and
              int(wife_dday[2]) < int(child_bday[2]) and
              (months.index(wife_dday[1])+1 < months.index(child_bday[1])+1 and 
              int(wife_dday[0]) < int(child_bday[0]))):
              testValue = False
        self.assertTrue(testValue, message)
        
    # check if multiple births >5
    def test_trueUS14(self):
        message = "Multiples births should not have more than five children"
        testValue = True
        for fam in fams:
            birthdays = []
            for indiv in indivs:
                if indiv['ID'] in fam['Children']:
                    birthdays.append(indiv['Birthday'])
            for birthday in birthdays:
                x = birthdays.count(birthday)
                if x >= 5:
                    testValue = False
                    break
        self.assertTrue(testValue, message)
            
    # check if count for number of children exists
    def test_trueUS15(self):
        message = "Families should not have more than fifteen children"
        testValue = True
        for fam in fams:
            numChildren = 0
            for child in fam['Children']:
                numChildren += 1
            if numChildren > 14:
                testValue = False 
        self.assertTrue(testValue, message) # check if multiple births >5 

    # Check if all marriages occur at least 14 years after birth of both spouses
    def test_trueUS10(self):
      message = "All marriages must occur at least 14 years after birth of both spouses"
      testValue = True
      for fam in fams:
        married_date = fam["Married"].split()
        husb_id = fam["Husband ID"]
        wife_id = fam["Wife ID"]
        for indiv in indivs:
          if indiv["ID"] == husb_id or indiv["ID"] == wife_id:
            full_bday = indiv["Birthday"].split()
            if (int(full_bday[2])+14 > int(married_date[2]) or
                (int(full_bday[2])+14 == int(married_date[2]) and 
                (months.index(full_bday[1])+1 > months.index(married_date[1])+1 or 
                  (months.index(full_bday[1])+1 == months.index(married_date[1])+1 and int(full_bday[0]) > int(married_date[0]))))):
              testValue = False
      self.assertTrue(testValue, message)

    # Check that no marriage should occur during marriage to another
    def test_trueUS11(self):
      message = "Marriage date must not occur during marriage to another"
      testValue = True
      for fam in fams:
        married_date = fam["Married"].split()
        husb_id = fam["Husband ID"]
        wife_id = fam["Wife ID"]
        divorce_date = "N/A"
        if fam["Divorced"] == "N/A":
          for indiv in indivs:
            if ((indiv["ID"] == husb_id or indiv["ID"] == wife_id) and
                indiv["Death"] != "N/A"):
              if divorce_date == "N/A":
                divorce_date = indiv["Death"].split()
              elif (int(indiv["Death"].split()[2]) < int(divorce_date[2]) or
                    (int(indiv["Death"].split()[2]) == int(divorce_date[2]) and 
                    (months.index(indiv["Death"].split()[1])+1 < months.index(divorce_date[1])+1 or 
                      (months.index(indiv["Death"].split()[1])+1 == months.index(divorce_date[1])+1 and int(indiv["Death"].split()[0]) < int(divorce_date[0]))))):
                  divorce_date = indiv["Death"].split()
          if divorce_date == "N/A":
            divorce_date = [full_today.day, months[full_today.month-1], full_today.year]
        else:
          divorce_date = fam["Divorced"].split()
        for other_fam in fams:
          if other_fam["ID"] != fam["ID"] and (husb_id == other_fam["Husband ID"] or wife_id == other_fam["Wife ID"]):
            other_married_date = other_fam["Married"].split()
            if ((int(married_date[2]) < int(other_married_date[2]) or
                (int(married_date[2]) == int(other_married_date[2]) and 
                  (months.index(married_date[1])+1 < months.index(other_married_date[1])+1 or 
                  (months.index(married_date[1])+1 == months.index(other_married_date[1])+1 and int(married_date[0]) < int(other_married_date[0]))))) and
                (int(other_married_date[2]) < int(divorce_date[2]) or
                (int(other_married_date[2]) == int(divorce_date[2]) and 
                  (months.index(other_married_date[1])+1 < months.index(divorce_date[1])+1 or 
                  (months.index(other_married_date[1])+1 == months.index(divorce_date[1])+1 and int(other_married_date[0]) < int(divorce_date[0])))))):
              testValue = False
        self.assertTrue(testValue, message)
  

# Open output file
output_filename = "testresults.txt"
with open(output_filename, 'w') as fp:
    fp.write(output)

if __name__ == '__main__':
  unittest.main()
