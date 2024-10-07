id_list = ["name", "description", "other"]

id_string = ', '.join([f"'{str(id)}'" for id in id_list])

print(id_string)