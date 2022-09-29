import datetime
from prettytable import PrettyTable

valid_tags = ["0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB", "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"]
indiv_tags = {"NAME":"Name", "SEX":"Gender", "BIRT":"Birthday", "DEAT":"Death", "FAMC":"Child", "FAMS":"Spouse"}
fam_tags = {"MARR":"Married","DIV":"Divorced","HUSB":"Husband ID","WIFE":"Wife ID","CHIL":"Children"}
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

# Open gedcom file
gedcom_filename = "CS555_FamilyTreeMaris.ged"
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

#checks if birth is before death.   
for indiv in indivs:
    if indiv["Birthday"] > indiv["Death"]:
        output += ("ERROR: INDIVIDUAL: " + indiv["ID"] + ": Death, " + indiv["Death"] + " occurs before birth, " + indiv["Birthday"] + ".\n")
#checks if birth is before marriage. 
for fam in fams:
    husb_id = fam["Husband ID"]
    wife_id = fam["Wife ID"]
    for indiv in indivs:
        if indiv["ID"] == husb_id:
            if indiv["Birthday"] > fam["Married"]:
                output += ("ERROR: INDIVIDUAL: " + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before birth, " + indiv["Birthday"] + "\n")
        if indiv["ID"] == wife_id:
            if indiv["Birthday"] > fam["Married"]:
                output += ("ERROR: INDIVIDUAL: " + indiv["ID"] + ": Marriage date, " + fam["Married"] + " occurs before birth, " + indiv["Birthday"] + "\n")
    

# Open output file
output_filename = "output.txt"
with open(output_filename, 'w') as fp:
    fp.write(output)
