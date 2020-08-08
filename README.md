# Sequence Extractor

### Description
Extract MIC subsequences from the [`<mds_ies_db>`](https://knot.math.usf.edu//mds_ies_db).

Input file must contain coordinates in BED format, while the output will use 1-based coordinates system.


### Usage
```text
usage: sequence_extractor.py [-h] -i INPUT_FILE -o OUTPUT_FILE -f
                             INPUT_FILE_FORMAT [-min MIN_LENGTH]
                             [-max MAX_LENGTH] [-p PREFIX_LENGTH]
                             [-s SUFFIX_LENGTH] -d FOLDER

Extract subsequence

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        File containing DNA sequence info with coordinates in
                        BED format (0-based exclusive)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output file with coordinates in 1-based inclusive
                        system
  -f INPUT_FILE_FORMAT, --input-file-format INPUT_FILE_FORMAT
                        Input file format
  -min MIN_LENGTH, --min-length MIN_LENGTH
                        Minimum subsequence length
  -max MAX_LENGTH, --max-length MAX_LENGTH
                        Maximum subsequence length
  -p PREFIX_LENGTH, --prefix-length PREFIX_LENGTH
                        Length of the prefix to be added to subsequence
  -s SUFFIX_LENGTH, --suffix-length SUFFIX_LENGTH
                        Length of the suffix to be added to subsequence
  -d FOLDER, --folder FOLDER
                        Folder with full sequences. File names format is
                        "<SEQUENCE_NAME>_sequences.fasta"
```
