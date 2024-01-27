# rgsplitter
rgsplitter - Illumina FastQ Read Group Splitter

# README.md for `rgsplitter` tool

## Overview
This repository contains a Docker component `rgsplitter`, a Python script designed to split Illumina FastQ files by read groups. It's optimized for handling large datasets and provides a user-friendly command-line interface for bioinformatics data processing.

## Features
- **Read Group Splitting**: Automatically identifies and segregates read groups within FastQ files, a crucial feature for multiplexed sequencing data.
- **Efficient Data Handling**: Optimized for large FastQ files, ensuring quick processing times and low memory usage.
- **User-Friendly Interface**: Simple command-line interface with clear argument requirements.
- **Quality Control**: Implements checks for data consistency after processing.

## Requirements
- Docker environment.

## Installation and Setup
1. **Clone the Repository**:
   ```bash
   git clone git@github.com:Genebio/rgsplitter.git
   ```
2. **Build the Docker Image**:
   Assuming the Dockerfile is in the same directory:
   ```bash
   docker build -t rgsplitter:1.0.0 .
   ```

## Usage
To run the script within a Docker container, use the following command:
```bash
docker run --rm -it \
    -v [local-directory-path]:/mnt \
    rgsplitter:1.0.0 \
    --fastq1 /mnt/[fastq-file-1] \
    --fastq2 /mnt/[fastq-file-2] \
    --output-basename /mnt/[output-basename] \
    --readgroups-txt /mnt/[readgroups-txt-file]
```
Replace `[local-directory-path]`, `[fastq-file-1]`, `[fastq-file-2]`, `[output-basename]`, and `[readgroups-txt-file]` with your specific file paths and names.

### Command-line Arguments
- `--fastq1`: Path to the input fastq.gz file (SE or PE pair 1).
- `--fastq2`: Path to the input fastq.gz file (PE pair 2), if applicable.
- `--output-basename`: The output prefix for processed files.
- `--readgroups-txt`: Path to the output file listing unique readgroups.
- `--ignore-warnings`: Option to ignore warnings in case of inconsistent results.

## Troubleshooting and Support
For issues and questions regarding the use of this tool, please refer to the issue tracker in the GitHub repository or contact genebio91@gmail.com.

## Contribution
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## Usage example on small test fastq files

```bash
docker run --rm -it \
    -v $(pwd)/test/:/mnt \
    rgsplitter:1.0.0 \
    --fastq1 /mnt/RNASeq-tumor_1k_1.fastq.gz \
    --fastq2 /mnt/RNASeq-tumor_1k_2.fastq.gz \
    --output-basename /mnt/RNASeq-tumor \
    --readgroups-txt /mnt/RNASeq-tumor-readgroups.txt
```
### Log Output

- `/usr/local/src/run.py | line 189 | INFO | TEMPDIR = '/tmp', OUTPREFIX = '/root'`
- `/usr/local/src/run.py | line 192 | INFO | Starting program with the following arguments: {'fastq1': '/mnt/RNASeq-tumor_1k_1.fastq.gz', 'fastq2': '/mnt/RNASeq-tumor_1k_2.fastq.gz', 'output_basename': '/mnt/RNASeq-tumor', 'readgroups_txt': '/mnt/RNASeq-tumor-readgroups.txt', 'ignore_warnings': False}`
- `/usr/local/src/run.py | line 165 | INFO | '/mnt/RNASeq-tumor-readgroups.txt' file content: ['A01231:742:HHMCWDRX3:1', 'A01231:742:HHMCWDRX3:2']`
- `/usr/local/src/run.py | line 124 | INFO | Splitting /mnt/RNASeq-tumor_1k_1.fastq.gz by 'A01231:742:HHMCWDRX3:1'...`
- `/usr/local/src/run.py | line 56  | INFO | Running the following subprocess command: 'seqkit grep -rp ^A01231:742:HHMCWDRX3:1 -j 8 -o /mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:1_1.fastq.gz /mnt/RNASeq-tumor_1k_1.fastq.gz'`
- `/usr/local/src/run.py | line 127 | INFO | Successfully splitted '/mnt/RNASeq-tumor_1k_1.fastq.gz' by 'A01231:742:HHMCWDRX3:1' to '/mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:1_1.fastq.gz'`
- `/usr/local/src/run.py | line 124 | INFO | Splitting /mnt/RNASeq-tumor_1k_2.fastq.gz by 'A01231:742:HHMCWDRX3:1'...`
- `/usr/local/src/run.py | line 56  | INFO | Running the following subprocess command: 'seqkit grep -rp ^A01231:742:HHMCWDRX3:1 -j 8 -o /mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:1_2.fastq.gz /mnt/RNASeq-tumor_1k_2.fastq.gz'`
- `/usr/local/src/run.py | line 127 | INFO | Successfully splitted '/mnt/RNASeq-tumor_1k_2.fastq.gz' by 'A01231:742:HHMCWDRX3:1' to '/mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:1_2.fastq.gz'`
- `/usr/local/src/run.py | line 124 | INFO | Splitting /mnt/RNASeq-tumor_1k_1.fastq.gz by 'A01231:742:HHMCWDRX3:2'...`
- `/usr/local/src/run.py | line 56  | INFO | Running the following subprocess command: 'seqkit grep -rp ^A01231:742:HHMCWDRX3:2 -j 8 -o /mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:2_1.fastq.gz /mnt/RNASeq-tumor_1k_1.fastq.gz'`
- `/usr/local/src/run.py | line 127 | INFO | Successfully splitted '/mnt/RNASeq-tumor_1k_1.fastq.gz' by 'A01231:742:HHMCWDRX3:2' to '/mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:2_1.fastq.gz'`
- `/usr/local/src/run.py | line 124 | INFO | Splitting /mnt/RNASeq-tumor_1k_2.fastq.gz by 'A01231:742:HHMCWDRX3:2'...`
- `/usr/local/src/run.py | line 56  | INFO | Running the following subprocess command: 'seqkit grep -rp ^A01231:742:HHMCWDRX3:2 -j 8 -o /mnt/RNASeq-tumor-A01231:742:HHMCWDRX3:2_2.fastq.gz /mnt/RNASeq-tumor_1k_2.fastq`
- `/usr/local/src/run.py | line 81  | INFO     | Checking if '/mnt/RNASeq-tumor_1k_1.fastq.gz' is consistent...`
- `/usr/local/src/run.py | line 93  | INFO     | Consistency check passed for '/mnt/RNASeq-tumor_1k_1.fastq.gz'`
- `/usr/local/src/run.py | line 81  | INFO     | Checking if '/mnt/RNASeq-tumor_1k_2.fastq.gz' is consistent...`
- `/usr/local/src/run.py | line 93  | INFO     | Consistency check passed for '/mnt/RNASeq-tumor_1k_2.fastq.gz'`
- `/usr/local/src/run.py | line 175 | INFO     | Consistency check passed for all input fastq files.`
- `/usr/local/src/run.py | line 196 | INFO     | Run completed successfully.`
