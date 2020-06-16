#!/usr/bin/env python3

import argparse
import os
import re
import zipfile

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriverdownloader import GeckoDriverDownloader

"""
Script to extract a subsequence from a given DNA sequence.


Copyright 2020 Margherita Maria Ferrari.


This file is part of SequenceExtractor.

SequenceExtractor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SequenceExtractor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SequenceExtractor.  If not, see <http://www.gnu.org/licenses/>.
"""


class SequenceExtractor:
    __BROWSER = None
    DNA_MAPPING = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C'
    }

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Extract subsequence')
        parser.add_argument('-i', '--input-file', metavar='INPUT_FILE', type=str, required=True,
                            help='File containing DNA sequence info with coordinates in BED format (0-based exclusive)',
                            default=None)
        parser.add_argument('-o', '--output-file', metavar='OUTPUT_FILE', type=str, required=True,
                            help='Output file with coordinates in 1-based inclusive system', default='output.fa')
        parser.add_argument('-f', '--input-file-format', metavar='INPUT_FILE_FORMAT', type=str, required=True,
                            choices=('fasta', 'tsv'), help='Input file format', default='tsv')
        parser.add_argument('-min', '--min-length', metavar='MIN_LENGTH', type=int, required=False,
                            help='Minimum subsequence length', default=1)
        parser.add_argument('-max', '--max-length', metavar='MAX_LENGTH', type=int, required=False,
                            help='Maximum subsequence length', default=1000)
        parser.add_argument('-p', '--prefix-length', metavar='PREFIX_LENGTH', type=int, required=False,
                            help='Length of the prefix to be added to subsequence', default=0)
        parser.add_argument('-s', '--suffix-length', metavar='SUFFIX_LENGTH', type=int, required=False,
                            help='Length of the suffix to be added to subsequence', default=0)
        parser.add_argument('-d', '--folder', metavar='FOLDER', type=str, required=True,
                            help='Folder with full sequences. File names format is "<SEQUENCE_NAME>_sequences.fasta"',
                            default='.')

        return parser.parse_args()

    @classmethod
    def __init_browser(cls, download_folder):
        if cls.__BROWSER is None:
            webdriver_path = os.path.join(os.path.expanduser('~'), '.webdriver')
            gdd = GeckoDriverDownloader(download_root=webdriver_path, link_path=os.path.join(webdriver_path, 'bin'))
            geckodriver_path = gdd.download_and_install()[0]

            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.download.dir', os.path.abspath(download_folder))
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-gzip;application/zip')

            options = Options()
            options.headless = True

            # driver = webdriver.Firefox(firefox_binary=FirefoxBinary('F:\\FirefoxPortable\\Firefox.exe'),
            #                            firefox_profile=profile, options=options, executable_path=geckodriver_path)
            cls.__BROWSER = webdriver.Firefox(firefox_profile=profile, options=options,
                                              executable_path=geckodriver_path, service_log_path=os.devnull)
            cls.__BROWSER.set_window_size(1920, 1080)

    @classmethod
    def __destroy_browser(cls):
        if cls.__BROWSER is not None:
            cls.__BROWSER.quit()
            cls.__BROWSER = None

    @classmethod
    def __extract_sequence(cls, line, input_format, prefix_len, suffix_len, folder):
        name = ''
        start = 0
        end = 0

        if input_format == 'fasta':
            if not line.startswith('>'):
                return name, start, end

            line = line.strip('>')
            pattern = re.compile(r'[\w\d\-_]+:[\d]+-[\d]+')

            for i in pattern.findall(line):
                name = i.split(':')[0]
                start = int(i.split(':')[1].split('-')[0]) - prefix_len
                end = int(i.split(':')[1].split('-')[1]) + suffix_len
                break
        elif input_format == 'tsv':
            parts = line.split('\t')

            if len(parts) < 3:
                raise AssertionError('')

            name = parts[0]
            start = int(parts[1]) - prefix_len
            end = int(parts[2]) + suffix_len
        else:
            raise AssertionError('')

        seq = cls.__download_sequence(name, folder)

        if start < 0:
            start = 0

        if end > len(seq):
            end = len(seq)

        return seq, name, start, end

    @classmethod
    def __download_sequence(cls, seq_name, folder):
        if not os.path.isfile(os.path.abspath(os.path.join(folder, seq_name + '.zip'))) and \
                not os.path.isfile(os.path.abspath(os.path.join(folder, seq_name + '_sequences.fasta'))):
            cls.__init_browser(folder)
            wait = WebDriverWait(cls.__BROWSER, 30)
            cls.__BROWSER.get('https://knot.math.usf.edu/mds_ies_db/search.php?q=' + seq_name)

            # if seq_name not in cls.__BROWSER.title:
            #     raise AssertionError('')

            elem = cls.__BROWSER.find_element_by_id('downloadList')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_xpath(
                '//button[@type="button" and @data-toggle="dropdown" and @data-id="download-select"]')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_xpath('//span[text()="' + seq_name + '"]')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_xpath(
                '//button[@type="button" and @data-toggle="dropdown" and @data-id="download-select"]')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_id('deselectAll_btn')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_name('seq_nuc')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_xpath(
                '//input[@type="radio" and @name="seq_type" and @value="fasta"]')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()
            elem = cls.__BROWSER.find_element_by_id('downloadBtn')
            wait.until(expected_conditions.visibility_of(elem))
            elem.click()

        if not os.path.isfile(os.path.abspath(os.path.join(folder, seq_name + '_sequences.fasta'))):
            if not os.path.isfile(os.path.abspath(os.path.join(folder, seq_name + '.zip'))):
                raise AssertionError('')

            with zipfile.ZipFile(os.path.abspath(os.path.join(folder, seq_name + '.zip')), 'r') as fin:
                fin.extractall(os.path.abspath(folder))

        seq = ''
        with open(os.path.join(os.path.abspath(folder), seq_name + '_sequences.fasta'), 'r') as fin:
            # ignore first line (fasta header)
            fin.readline()

            seq_part = fin.readline()
            while seq_part != '' and seq_part is not None:
                seq += seq_part.strip()
                seq_part = fin.readline()

        if len(seq) < 1:
            raise AssertionError('')

        return seq

    @classmethod
    def extract_sequences(cls, in_file, input_format='fasta', prefix_len=0, suffix_len=0, min_len=1, max_len=1000,
                          folder='.', out_file='output.fa'):
        names = list()
        first_save = True

        with open(in_file, 'r') as fin:
            line = fin.readline()

            while line:
                line = line.strip()

                if len(line) < 1:
                    line = fin.readline()
                    continue

                seq, name, start, end = cls.__extract_sequence(line, input_format, prefix_len, suffix_len, folder)

                if not name or end - start < min_len or end - start > max_len:
                    line = fin.readline()
                    continue

                subseq = seq[start:end]
                subseq_rev_compl = ''

                for i in range(len(subseq) - 1, -1, -1):
                    subseq_rev_compl += cls.DNA_MAPPING.get(subseq[i].upper(), '_')

                open_mode = 'w' if first_save else 'a'
                first_save = False

                with open(out_file, open_mode) as fout:
                    tmp_name = name
                    if tmp_name in names:
                        i = 1
                        tmp_name = name + '-' + str(i)
                        while tmp_name in names:
                            i += 1
                            tmp_name = name + '-' + str(i)
                    names.append(tmp_name)
                    fout.write('>' + tmp_name + ' range=' + tmp_name + ':' + str(start + 1) + '-' + str(end) +
                               ' 5\'pad=0 3\'pad=0 strand=+ repeatMasking=none\n')
                    fout.write(subseq + '\n')
                    fout.write('>' + tmp_name + '_rev_compl' + ' range=' + tmp_name + '_rev_compl' + ':' +
                               str(len(seq) - end + 1) + '-' + str(len(seq) - start) +
                               ' 5\'pad=0 3\'pad=0 strand=+ repeatMasking=none\n')
                    fout.write(subseq_rev_compl + '\n')

                line = fin.readline()
        cls.__destroy_browser()


if __name__ == '__main__':
    args = vars(SequenceExtractor.get_args())
    SequenceExtractor.extract_sequences(args.get('input_file', None), args.get('input_file_format', 'tsv'),
                                        args.get('prefix_length', 0), args.get('suffix_length', 0),
                                        args.get('min_length', 1), args.get('max_length', 1000),
                                        args.get('folder', '.'), args.get('output_file', 'output.fa'))
