#!/usr/local/bin/python3.5
# encoding: utf-8
'''
WordFrequencyCounter -- Counts the words in a piece of text and displays the list of most common words and
their corresponding frequencies

WordFrequencyCounter is a short program which counts the words in a piece of text.
This text can be either specified from the command line

@author:     SophieDurrant

@copyright:  2016 Sophie Durrant. All rights reserved.

@license:        This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

@contact:    sgd38@cam.ac.uk
@deffield    updated: Updated 2016-12-06
'''

import sys
import os
import requests
import mimetypes

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from collections import Counter
from math import log10
from math import floor

__all__ = []
__version__ = 0.1
__date__ = '2016-12-06'
__updated__ = '2016-12-06'

DEBUG = 1

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
def addToWordlist(word, wordlist, semi_word_characters):
    """Strips any trailing hyphens or apostrophies and adds result to word list"""
    while len(word) > 0 and (word[-1] in semi_word_characters):
        word = word[:-1]
    if word != "":
        wordlist.append(word)
    

def createWordList(text: str, make_phrase_list = False):
    """Creates a list of words by finding
    strings which:
    1. start with a letter
    2. contain only letters, apostrophies and hyphens
    3. end with a letter
    
    words are automatically converted to lowercase"""
    semi_word_characters = ["'", '-', '’']
    phrase_punctuation = [',', '—', ':', ';', '–', '/', '&', '-']
    wordlist = []
    word = ""
    for char in text:
        if (is_letter(char)) or (is_digit(char)):
            word = word + char.lower()
        elif (char in semi_word_characters) and word != "":
            word = word + char
        else:
            addToWordlist(word, wordlist, semi_word_characters)
            word = ""
        if word == "" and char in phrase_punctuation and make_phrase_list:
            wordlist.append(char)
    
    addToWordlist(word, wordlist, semi_word_characters)
    
    return wordlist

def get_phrases(word_list, min_words):
    phrases = []
    while len(word_list) >= min_words:
        phrase = ""
        for i in range(min_words - 1):
            phrase = phrase + word_list[i] + " "
        
        for word in word_list[min_words - 1:]:
            phrase = phrase + word + " "
            phrases.append(phrase)
        word_list = word_list[1:]
    return phrases

            

def countWords(word_list):
    """Creates a Counter (like a dictionary, but stores the frequency of a key alongside the key)
    which stores the words and their frequency)"""
    word_count = Counter()
    word_count.update(word_list)
    return word_count

def getWordListFreqOrder(word_counter: Counter, n: int):
    """Gets a n-length list of words sorted by their frequency"""
    if n == 0:
        word_list = word_counter.most_common()
    else:
        word_list = word_counter.most_common(n)
    
    return word_list

def removeCommonWords(word_count, common_words):
    """removes the common words, as defined by the list common_words, from the Counter word_count"""
    for word in common_words:
        if word in word_count:
            del word_count[word]
            
def getLongestWordLength(word_list):
    """Gets the length of the longest word"""
    max_word_length = 0
    for word in word_list:
        if len(word[0]) > max_word_length:
            max_word_length = len(word[0])
    return max_word_length

def getCommonWords(r: requests.Response, count = 0, includeFreq = False, start = 0):
    """Gets a list of common words from a url containing  a text file with them"""   
    common_word_list = []
    line_no = 0
    for line in r.iter_lines():
        if line_no >= start and line_no < start + count:
            line = line.decode('utf-8')
            splitline = line.split("\t")
            splitline[0] = splitline[0].lower()
            if len(splitline[0]) > 1 or splitline[0] == "i" or splitline[0] == "a":
                if includeFreq:
                    common_word_list.append(splitline)
                else:
                    common_word_list.append(splitline[0])
        line_no = line_no + 1
        
        if line_no >= (start + count):
            break           
    return common_word_list

def getSentences(text):
    """Gets sentences in a text file."""
    sentences = []
    sentence = text[0]
    for i in range(1, len(text) - 1):
        prev = text[i - 1]
        curr = text[i]
        next = text[i + 1]
        if end_of_sentence(prev, curr, next):
            if len(sentence) > 0:
                sentences.append(sentence)
                sentence = ""
        else:
            sentence = sentence + curr
        
    sentence = sentence + text[len(text) - 1]
    sentences.append(sentence)
    return sentences


    
        
        
def is_digit(char):
    return ord(char) >= ord("0") and ord(char) <= ord("9")

def is_letter(char):
    uchar = char.upper()
    return ord(uchar) >= ord('A') and ord(uchar) <= ord("Z")

def end_of_sentence(prev, curr, next):
    if curr == '\n' or curr == "!" or curr == '?':
        return True
    elif curr == '.' and not(is_digit(prev) and  is_digit(next)):
        return True
    else: return False

def getRequest(url):
    #This module features two security checks:
    #1. The file seems like a plaintext file.
    #2. The file says it's a plaintext file.
    #This should help mitigate an attack of a malicious binary url being passed to the program
    plaintext_mime = "text/plain"
    guessed_type = mimetypes.guess_type(url) #This finds the guessed type of the url file
    if guessed_type[0] == plaintext_mime:
        r = requests.get(url, stream=True)
        content_type = r.headers['content-type'] #this finds the stated type of the url file        
        content_type = content_type.split(";")
        if content_type[0] == plaintext_mime:
            #If both checks pass, then returns the request
            return r
        else:
            raise Exception
    
def getNormalisationNumber(word_list):
        return max(floor(log10(int(word_list[0][1]))) - 1, 0)
    
def align_hist(word, max_word_length):
    return " " * (max_word_length - len(word) + 1)

def generate_hist_string(word, count, max_word_length, norm_number):
    alignment = align_hist(word, max_word_length)
    histogram = hist(count, norm_number)
    return  alignment + histogram


def output(word_list, is_hist, show_count = True):
    """Outputs the list of words"""
    normalisation_number = getNormalisationNumber(word_list)
    max_word_length = getLongestWordLength(word_list)
    for item in word_list:
        string = item[0] + ": "
        if is_hist:
            string = string + generate_hist_string (item[0], int(item[1]), max_word_length, normalisation_number)
         
        if show_count:   
            string = string + " " + str(item[1])
        print (string)

def hist(count, normalisation_number: int):
    hist = "|" * floor(count / (10 ** normalisation_number))
    return hist      
            
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    
    false_default = -1
    url = "https://raw.githubusercontent.com/SophieDurrant/WordFrequencyCount/master/count_1w100k.txt"

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

      This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
''' + str((program_shortdesc, str(__date__)))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-f", "--filename", default='', dest="is_file", action="store_true", help="Counts the words in the specified file [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-n', '--number', action='store', default=10, dest='number', help="Number of words to display. Most common words will be shown first. Set -n to 0 to show all words. [default: %(default)s]")
        parser.add_argument('-u', '--uncommon-words', action='store', nargs = '?', default = false_default, const = 20, dest='remove_common_words', help="""Removes the words which come up frequently in the English language, to illuminate words which are common to the text but not the language in general.
            The user can specify an argument to state the number of words excluded.
            The default argument is 10. If the user inputs 0, all words from the url are excluded.""")
        parser.add_argument('-H', '--histogram', action=('store_true'), dest='is_hist', help="Displays a normalised textual histogram to visualise the frequencies of words")
        parser.add_argument('-c', '--compare', action='store_true', dest='compare', help='Displays a list of the most common words in order, so you can compare your text to the English language average.')
        parser.add_argument('-p', '--phrases', action='store', dest='phrases', nargs = "?", default = 0, const = 2, help='Analyse the text to reveal the most common phrases, with the argument being the minimum number of words in a phrase')
        parser.add_argument("text")
        
        # Process arguments
        args = parser.parse_args()

        is_file = args.is_file
        number_to_show = int(args.number)
        wordsToRemove = int(args.remove_common_words)
        is_hist = args.is_hist
        compare = args.compare
        use_phrases = int(args.phrases)
        
        #only get the request if it's going to be used
        if wordsToRemove > false_default or compare:
            request = getRequest(url)

        if is_file:      
            filename = args.text
            if os.path.isfile(filename):
                f = open(filename, 'r')
                text = f.read()
                f.close()
            else:
                print("FATAL ERROR: File does not exist")
                return 2
        else:
            text = args.text
            
        wordCounter =   countWords(createWordList(text))
        if wordsToRemove > false_default:
            #TODO get word list from file (eg https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt)
            #current word list is inspired by the wikipedia article https://en.wikipedia.org/wiki/Most_common_words_in_English
            #and include user option with -u to specify a number of words to remove.
            # eg -u 100 removes most common 100 words.
            common_words = getCommonWords(request, wordsToRemove)            
            removeCommonWords(wordCounter, common_words)
        wordsByFrequency = getWordListFreqOrder(wordCounter, number_to_show)
                                                
        output(wordsByFrequency, is_hist)
        
        if args.compare:
            if number_to_show > 0:
                number_of_words = number_to_show
            else:
                number_of_words = len(wordCounter)
                
            
            if wordsToRemove > 0:
                common_words = getCommonWords(request, number_of_words + wordsToRemove, True)
                common_words = common_words[wordsToRemove:]
            else:
                common_words = getCommonWords(request, number_to_show, True)
                    
            print()
            print("Reference:")
            output(common_words, is_hist, True)
                 
        if use_phrases > 0:
            print()
            print("Phrases")
            sentences = getSentences(text)
            commonPhrases = Counter()
            for sentence in sentences:
                wordList = createWordList(sentence)
                phrases = get_phrases(wordList, use_phrases)
                commonPhrases.update(phrases)
            most_common_phrases = getWordListFreqOrder(commonPhrases, number_to_show)
            output(most_common_phrases, is_hist, True)
                
            
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG == 1:
            raise e
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())