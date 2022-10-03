import datetime
from datetime import datetime as dt
from prettytable import PrettyTable

valid_tags = ["0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB", "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"]
indiv_tags = {"NAME":"Name", "SEX":"Gender", "BIRT":"Birthday", "DEAT":"Death", "FAMC":"Child", "FAMS":"Spouse"}
fam_tags = {"MARR":"Married","DIV":"Divorced","HUSB":"Husband ID","WIFE":"Wife ID","CHIL":"Children"}
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

# Open gedcom file
gedcom_filename = "TEST.ged"
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
            output += ("ERROR: INDIVIDUAL: US03:" + indiv["ID"] + ": Death, " + indiv["Death"] + " occurs before birth, " + indiv["Birthday"] + ".\n")

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
            output += ("ERROR: FAMILY: US04: " + fam["ID"] + ": Marriage date, " + fam["Married"] + " occurs before divorce, " + fam["Divorced"] + "\n")

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

# Open output file
output_filename = "testresults.txt"
with open(output_filename, 'w') as fp:
    fp.write(output)
