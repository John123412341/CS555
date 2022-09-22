from prettytable import PrettyTable

valid_tags = ["0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB", "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"]
indiv_tags = {"NAME":"Name", "SEX":"Gender", "BIRT":"Birthday", "DEAT":"Death", "FAMC":"Child", "FAMS":"Spouse"}

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
index = 0
while index<len(instructions):
  instruction = instructions[index]

  if instruction["tag"] == "INDI":
    indiv = {}
    indiv["ID"] = instruction["arg"]
    # print(indiv["ID"])
    base_level = instruction["level"]
    index+=1
    if index<len(instructions):
      instruction = instructions[index]

    while instruction["level"]!=base_level and index<len(instructions):
      instruction = instructions[index]

      if instruction["tag"] in indiv_tags:
        tag = instruction["tag"]
        if tag == "BIRT":
          index+=1
          instruction = instructions[index]
          indiv[indiv_tags[tag]] = instruction["arg"]
        elif tag == "DEAT":
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
    
    if "Death" in indiv:
      indiv["Alive"] = "False"
      birth_year = indiv["Birthday"].split()[-1]
      death_year = indiv["Death"].split()[-1]
      indiv["Age"] = int(death_year) - int(birth_year)
    else:
      indiv["Death"] = "N/A"
      indiv["Alive"] = "True"
      birth_year = indiv["Birthday"].split()[-1]
      indiv["Age"] = 2022 - int(birth_year)

    if "Child" not in indiv:
      indiv["Child"] = "N/A"
    if "Spouse" not in indiv:
      indiv["Spouse"] = "N/A"

    indivs.append(indiv)

  else:
    index+=1


indiv_table = PrettyTable()
indiv_table.field_names = ["ID","Name","Gender","Birthday","Age","Alive","Death","Child","Spouse"]
for indiv in indivs:
  indiv_table.add_row([indiv["ID"],indiv["Name"],indiv["Gender"],indiv["Birthday"],indiv["Age"],indiv["Alive"],indiv["Death"],indiv["Child"],indiv["Spouse"]])

print(indiv_table)

# # Open output file
# output_filename = "output.txt"
# with open(output_filename, 'w') as fp:
#     fp.write(output)