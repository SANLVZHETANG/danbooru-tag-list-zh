import os
import requests
import collections
import csv
import time

class Complete(Exception): pass

csv_filename = input('Output filename: ')
minimum_count = input('Minimum tag count (> 50 is preferable): ')
dashes = input('replace \'_\' with \'-\'? (often better for prompt following) (Y/n): ')
exclude = input('enter categories to exclude: (general,artist,copyright,character,post) (press enter for none): \n')
alias = input('Include aliases? (Only supported in tag-complete) (y/N): ')
boards = input('Enter boards to scrape danbooru(d), e621(e), both(de) (default: danbooru): ')

boards = boards.lower()
if (not "d" in boards) and (not "e" in boards):
    boards = "d"

excluded = ""
excluded += "0" if "general" in exclude else ""
excluded += "1" if "artist" in exclude else ""
excluded += "3" if "copyright" in exclude else ""
excluded += "4" if "character" in exclude else ""
excluded += "5" if "post" in exclude else ""

kaomojis = [
    "0_0", "(o)_(o)", "+_+", "+_-", "._.", "<o>_<o>", "<|>_<|>", "=_=", ">_<",
    "3_3", "6_9", ">_o", "@_@", "^_^", "o_o", "u_u", "x_x", "|_|", "||_||",
]

if not '.csv' in csv_filename:
    csv_filename += '.csv'

if not 'n' in dashes.lower():
    dashes = 'y'
    csv_filename += '-temp'

if not 'y' in alias.lower():
    alias = 'n'

if not minimum_count.isdigit():
    minimum_count = 50

# Base URL without the page parameter
base_url = 'https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count'
alias_url = 'https://danbooru.donmai.us/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count'
e6_base_url = 'https://e621.net/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count'
e6_alias_url = 'https://e621.net/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count'

dan_aliases = collections.defaultdict(str)
e6_aliases = collections.defaultdict(str)

def get_aliases(alias_url,type):
    # create alias dictionary
    try:
        aliases = collections.defaultdict(str)
        for page in range(1,1001):
            # Update the URL with the current page
            url = f'{alias_url}&page={page}'
            # Fetch the JSON data
            response = requests.get(url,headers={"User-Agent": "tag-list/2.0"})
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Break the loop if the data is empty (no more tags to fetch)
                if not data:
                    print(f'No more data found at page {page}. Stopping.', flush=True)
                    break
                for item in data:
                    if type == "e": # danbooru doesn't have post counts for aliases
                        if int(item['post_count']) < int(minimum_count):
                            raise Complete
                    aliases[item['consequent_name']] += ',' + item['antecedent_name'] if aliases[item['consequent_name']] else item['antecedent_name']
            print(f'Page {page} aliases processed.', flush=True)
            # Sleep for 0.5 second because we have places to be
            time.sleep(0.5)
    except(Complete):
        print("reached the post threshold")
    return(aliases)

if alias == 'y':
    if "d" in boards:
        dan_aliases = get_aliases(alias_url,"d")
    #if "e" in boards:
    #    e6_aliases = get_aliases(e6_alias_url,"e")

#######
if "d" in boards:
    dan_tags = {}
    try:
        for page in range(1, 1001):
            # Update the URL with the current page
            url = f'{base_url}&page={page}'
            # Fetch the JSON data
            response = requests.get(url,headers={"User-Agent": "tag-list/2.0"})
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Break the loop if the data is empty (no more tags to fetch)
                if not data:
                    print(f'No more data found at page {page}. Stopping.', flush=True)
                    break
                
                for item in data:
                    if int(item['post_count']) < int(minimum_count): # break if below minimum count
                        raise Complete
                    if not str(item['category']) in excluded:
                        if alias == 'n':
                            dan_tags[item['name']] = [item['category'],item['post_count'],'']
                        else:
                            alt = dan_aliases.get(item['name']) if dan_aliases.get(item['name']) != None else ''
                            dan_tags[item['name']] = [item['category'],item['post_count'],alt]
            else:
                print(f'Failed to fetch data for page {page}. HTTP Status Code: {response.status_code}', flush=True)
                break
            print(f'Danbooru page {page} processed.', flush=True)
            # Sleep for 0.5 second because we have places to be
            time.sleep(0.5)
    except(Complete):
        pass
if "e" in boards:
    e6_tags = {}
    try:
        for page in range(1, 1001):
            # Update the URL with the current page
            url = f'{e6_base_url}&page={page}'
            # Fetch the JSON data
            response = requests.get(url,headers={"User-Agent": "tag-list/2.0"})
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Break the loop if the data is empty (no more tags to fetch)
                if not data:
                    print(f'No more data found at page {page}. Stopping.', flush=True)
                    break
                
                for item in data:
                    if int(item['post_count']) < int(minimum_count): # break if below minimum count
                        raise Complete
                    if not str(item['category']) in excluded:
                        #if alias == 'n':
                        e6_tags[item['name']] = [item['category'],item['post_count'],'']
                        #else:
                        #    alt = e6_aliases.get(item['name']) if e6_aliases.get(item['name']) != None else ''
                        #    e6_tags[item['name']] = [item['category'],item['post_count'],alt]
            else:
                print(f'Failed to fetch data for page {page}. HTTP Status Code: {response.status_code}', flush=True)
                break
            print(f'e621 page {page} processed.', flush=True)
            # Sleep for 0.5 second because we have places to be
            time.sleep(0.5)
    except Complete:
        print(f'All tags with {minimum_count} posts or greater have been scraped.')

# Merge boards
if ("d" in boards) and ("e" in boards):
    for tag in dan_tags:
        if tag in e6_tags:
            e6_tags[tag][1] += dan_tags[tag][1] # combined count
            """if e6_tags[tag][2] != None and dan_tags[tag][2] != None:
                if e6_tags[tag][2] == "":
                    e6_tags[tag][2] += dan_tags[tag][2]  # aliases
                else:
                    e6_tags[tag][2] += "," + dan_tags[tag][2]"""
    dan_tags.update(e6_tags)
    full_tags = dan_tags
elif "d" in boards:
    full_tags = dan_tags
else:
    full_tags = e6_tags

# Open a file to write
print("writing to file")
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # danbooru
    # Write the data
    for key, value in full_tags.items():
        if not str(value[0]) in excluded:
            if alias == 'n':
                writer.writerow([key,value[0],value[1],''])
            else:
                writer.writerow([key,value[0],value[1],value[2]])
    # Explicitly flush the data to the file
    file.close()

    if dashes == 'y':
        print(f'Replacing \'_\' with \'-\'')
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            with open(csv_filename.removesuffix('-temp'), 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                for row in reader:
                    if not row[0] in kaomojis:
                        row[0] = row[0].replace("_", "-")
                        row[3] = row[3].replace("_", "-")
                    writer.writerow(row)
                outfile.close()    
            csvfile.close()
        os.remove(csv_filename)
        csv_filename = csv_filename.removesuffix('-temp')

print(f'Data has been written to {csv_filename}', flush=True)