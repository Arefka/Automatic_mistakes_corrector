import os
import re
import pickle
from collections import OrderedDict

'''
=======================================================================

    For updating the dictionary files with context:      
        1. put all new sentences to the books folder
        2. call DictionaryCreator().make_files_of_etalon_words(True)

    For updating the dictionary files without context:
        1. put all new sentences to the books folder
        2. call DictionaryCreator().make_files_of_etalon_words()    

=======================================================================
'''

class DictionaryCreator:

    __books_folder_path = os.path.dirname(__file__) + '/books/'
    __full_file_path_to_the_words_friendly = os.path.dirname(__file__) + '/etalon_dictionary/words_friendly.pkl'
    __full_file_path_to_the_words_len = os.path.dirname(__file__) + '/etalon_dictionary/words_len.pkl'
    __full_file_path_to_the_all_words = os.path.dirname(__file__) + '/etalon_dictionary/words_in_set.pkl'


    def __init__(self):
        self.__loader()

    def __loader(self):
        self.__set_of_all_words = self.__load_obj(self.__full_file_path_to_the_all_words) \
            if os.path.exists(self.__full_file_path_to_the_all_words) else set()
        self.__dict_of_all_words_len = self.__load_obj(self.__full_file_path_to_the_words_len) \
            if os.path.exists(self.__full_file_path_to_the_words_len) else {}
        self.__dict_of_all_words_friendly = self.__load_obj(self.__full_file_path_to_the_words_friendly) \
            if os.path.exists(self.__full_file_path_to_the_words_friendly) else {}

    def __load_obj(self, path_and_name):
        with open(path_and_name, 'rb') as f:
            return pickle.load(f)

    def __save_obj(self, obj, path_and_name):
        with open(path_and_name, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


    def __make_words_list_from_sentence(self, sentence: str) -> list:
        split_regex = re.compile('[^а-яА-Я -]')
        words_list = split_regex.sub('', sentence.lower()).split(' ')
        words_list_without_spaces = [word for word in words_list if word.strip()]
        return list(dict.fromkeys(words_list_without_spaces))

    def __make_sentences_list_from_text(self, text_fragment: str) -> list:
        split_regex = re.compile(r'[.|!|?|…|;]')
        sentences = filter(lambda t: t, [t.strip() for t in split_regex.split(text_fragment)])
        return list(sentences)

    def __add_to_lists_values(self, current_sequence: list, new_sequence: list) -> list:
        union_of_lists = sum([current_sequence, new_sequence], [])
        return list(dict.fromkeys(union_of_lists))

    def __update_current_set_of_all_words(self, new_word: str):
        self.__set_of_all_words.add(new_word)

    def __update_current_dict_of_all_words_len(self, new_word: str):
        new_value = [new_word]
        if len(new_word) in self.__dict_of_all_words_len:
            self.__dict_of_all_words_len[len(new_word)] = self.__add_to_lists_values(
                self.__dict_of_all_words_len[len(new_word)], new_value)
        else:
            self.__dict_of_all_words_len[len(new_word)] = new_value

    def __update_current_dict_of_words_friendly(self, new_word: str, new_neighboring_words: list):
        if not new_neighboring_words:
            return
        if new_word in self.__dict_of_all_words_friendly:
            self.__dict_of_all_words_friendly[new_word] = self.__add_to_lists_values(
                self.__dict_of_all_words_friendly[new_word], new_neighboring_words)
        else:
            self.__dict_of_all_words_friendly[new_word] = new_neighboring_words

    def make_files_of_etalon_words(self, add_sentences_to_the_context=False):
        all_files_of_books_folder = os.listdir(self.__books_folder_path)
        files_of_books = filter(lambda x: x.endswith('.txt'), all_files_of_books_folder)

        text_fragment = ''
        for file_name in list(files_of_books):
            file_path = self.__books_folder_path + file_name
            with open(file_path, 'r', encoding='utf-8') as our_file:
                text_fragment += our_file.read().replace('\n', ' ')

        if text_fragment:
            sentences_list = self.__make_sentences_list_from_text(text_fragment)

            for sentence in sentences_list:
                words_list = self.__make_words_list_from_sentence(sentence)

                for current_word in words_list:
                    self.__update_current_set_of_all_words(current_word)
                    if add_sentences_to_the_context:
                        neighboring_words = [word for word in words_list if word != current_word]
                        self.__update_current_dict_of_all_words_len(current_word)
                        self.__update_current_dict_of_words_friendly(current_word, neighboring_words)

            self.__save_obj(self.__set_of_all_words, self.__full_file_path_to_the_all_words)
            if add_sentences_to_the_context:
                self.__dict_of_all_words_len = dict(
                    OrderedDict(sorted(self.__dict_of_all_words_len.items(), key=lambda t: t[0])))
                self.__save_obj(self.__dict_of_all_words_len, self.__full_file_path_to_the_words_len)
                self.__dict_of_all_words_friendly = dict(
                    OrderedDict(sorted(self.__dict_of_all_words_friendly.items(), key=lambda t: t[0])))
                self.__save_obj(self.__dict_of_all_words_friendly, self.__full_file_path_to_the_words_friendly)

            print('The files creation is completed...')

        else:
            print('There are no books in our folder...')

