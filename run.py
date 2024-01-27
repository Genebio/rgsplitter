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


def exit_with_error(message: Optional[str]) -> None:
    if message is None:
        message = "Empty message for error!"
    logger.critical(message)
    sys.exit(1)


def run_command(cmd: List[str], exit_message: Optional[str] = None) -> None:
    logger.info(f"Running the following subprocess command: '{' '.join(cmd)}'")
    result = subprocess.run(cmd)
    if result.returncode:
        exit_with_error(exit_message)


def reset_rg_to_default(fastq1: str, fastq2: Optional[str],
                        output_basename: str, readgroups_txt: str) -> None:
    logger.warning(f"Writing '{DEFAULT_READGROUP}' to '{readgroups_txt}'...")
    with open(readgroups_txt, 'w') as rg_file:
        rg_file.write(DEFAULT_READGROUP + "\n")
    logger.info("Removing all splitted fastq files...")
    run_command(['rm', '-f', os.path.join(outprefix, "*.fastq.gz")])
    save_fastq_by_rg(fastq1, fastq2, [DEFAULT_READGROUP], output_basename)


def count_fq_lines(fastq: str) -> int:
    unpigz_proc = subprocess.Popen(['unpigz', '-c', fastq], stdout=subprocess.PIPE)
    counter_proc = subprocess.run(['wc', '-l'], stdin=unpigz_proc.stdout, stdout=subprocess.PIPE)

    return int(counter_proc.stdout.split()[0])


def check_fastq_line_counts(fastq: str, rg_list: List[str], output_basename: str, fastq_outsuffix: str) -> bool:
    """Check if the number of lines in the input fastq file is equal to the sum of lines in the output fastq files."""
    logger.info(f"Checking if '{fastq}' is consistent...")

    input_fastq_lines_count = count_fq_lines(fastq)

    fastq_outprefix = os.path.join(outprefix, f"{output_basename}")
    fastq_results_dict = dict()
    for rg in rg_list:
        fastq_rg_output_path = f"{fastq_outprefix}-{rg}{fastq_outsuffix}"
        fastq_results_dict[fastq_rg_output_path] = count_fq_lines(fastq_rg_output_path)

    is_consistent = input_fastq_lines_count == sum(fastq_results_dict.values())
    if is_consistent:
        logger.info(f"Consistency check passed for '{fastq}'")
    else:
        logger.warning("Inconsistency detected!")
        logger.warning("Total number of lines in input fastq file:")
        logger.warning(f"'{fastq}': {input_fastq_lines_count}")
        logger.warning("Number of lines in output fastq files:")
        for fastq_path, lines_count in fastq_results_dict.items():
            logger.warning(f"'{fastq_path}': {lines_count}")

    return is_consistent


def check_results_consistency(fastq1: str, fastq2: Optional[str],
                              rg_list: List[str], output_basename: str) -> bool:
    check_list = []
    if fastq2 is not None:
        check_list.append(check_fastq_line_counts(fastq1, rg_list, output_basename, '_1.fastq.gz'))
        check_list.append(check_fastq_line_counts(fastq2, rg_list, output_basename, '_2.fastq.gz'))
    else:
        check_list.append(check_fastq_line_counts(fastq1, rg_list, output_basename, '.fastq.gz'))

    return all(check_list)


def split_fastq_by_rg(fastq: str, rg: str, output_fastq_rg: str) -> None:
    cmd_suffix = ['-j', str(cpu_count()), '-o', output_fastq_rg, fastq]
    if rg == DEFAULT_READGROUP:
        logger.info(f"Injecting default '{DEFAULT_READGROUP}' readgroup to '{fastq}'...")
        cmd = ['seqkit', 'replace', '-p', '^', '-r', f"{DEFAULT_READGROUP}:"] + cmd_suffix
        run_command(cmd, exit_message=f"Failed to inject '{DEFAULT_READGROUP}' to '{fastq}'")
    else:
        logger.info(f"Splitting {fastq} by '{rg}'...")
        cmd = ['seqkit', 'grep', '-rp', f'^{rg}'] + cmd_suffix
        run_command(cmd, exit_message=f"Failed to extract '{rg}' from '{fastq}'")
        logger.info(f"Successfully splitted '{fastq}' by '{rg}' to '{output_fastq_rg}'")


def save_fastq_by_rg(fastq1: str, fastq2: Optional[str], rg_list: List[str], output_basename: str) -> None:
    for rg in rg_list:
        fastq_outprefix = os.path.join(outprefix, f"{output_basename}-{rg}")
        if fastq2 is not None:
            split_fastq_by_rg(fastq1, rg, f"{fastq_outprefix}_1.fastq.gz")
            split_fastq_by_rg(fastq2, rg, f"{fastq_outprefix}_2.fastq.gz")
        else:
            split_fastq_by_rg(fastq1, rg, f"{fastq_outprefix}.fastq.gz")


def is_valid_pattern(readgroups_txt: str) -> bool:
    rg_counter_process = subprocess.run(['wc', '-l', readgroups_txt], stdout=subprocess.PIPE)
    rg_count = int(rg_counter_process.stdout.split()[0])

    return 0 < rg_count < READGROUPS_NUM_THRESHOLD


def write_rg_candidates(fastq: str, pattern: str, readgroups_txt: str) -> None:
    with open(readgroups_txt, 'w') as rg_file:
        zcat_process = subprocess.Popen(['zcat', fastq], stdout=subprocess.PIPE)
        sed_process = subprocess.Popen(['sed', '-n', '1~4p'], stdin=zcat_process.stdout, stdout=subprocess.PIPE)
        zgrep_process = subprocess.Popen(['grep', '-oP', pattern], stdin=sed_process.stdout, stdout=subprocess.PIPE)
        subprocess.run(['sort', '-u'], stdin=zgrep_process.stdout, stdout=rg_file)


def get_rg_list(fastq: str, readgroups_txt: str) -> List[str]:
    write_rg_candidates(fastq, NEW_FASTQ_HEADER_PATTERN, readgroups_txt)
    if not is_valid_pattern(readgroups_txt):
        logger.warning("Unable to find readgroups in fastq headers by pattern. "
                       f"Going to use default '{DEFAULT_READGROUP}' readgroup.")
        with open(readgroups_txt, 'w') as rg_file:
            rg_file.write(DEFAULT_READGROUP + "\n")

    with open(readgroups_txt, 'r') as rg_file:
        rg_list = rg_file.read().splitlines()
        logger.info(f"'{readgroups_txt}' file content: {rg_list}")

    return rg_list


def run(fastq1: str, fastq2: Optional[str], output_basename: str,
        readgroups_txt: str, ignore_warnings: bool) -> None:
    rg_list = get_rg_list(fastq=fastq1, readgroups_txt=readgroups_txt)
    save_fastq_by_rg(fastq1, fastq2, rg_list, output_basename)
    if check_results_consistency(fastq1, fastq2, rg_list, output_basename):
        logger.info("Consistency check passed for all input fastq files.")
    elif ignore_warnings:
        logger.info("Because of inconsistent results and passed '--ignore-warnings' flag, "
                    f"readgroups reset to '{DEFAULT_READGROUP}'.")
        reset_rg_to_default(fastq1, fastq2, output_basename, readgroups_txt)
    else:
        exit_with_error("Failed to pass consistency check.")


if __name__ == '__main__':
    set_logger(LOGGER_FORMAT)

    tempdir = os.environ.get("TEMPDIR", "/tmp")
    outprefix = os.environ.get("HOME", "")
    logger.info(f"TEMPDIR = '{tempdir}', OUTPREFIX = '{outprefix}'")

    args = parse_args()
    logger.info(f"Starting program with the folowing arguments: {args}")

    run(**args)
    logger.info("Run is completed successfully.")
