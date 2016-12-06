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
    
def addToWordlist(word, wordlist):
    """Strips any trailing hyphens or apostrophies and adds result to word list"""
    while len(word) > 0 and (word[-1] == "'" or word[-1] == '-'):
        word = word[:-1]
    if word != "":
        wordlist.append(word)
    

def createWordList(text: str):
    """Creates a list of words by finding
    strings which:
    1. start with a letter
    2. contain only letters, apostrophies and hyphens
    3. end with a letter
    
    words are automatically converted to lowercase"""
    wordlist = []
    word = ""
    for char in text:
        if ord(char.upper()) >= ord('A') and ord(char.upper()) <= ord("Z"):
            word = word + char.lower()
        elif (char == '-' or char == "'") and word != "":
            word = word + char
        else:
            addToWordlist(word, wordlist)
            word = ""
    
    addToWordlist(word, wordlist)
    
    return wordlist

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
    for word in common_words:
        if word in word_count:
            del word_count[word]
            
def getMaxWordLength(word_list):
    max_word_length = 0
    for word in word_list:
        if len(word[0]) > max_word_length:
            max_word_length = len(word[0])
    return max_word_length
    
def output(word_list, is_hist):
    """Outputs the list of words"""
    
    normalisation_number = max(floor(log10(word_list[0][1])) - 1, 0)
    max_word_length = getMaxWordLength(word_list)
    for item in word_list:
        string = item[0] + ": "
        if is_hist:
            string = string + " " * (max_word_length - len(item[0]) + 1) + hist(item[1], normalisation_number)   
            
        string = string + " " + str(item[1])
        print (string)

def hist(word_count, normalisation_number):
    hist = ""
    for i in range(word_count):
        if (i + 1) % (10 ** normalisation_number) == 0:
            hist = hist + "|"
    return hist
            
            
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

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
        parser.add_argument('-u', '--uncommon-words', action='store_true', dest='remove_common_words', help="Removes the words which come up frequently in the English language, to illuminate words which are common to the text but not the language in general")
        parser.add_argument('-H', '--histogram', action=('store_true'), dest='is_hist', help="Displays a normalised textual histogram to visualise the frequencies of words")
        parser.add_argument("text")
        
        # Process arguments
        args = parser.parse_args()

        is_file = args.is_file
        number_to_show = int(args.number)
        remove_common_words = args.remove_common_words
        hist = args.is_hist

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
        if remove_common_words:
            #TODO get word list from file (eg https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt)
            #and include user option with -u to specify a number of words to remove.
            # eg -u 100 removes most common 100 words.
            common_words = ["the", "be", "am", "are", "is", "were", "was", "to", "of", "and", "a", "in", "that", "have", "has", "had", "I"]
            removeCommonWords(wordCounter, common_words)
        wordsByFrequency = getWordListFreqOrder(wordCounter, number_to_show)
                                                
        output(wordsByFrequency, hist)
            
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