import os
this_module = __import__(__name__)

class PhraseFinder:
	def find_phrase_in_the_files(self,search_phrase):
		result_strings = []
		txt_files = self.get_txt_files()
		if len(txt_files) == 0: return []

		for file_path in txt_files:
			f = open(file_path, 'r+', encoding = 'utf-8')
			file_strings = f.readlines()
			f.close()

			for row_count in range(len(file_strings)):
				string = file_strings[row_count].lower()
				if search_phrase in string: result_strings.append('phrase {} was found in the file {}, in the {} row'.format(search_phrase, file_path.replace('.//', ''), row_count + 1 ))

		return result_strings

	def get_txt_files(self):
		txt_files = []
		for root,dirs,files in os.walk('./'):
			for file in files:
				if '.txt' in file:
					txt_files.append(root + '\\' + file)
		return txt_files
