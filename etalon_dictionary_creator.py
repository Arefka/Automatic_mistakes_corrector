import os
import re
import pickle

class DictionaryCreator:
    books_folder_path = os.path.dirname(__file__) + '/books/'


    def add_to_lists_values(self, current_sequence: list, new_sequence: list) -> list:
        union_of_lists = sum([current_sequence, new_sequence], [])
        return list(dict.fromkeys(union_of_lists))

    def update_current_dictionary(self, current_dictionary: dict, new_word: str, new_neighboring_words: list):
        if current_dictionary and new_word in current_dictionary:
            current_dictionary[new_word] = self.add_to_lists_values(current_dictionary[new_word], new_neighboring_words)
        else:
            current_dictionary[new_word] = new_neighboring_words


    def make_sentences_list_from_text(self, text_fragment: str) -> list:
        split_regex = re.compile(r'[.|!|?|…|;]')
        sentences = filter(lambda t: t, [t.strip() for t in split_regex.split(text_fragment)])
        return list(sentences)

    def make_words_list_from_sentence(self, sentence: str) -> list:
        split_regex = re.compile('[^а-яА-Я -]')
        words_list = split_regex.sub('', sentence.lower()).split(' ')
        words_list_without_spaces = [word for word in words_list if word.strip()]
        return list(dict.fromkeys(words_list_without_spaces))

    def save_file_of_etalon_dictionary(self, current_dictionary: dict, file_name: str):
        with open('etalon_dictionary/' + file_name + '.pkl', 'wb') as f:
            pickle.dump(current_dictionary, f, pickle.HIGHEST_PROTOCOL)

    def make_file_of_etalon_dictionary(self):
        etalon_dictionary = {}
        all_files_of_books_folder = os.listdir(self.books_folder_path)
        files_of_books = filter(lambda x: x.endswith('.txt'), all_files_of_books_folder)

        for file_name in list(files_of_books):
            file_path = self.books_folder_path + file_name
            with open(file_path, 'r', encoding='utf-8') as our_file:
                text_fragment = our_file.read().replace('\n',' ')

            if text_fragment:
                sentences_list = self.make_sentences_list_from_text(text_fragment)

                for sentence in sentences_list:
                    words_list = self.make_words_list_from_sentence(sentence)

                    for current_word in words_list:
                        neighboring_words = [word for word in words_list if word != current_word]
                        self.update_current_dictionary(etalon_dictionary, current_word, neighboring_words)

        if etalon_dictionary:
            file_name = 'dictionary_of_etalon_words'
            self.save_file_of_etalon_dictionary(etalon_dictionary, file_name)
            print('The file creation is completed')