valid_tags = ["0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB", "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"]

# Open gedcom file
gedcom_filename = "CS555_FamilyTreeMaris.ged"
with open(gedcom_filename, 'r') as fp:
    gedcom_data = fp.readlines()

# Parse by line
output = ""
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
  output += f"--> {line}\n"
  output += f"<-- {level}|{tag}|{is_valid}|{arg}\n"

# print(output)

# Open output file
output_filename = "output.txt"
with open(output_filename, 'w') as fp:
    fp.write(output)