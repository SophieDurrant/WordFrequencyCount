This project is a program designed to count the frequency of words in a text file or in the argument.

#Example:
Using an input file containing the GNU GPL:

Input: `-Hf ~/gnu_gpl3.txt`

Output:
```
the:      |||||||||||||||||||||||||||||||||| 345
of:       |||||||||||||||||||||| 221
to:       |||||||||||||||||| 189
a:        |||||||||||||||||| 184
or:       ||||||||||||||| 151
you:      |||||||||||| 128
license:  |||||||||| 102
and:      ||||||||| 98
work:     ||||||||| 95
that:     ||||||||| 91
```

#Motivation:
Project came up as a tool to detect repetitive words in speeches and essays.

#Installation:
1. Download WordFrequencyCounter.py file (file is a standalone .py file)
2. Run python3 /path/to/file arguments

#Arguments:
The program takes one positional argument.
If -f is specified, the positional argument is the path to a file
If -f is not specified, the positional argument is the text to be analysed.

##Optional arguments:
-h --help: shows help text
-f --filename: input is a path to a file rather than the text to be analysed
-V --version: prints version number
-n --number: display the number of words of the following argument. The default is 10 words.
            Write -n 0 to show all words.
-u --uncommon-words: remove the most common words in the English language from the output.
		Specify a number to specify the number of words to be removed
-c --compare Use this flag to enable comparasion with most common words
-H --histogram: displays a histogram to visualise the distribution of words.

#License:
 ```
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
```
 
#Potential improvements:
 1. The ability to display most common phrases (groups of two or more words) as well as words.
 2. Grab a list of most common words from a file on the Web (eg https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt) 
 and allow the user to specify the number of words to remove
 3. Improve histogram readibility
 
 #Other Notices:
 The file count_1w100k.txt was put together by Peter Norvig from http://norvig.com/ngrams/ .
