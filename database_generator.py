from glob import glob
from re import compile
from json import load, dump
from functional import seq

# MARK: definitions
class Language:
	def __init__(self, _name, _description):
		self.name = _name
		self.description = _description
		self.notes = []
	
	def serialize(self):
		self.notes = [x.__dict__ for x in self.notes]

class Note:
	def __init__(self, _name, _terms, _new):
		self.name = _name
		self.terms = _terms
		self.new = _new

flashcard_regex = compile(r"(.*?)(?:「.+」|（.+）|{(?:L|H)+})*:::?.*")
comment_regex = compile(r"<!--[\w\W]*?(?:-->|$)")
markup_regex = compile(r"(?P<delim>\*\*|\*|__|_)(?P<text>[^\*_]+)(?P=delim)")

def remove_comments_and_markup(string):
	return markup_regex.sub(r"\g<text>", comment_regex.sub("", string))

def is_not_読み(card):
	return "読み" not in card

# MARK: config
database_file = "languages.json"
obsidian_path = "/Users/simonomi/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
notes_to_skip = ["ひらがな", "カタカナ", "助詞"]

languages = [
	Language(
		"日本語", 
		"japanese is one of the languages most different from english. as such, for a native english speaker, learning japanese is quite the interesting challenge. new sentence structure, new grammar, not one, not two, but THREE new writing systems, one of which is kanji for crying out loud! i quite enjoy learning all the new concepts."
	),
	Language(
		"русский", 
		"i have... mixed feelings about russian. on one hand, coming from japanese, its wayyy more similar to english, making it (theoretically) easier to learn. on the other hand, how can one be expected to pronounce 12 different consonants in a row??? this language is so silly and i really just don't know how to feel about it."
	)
]

# MARK: execution
with open(database_file) as file:
	old_languages = load(file)

for language in languages:
	language_files = glob(obsidian_path + language.name + "/**/*.md", recursive=True)
	
	old_language = [x for x in old_languages if x["name"] == language.name][0]
	old_words = [word for note in old_language["notes"] for word in note["terms"] + note["new"]]

	for language_file in language_files:
		note_name = language_file.split("/")[-1][:-3]
		if note_name in notes_to_skip: continue
		
		with open(language_file) as file:
			is_active = file.readline().startswith(f"#{language.name}")
			if not is_active: continue
			
			file_text = remove_comments_and_markup(file.read())
		
		note_words = seq(file_text.split("\n"))\
			.filter(is_not_読み)\
			.map(flashcard_regex.match)\
			.filter(bool)\
			.map(lambda match: match.group(1))
		
		note_old_words = [x for x in note_words if x in old_words]
		note_new_words = [x for x in note_words if x not in old_words]
		
		note = Note(
			note_name,
			note_old_words,
			note_new_words
		)
		
		language.notes.append(note)
		if note.new:
			print(f"new terms for {language.name}/{note.name}: [{', '.join(note.new)}]")

[x.serialize() for x in languages]
output_data = [x.__dict__ for x in languages]

dont_save = input("save? ").lower().startswith("n")

if dont_save:
	print("cancelling")
	exit()
else:
	print("saving")

with open(database_file, "w") as file:
	dump(output_data, file, ensure_ascii=False)
