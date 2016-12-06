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
__version__ = 0.2
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
    
class SecurityError(Exception):
    '''Exception which shows that there was an error in parsing the webpage,
    such , which indicates that the URL does not contain a text file. 
    THis could represent an error in inputting the URL, or indicatethat the webpage is acting maliciously'''
    def __init__(self, msg):
        super(SecurityError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
def addToWordlist(word, wordlist, semi_word_characters):
    """Strips any trailing hyphens or apostrophies and adds result to word list
    
    word is a word
    wordlist is a list of words
    semi_word_characters is a list of characters which are considered to be part of a word
    if surrounded by letters but not if on their own."""
    while len(word) > 0 and (word[-1] in semi_word_characters):
        word = word[:-1]
    if word != "":
        wordlist.append(word)
    

def createWordList(text: str):
    """Creates a list of words by finding
    strings which:
    1. start with a letter
    2. contain only letters, apostrophies and hyphens
    3. end with a letter
    
    words are automatically converted to lowercase.
    
    text: the text to be analysed"""
    semi_word_characters = ["'", '-', '’']
    wordlist = []
    word = ""
    for char in text:
        if (isLetter(char)) or (isDigit(char)):
            word = word + char.lower()
        elif (char in semi_word_characters) and word != "":
            word = word + char
        else:
            addToWordlist(word, wordlist, semi_word_characters)
            word = ""
    
    addToWordlist(word, wordlist, semi_word_characters)
    
    return wordlist

def getPhrases(word_list, min_words):
    """Gets a list of phrases in a word list.
    A phrase is defined as a combination of words in sequential order,
    of a number of words longer than min_words.
    
    word_list is a list of words.
    min_words is an int representing the minimum number of words in a phrase."""
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
    which stores the words and their frequency)
    
    word_list is a list of words."""
    word_count = Counter()
    word_count.update(word_list)
    return word_count

def getWordCounterFreqOrder(word_counter: Counter, n: int):
    """Gets a n-length list of words sorted by their frequency.
    
    word_counter is a Counter
    n is an int."""
    if n == 0:
        word_list = word_counter.most_common()
    else:
        word_list = word_counter.most_common(n)
    
    return word_list

def removeCommonWords(word_count, common_words):
    """removes the common words, as defined by the list common_words, from the Counter word_count
    
    word_count is a Counter object.
    common_words is a list."""
    for word in common_words:
        if word in word_count:
            del word_count[word]
            
def getLongestWordLength(word_list):
    """Gets the length of the longest word in the word_list.
    word_list is a list of 2-tuple where word[0] is a string."""
    max_word_length = 0
    for word in word_list:
        if len(word[0]) > max_word_length:
            max_word_length = len(word[0])
    return max_word_length

def getCommonWordList(r, count = 0, includeFreq = False, start = 0):
    """Gets a list of common words from a response object containing a common-words file.
    
    r: a response object obtained from getRequest.
    count: the number of words to fetch
    includeFreq: if the output should be a list of 2-tuple,
        where common_word_list[][1] is the frequency of the word in
        common_word_list[][0]
    start: the line to start at (0-based)
    """   
    common_word_list = []
    line_no = 0
    for line in r.iter_lines():
        if line_no >= start and line_no < start + count:
            line = line.decode('utf-8')
            
            #splits the line into word and frequency
            splitline = line.split("\t") 
            splitline[0] = splitline[0].lower()
            
            #Filters out the single letters which seem to appear in the text file
            if len(splitline[0]) > 1 or splitline[0] == "i" or splitline[0] == "a":
                if includeFreq:
                    common_word_list.append(splitline)
                else:
                    common_word_list.append(splitline[0])
                    
        line_no = line_no + 1
        
        #ends if all the required words have been read
        if line_no >= (start + count):
            break           
    return common_word_list

def getSentences(text):
    """Gets sentences in a text file. A sentence is a series of letters ending with a new line,
    a question mark or an exclamation mark, or a full stop, assuming that the full stop isn't already
    part of a decimal number.
    
    text is the text to be analysed."""
    sentences = []
    sentence = text[0]
    for i in range(1, len(text) - 1):
        prev = text[i - 1]
        curr = text[i]
        next = text[i + 1]
        if endOfSentence(prev, curr, next):
            if len(sentence) > 0:
                sentences.append(sentence)
                sentence = ""
        else:
            sentence = sentence + curr
        
    sentence = sentence + text[len(text) - 1]
    sentences.append(sentence)
    return sentences
    
def isDigit(char):
    """Checks if the character is a digit"""
    return ord(char) >= ord("0") and ord(char) <= ord("9")

def isLetter(char):
    """checks if the character is a letter"""
    lchar = char.lower()
    return ord(lchar) >= ord('a') and ord(lchar) <= ord("z")

def endOfSentence(prev, curr, next):
    """Checks if the sentence has ended.
    
    The definition of the end of a sentence is:
    The current character is '\n', "!", '?'
    Or the current character is '.' and not between two digits.
    
    prev = previous character in text
    curr = current character in text
    next = next character in text"""
    if curr == '\n' or curr == "!" or curr == '?':
        return True
    elif curr == '.' and not(isDigit(prev) and  isDigit(next)):
        return True
    else: return False

def getRequest(url):
    """Does some security checks on the url, and if they pass, then it gets the url
    and returns the Response object
    #This module features two security checks:
    #1. The file seems like a plaintext file.
    #2. The file says it's a plaintext file.
    #This should help mitigate an attack of a malicious binary url being passed to the program
    
    url: a string of the url pointing to the file to be used"""
    plaintext_mime = "text/plain"
    guessed_type = mimetypes.guess_type(url)[0] #This finds the guessed type of the url file
    if guessed_type == plaintext_mime:
        r = requests.get(url, stream=True)
        #this finds the stated type of the url file
        content_type = r.headers['content-type'].split(";")[0]         
        if content_type == plaintext_mime:
            #If both checks pass, then returns the request
            return r
        else:
            raise SecurityError("Stated content-type and actual content-type do not match")
    else:
        raise SecurityError("Webpage is not a plaintext file")
    
def getNormalisationNumber(word_list):
    """Returns a number which states the factor by which to shrink the histogram bar
    This is defined as one less than the number of digits in the count of the largest word.
    This ensures that the length of the largest histogram is no larger than 99 characters.
    10^normalisationNumber represents the number of occurences per pipe symbol in the histogram.

    If the largest number of words is a single-digit number then the normalisation factor is set to 0.
    
    word_list is a list of 2-tuple. word_list[x][1] must be an integer.
    """
    if len(word_list) == 0:
        return 0
    else:
        return max(floor(log10(int(word_list[0][1]))) - 1, 0)
    
def alignHist(word, max_word_length):
    """Returns the number of spaces which should be between the word and the histogram
    This ensures that every histogram starts in the same place.
    
    word: a string representing a single word
    max_word_length: length of longest word in text"""
    return " " * (max_word_length - len(word) + 1)

def generateHistString(word, count, max_word_length, norm_number):
    """Generates a string corresponding to a single bar of the histogram
    Variables:
    word: a string representing a single word
    count: number of times word occurs in text
    max_word_length: length of longest word in text
    norm_number: normalisation number"""
    alignment = alignHist(word, max_word_length)
    histogram = createHist(count, norm_number)
    return  alignment + histogram


def output(word_list, is_hist, show_count = True):
    """Outputs the list of words, in order of max frequency to min frequency.
    
    word_list: words to be outputted. this is a 2-tuple list where word_list[][0] is a word and
    word_list[1] represents an int.
    
    is_hist: if a histogram should be outputted.
    show_count: if the word count should be outputted."""
    normalisation_number = getNormalisationNumber(word_list)
    max_word_length = getLongestWordLength(word_list)
    for item in word_list:
        string = item[0] + ": "
        if is_hist:
            string = string + generateHistString (item[0], int(item[1]), max_word_length, normalisation_number)
         
        if show_count:   
            string = string + " " + str(item[1])
        print (string)

def createHist(count, normalisation_number: int):
    """Creates a histogram bar based on the count and the normalisation
    
    See above for info on normalisation."""
    createHist = "|" * floor(count / (10 ** normalisation_number))
    return createHist      
            
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    
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
        parser.add_argument('-u', '--uncommon-words', action='store', nargs = '?', default = 0, const = 20, dest='remove_common_words', help="""Removes the words which come up frequently in the English language, to illuminate words which are common to the text but not the language in general.
            The user can specify an argument to state the number of words excluded.
            The default argument is 10.""")
        parser.add_argument('-H', '--histogram', action='store_true', dest='is_hist', help="Displays a normalised textual histogram to visualise the frequencies of words")
        parser.add_argument('-c', '--use_compare', action='store_true', dest='use_compare', help='Displays a list of the most common words in order, so you can use_compare your text to the English language average.')
        parser.add_argument('-p', '--phrases', action='store', dest='phrases', nargs = "?", default = 0, const = 2, help='Analyse the text to reveal the most common phrases, with the argument being the minimum number of words in a phrase')
        parser.add_argument('-v', '--verbose', action = 'store_true', dest='verbose', help='Program is_verbose')
        parser.add_argument("text")
        
        # Process arguments
        args = parser.parse_args()

        is_file = args.is_file
        words_to_show = int(args.number)
        words_to_remove = int(args.remove_common_words)
        is_hist = args.is_hist
        use_compare = args.use_compare
        words_in_phrase = int(args.phrases)
        is_verbose = args.verbose
        
        #only get the request if it's going to be used
        if words_to_remove > 0 or use_compare:
            request = getRequest(url)
            
        #reads the file
        if is_file:      
            filename = args.text
            if os.path.isfile(filename):
                #Solves a problem involving windows compatibility.
                #if program can't be decoded in utf-8, try decoding it in ISO-8859-1
                try:
                    f = open(filename, 'r')
                    text = f.read()
                except UnicodeDecodeError:
                    f = open(filename, 'r', encoding="ISO-8859-1")
                    text = f.read()
                f.close()
            else:
                print("FATAL ERROR: File does not exist")
                return 2
        else:
            text = args.text
        
        #creates an object which stores a set of words and their frequency
        wordCounter =   countWords(createWordList(text))
        
        #removes most common words from above counter if this option is specified.
        if words_to_remove > 0:
            common_words = getCommonWordList(request, words_to_remove)            
            removeCommonWords(wordCounter, common_words)
        
        #sorts the words by frequency
        wordsByFrequency = getWordCounterFreqOrder(wordCounter, words_to_show)
                                                
        output(wordsByFrequency, is_hist)
        
        #creates a comparasion word frequency output if the user specifies
        if use_compare:
            
            #finds the number of words, n, which will be displayed in the output
            if words_to_show > 0:
                n = words_to_show
            else:
                n = len(wordCounter)
                
            #if there are common words which have been removed,
            #get a word list containing the most common words which haven't been removed
            #otherwise get a list of the most common words.
            if words_to_remove > 0:
                common_words = getCommonWordList(request, words_to_remove, True, n)
            else:
                common_words = getCommonWordList(request, includeFreq= True, count= n)
                    
            print()
            print("Reference:")
            output(common_words, is_hist, True)
        
        #Processes the phrases of the text and finds the most frequently used phrases
        #if the phrases option has been specified.
             
        if words_in_phrase > 0:
            print()
            print("Phrases")
            sentences = getSentences(text)
            
            #creates a counter and updates the counter with the list of phrases for each sentence.
            phrase_counter = Counter()
            for sentence in sentences:
                wordList = createWordList(sentence)
                phrases = getPhrases(wordList, words_in_phrase)
                phrase_counter.update(phrases)
            
            #gets the most common phrases from the counter and outputs this result    
            most_common_phrases = getWordCounterFreqOrder(phrase_counter, words_to_show)
            output(most_common_phrases, is_hist, True)
        
        if is_verbose:
            print("done")
            
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