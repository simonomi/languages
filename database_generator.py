from glob import glob
from re import compile
from json import load, dump
from functional import seq

# MARK: definitions
class Language:
	def __init__(self, _name, _description):
		self.name = _name
		self.description = _description
		self.new = []

flashcard_regex = compile(r"(.*?)(?:「.+」|（.+）|{(?:L|H)+})?:::?.*")
comment_regex = compile(r"<!--[\w\W]*?(?:-->|$)")

def remove_comments(string):
	return comment_regex.sub("", string)

def is_not_読み(card):
	return "読み" not in card

def identity(x):
	return x

# MARK: config
database_file = "languages.json"
obsidian_path = "/Users/simonomi/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
notes_to_skip = ["ひらがな", "カタカナ", "助詞"]

languages = [
	Language(
		"日本語", 
		"japanese description"
	),
	Language(
		"русский", 
		"russian description"
	)
]

# MARK: execution
with open(database_file) as file:
	old_languages = load(file)

for language in languages:
	language_notes = glob(obsidian_path + language.name + "/**/*.md", recursive=True)
	
	old_language = [x for x in old_languages if x["name"] == language.name][0]
	old_words = old_language["words"] + old_language["new"]
	
	language_words = []
	for language_note in language_notes:
		if language_note.split("/")[-1][:-3] in notes_to_skip: continue
		
		with open(language_note) as file:
			is_active = file.readline().startswith(f"#{language.name}")
			if not is_active: continue
			
			file_text = remove_comments(file.read())
		
		note_words = seq(file_text.split("\n"))\
			.filter(is_not_読み)\
			.map(flashcard_regex.match)\
			.filter(identity)\
			.map(lambda match: match.group(1))
		
		language_words += note_words
	
	language.words = [word for word in language_words if word in old_words]
	language.new   = [word for word in language_words if word not in old_words]

output_data = [x.__dict__ for x in languages]

with open(database_file, "w") as file:
	dump(output_data, file, ensure_ascii=False)
