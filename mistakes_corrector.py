import os
import re
import pymorphy2
from datetime import timedelta, datetime
import pickle

'''
=======================================================================

    For correcting mistakes in a sentence:      
        call MistakesCorrector().check_the_sentence('your sentence')   

=======================================================================
'''

class MistakesCorrector:
    __full_file_path_to_the_words_friendly = os.path.dirname(__file__) + '/etalon_dictionary/words_friendly.pkl'
    __full_file_path_to_the_words_len = os.path.dirname(__file__) + '/etalon_dictionary/words_len.pkl'
    __full_file_path_to_the_all_words = os.path.dirname(__file__) + '/etalon_dictionary/words_in_set.pkl'
    __endtime = datetime.utcnow()
    __neighboring_words_set = set()

    def __init__(self):
        self.__loader()

    def __loader(self):
        self.__dict_of_all_words_friendly = self.__load_obj(self.__full_file_path_to_the_words_friendly)
        self.__dict_of_all_words_len = self.__load_obj(self.__full_file_path_to_the_words_len)
        self.__set_of_all_words = self.__load_obj(self.__full_file_path_to_the_all_words)
        self.__morph = pymorphy2.MorphAnalyzer()

    def __load_obj(self, path_and_name):
        with open(path_and_name, 'rb') as f:
            return pickle.load(f)


    def __create_dict_of_input_words(self, input_sentence : str) -> {}:
        reg = re.compile('[^а-яА-Я -]')
        return dict.fromkeys(reg.sub('', input_sentence.lower()).split(' '))

    def __word_is_in_etalon_words_set(self, input_word : str) -> bool:
        return (input_word in self.__set_of_all_words)

    def __word_is_in_neighboring_words_set(self, input_word : str) -> bool:
        return (input_word in self.__neighboring_words_set)

    def __update_neighboring_words_set(self, input_word) -> bool:
        if input_word in self.__dict_of_all_words_friendly:
            self.__neighboring_words_set = self.__neighboring_words_set.union(set(self.__dict_of_all_words_friendly[input_word]))
            return True
        return False

    def __words_are_similar(self, first_word: str, second_word: str) -> bool:
        return (first_word[-1] == second_word[-1]
                and self.__morph.parse(first_word)[0].tag.POS == self.__morph.parse(second_word)[0].tag.POS)


    def __find_nearest_key_word(self, input_word : str) -> [bool, str]:
        typing_words = {
            'й':['ц', 'ы', 'ф'], 'ц':['й','ф','ы','в','у'], 'у':['ц','ы','в','а','к'], 'к':['у','в','а','п','е'],
            'е':['к','а','п','р','н'], 'н':['е','п','р','о','г'], 'г':['н','р','о','л','г'], '-':['-'],
            'ш':['г','о','л','д','щ'], 'щ':['ш','л','д','ж','з'], 'з':['щ','д','ж','э','х'],
            'х':['з','ж','э','ъ'], 'ъ':['х','э'], 'ф':['й','ц','ы','ч','я'], 'ы':['ф','й','ц','у','в','с','ч','я'],
            'в':['ы','ц','у','к','а','м','с','ч'], 'а':['в','у','к','е','п','и','м','с'],
            'п':['а','к','е','н','р','т','и','м'], 'р':['п','е','н','г','о','ь','т','и'],
            'о':['р','н','г','ш','л','б','ь','т'], 'л':['о','г','ш','щ','д','ю','б','ь'],
            'д':['л','ш','щ','з','ж','ю','б'], 'ж':['д','щ','з','х','э','ю'], 'э':['ж','з','х','ъ','ж'],
            'я':['ф','ы','ч'], 'ч':['я','ы','в','с'], 'с':['ч','в','а','м'], 'м':['с','а','п','и'], 'и':['м','п','р','т'],
            'т':['и','р','о','ь'], 'ь':['т','о','л','б'], 'б':['ь','л','д','ю'], 'ю':['б','д','ж']
        }

        for numer, origen_item in enumerate(input_word):
            for typing_item in typing_words[origen_item]:
                if datetime.utcnow() > self.__endtime:
                    print('Timeout of SentenceCorrector')
                    return [False, input_word]
                new_word = input_word[:numer] + typing_item + input_word[numer+1:]

                if (self.__word_is_in_neighboring_words_set(new_word)
                        and self.__words_are_similar(input_word, new_word)):
                    self.__update_neighboring_words_set(new_word)
                    return [True, new_word]

        return [False, input_word]


    def __find_splitting_words(self, input_word : str) -> [bool, str, str]:
        if len(input_word) < 3:
            return [False, input_word, input_word]

        for numer in range(2, len(input_word)-2):
            if datetime.utcnow() > self.__endtime:
                print('Timeout of SentenceCorrector')
                return [False, input_word, input_word]
            first_word = input_word[:numer]
            second_word = input_word[numer:]

            if (self.__word_is_in_neighboring_words_set(first_word)
                    and self.__word_is_in_neighboring_words_set(second_word)
                    and self.__words_are_similar(input_word, second_word)):
                self.__update_neighboring_words_set(first_word)
                self.__update_neighboring_words_set(second_word)
                return [True, first_word, second_word]

        return [False, input_word, input_word]


    def __calculate_Damerau_Levenshtein_distance(self, firstWord: str, secondWord: str):
        d = {}
        lenghtWord1, lenghtWord2 = len(firstWord), len(secondWord)

        if lenghtWord1 > lenghtWord2:
            lenghtWord1, lenghtWord2 = lenghtWord2, lenghtWord1
            firstWord, secondWord = secondWord, firstWord

        for i in range(-1, lenghtWord1 + 1):
            d[(i, -1)] = i + 1

        for j in range(-1, lenghtWord2 + 1):
            d[(-1, j)] = j + 1

        for i in range(lenghtWord1):
            for j in range(lenghtWord2):
                if firstWord[i] == secondWord[j]:
                    cost = 0
                else:
                    cost = 1
                d[(i, j)] = min(
                    d[(i - 1, j)] + 1,
                    d[(i, j - 1)] + 1,
                    d[(i - 1, j - 1)] + cost
                )
                if i and j and firstWord[i] == secondWord[j - 1] and firstWord[i - 1] == secondWord[j]:
                    d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)

        return d[lenghtWord1 - 1, lenghtWord2 - 1]


    def __find_nearest_word_in_neighboring_words_set(self, input_word: str) -> [bool, str]:
        left_limit = 1
        right_limit = 1
        error_limit = 2

        if len(input_word) <= 1:
            return [False, input_word]
        elif len(input_word) <= 4:
            left_limit = 0
            right_limit = 1
            error_limit = 1
        elif len(input_word) <= 5:
            left_limit = 1
            right_limit = 1
            error_limit = 1

        output_word = input_word
        distance = 100
        for item in self.__neighboring_words_set:
            if datetime.utcnow() > self.__endtime:
                print('Timeout of SentenceCorrector')
                return [False, input_word]

            if ((input_word[0] == item[0] and self.__words_are_similar(input_word, item))
                    and (len(item) >= len(input_word) - left_limit)
                    and (len(item) <= len(input_word) + right_limit)):
                new_distance = self.__calculate_Damerau_Levenshtein_distance(input_word, item)

                if ((new_distance < distance)
                        or (new_distance <= distance and len(item) == len(input_word))):
                    distance = new_distance
                    output_word = item

        if distance > error_limit:
            return [False, input_word]

        self.__update_neighboring_words_set(output_word)
        return [True, output_word]


    def __find_nearest_word_in_set_of_all_words(self, input_word: str) -> [bool, str]:
        left_limit = 1
        right_limit = 1
        error_limit = 2

        if len(input_word) <= 1:
            return [False, input_word]
        elif len(input_word) <= 4:
            left_limit = 0
            right_limit = 1
            error_limit = 1
        elif len(input_word) <= 5:
            left_limit = 1
            right_limit = 1
            error_limit = 1

        output_word = input_word
        distance = 100

        for num in range((len(input_word) - left_limit), (len(input_word) + right_limit)):
            if num in self.__dict_of_all_words_len:
                for item in (self.__dict_of_all_words_len[num]):
                    if datetime.utcnow() > self.__endtime:
                        print('Timeout of SentenceCorrector4')
                        return [False, input_word]

                    if ((input_word[0] == item[0]
                         and self.__words_are_similar(input_word, item))):
                        new_distance = self.__calculate_Damerau_Levenshtein_distance(input_word, item)

                        if ((new_distance < distance)
                                or (new_distance <= distance and len(item) == len(input_word))):
                            distance = new_distance
                            output_word = item

        if distance > error_limit:
            return [False, input_word]

        self.__update_neighboring_words_set(output_word)
        return [True, output_word]


    def check_the_sentence(self, input_sentence : str) -> [bool, str]:
        reg = re.compile('[^а-яА-Я]')
        if len(reg.sub('', input_sentence.lower().strip())) == 0:
            return [False, input_sentence]

        self.__endtime = datetime.utcnow() + timedelta(seconds = 1)

        self.__neighboring_words_set.clear()
        user_sentence_dict = self.__create_dict_of_input_words(input_sentence.strip())

        if not ([user_word for user_word in user_sentence_dict if len(user_word) > 1]):
            return [False, input_sentence]

        if len(user_sentence_dict) == 1:
            if self.__word_is_in_etalon_words_set(input_sentence.strip().lower()):
                return [False, input_sentence]
            return self.__find_nearest_word_in_set_of_all_words(input_sentence.strip().lower())

        not_find_word_without_error = True
        for user_word in user_sentence_dict.keys():
            if len(user_word) == 1:
                user_sentence_dict[user_word] = user_word
            elif self.__word_is_in_etalon_words_set(user_word):
                user_sentence_dict[user_word] = user_word
                not_find_word_without_error = not self.__update_neighboring_words_set(user_word)
            else:
                user_sentence_dict[user_word] = ''

        if not_find_word_without_error:
            for user_word in user_sentence_dict.keys():
                new_word_constr = self.__find_nearest_word_in_set_of_all_words(user_word)

                if new_word_constr[0]:
                    user_sentence_dict[user_word] = new_word_constr[1]
                    not_find_word_without_error = False
                    break

        if not_find_word_without_error:
            return [False, input_sentence]

        for user_word in user_sentence_dict.keys():
            if user_sentence_dict[user_word] == '':
                not_find_new_good_word = True
                new_word_constr = self.__find_nearest_key_word(user_word)

                if new_word_constr[0]:
                    user_sentence_dict[user_word] = new_word_constr[1]
                    not_find_new_good_word = False

                if not_find_new_good_word:
                    new_word_constr = self.__find_splitting_words(user_word)
                    if new_word_constr[0]:
                        user_sentence_dict[user_word] = new_word_constr[1] + ' ' + new_word_constr[2]
                        not_find_new_good_word = False

                if not_find_new_good_word:
                    new_word_constr = self.__find_nearest_word_in_neighboring_words_set(user_word)
                    if new_word_constr[0]:
                        user_sentence_dict[user_word] = new_word_constr[1]

        output_sentence_list = input_sentence.split(' ')
        reg = re.compile('[^а-яА-Я -]')
        error_marker = False

        for user_word in user_sentence_dict.keys():
            if ((user_word.lower() != user_sentence_dict[user_word])
                    and (user_sentence_dict[user_word] != '')):

                for num, item in enumerate(output_sentence_list):
                    item = item.lower()
                    clear_word = reg.sub('', item.strip())
                    if clear_word == user_word:
                        error_marker = True
                        output_sentence_list[num] = item.replace(clear_word, user_sentence_dict[user_word])

        if error_marker:
            return [True, ' '.join(output_sentence_list)]
        return [False, input_sentence]
