#!/usr/local/bin/python3

import os
import sys
import logging
import argparse
import subprocess
from typing import Optional, List
from multiprocessing import cpu_count


NEW_FASTQ_HEADER_PATTERN = r"(?<=^@)[\w\d_-]+:[\d]+:[\w\d]+:[\d]+"
READGROUPS_NUM_THRESHOLD = 10  # Threshold for the number of readgroups in fastq headers. If more, then DEFAULT is used.
DEFAULT_READGROUP = 'DEFAULT:000:READGROUP:1'

LOGGER_FORMAT = "%(name)s | line %(lineno)-3d | %(levelname)-8s | %(message)s"
logger = logging.getLogger(name=__file__)


def set_logger(logger_format: str = LOGGER_FORMAT) -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logger_format))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False


class AddOutputPrefix(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, args: argparse.Namespace,
                 value: str, option_string: Optional[str] = None):
        setattr(args, self.dest, os.path.join(outprefix, value))


def parse_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument('--fastq1', help='Input fastq.gz file, SE or PE pair 1', required=True)
    parser.add_argument('--fastq2', help='Input fastq.gz file, PE pair 2')
    parser.add_argument('--output-basename', help='Output prefix', required=True)
    parser.add_argument('--readgroups-txt', help='Output readgroups.txt file with listed unique readgroups',
                        required=True, action=AddOutputPrefix)
    parser.add_argument('--ignore-warnings', help="In case of inconsistent results ignore warnings. "
                        "Default is 'False'", action='store_true')
    return vars(parser.parse_args())


if __name__ == '__main__':
    set_logger(LOGGER_FORMAT)

    tempdir = os.environ.get("TEMPDIR", "/tmp")
    outprefix = os.environ.get("HOME", "")
    logger.info(f"TEMPDIR = '{tempdir}', OUTPREFIX = '{outprefix}'")

    args = parse_args()
    logger.info(f"Starting program with the folowing arguments: {args}")

    run(**args)
    logger.info("Run is completed successfully.")
