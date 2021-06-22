#! /usr/bin/env python

import re
import argparse


def add_email_to_job_template(email):
    """Add email to job file, if specified."""
    jobfile = '../template/job.run'

    with open(jobfile, 'r') as f:
        filedata = f.read()

    if email is None:
        # no email notification
        filedata = re.sub(("EMAIL OPT\n"
                           "#SBATCH --mail-type=END\n"
                           "#SBATCH --mail-user=.+?\n"),
                          "EMAIL: None\n",
                          filedata)
    else:
        # yes email notification
        filedata = re.sub("EMAIL: None\n",
                          ("EMAIL OPT\n"
                           "#SBATCH --mail-type=END\n"
                           "#SBATCH --mail-user={}\n".format(email)),
                          filedata)

    with open(jobfile, 'w') as f:
        f.write(filedata)
    return


def modify_mpipath(mpidest):
    """
    Add the appripriate path to the two locations.

    The mpi path is specified in the job.run file and in nwxpl.
    This functions changes the job file in the template direcotry
    and the run_nwchem_job function in nwxutils to reflect that path.
    """
    # job file modification
    jobfile = '../template/job.run'
    keyword = 'LD_LIBRARY_PATH ".+?/mpich-3.2/lib"'

    with open(jobfile, 'r') as f:
        filedata = f.read()

    filedata = re.sub(keyword,
                      'LD_LIBRARY_PATH "{}/mpich-3.2/lib"'.format(mpidest),
                      filedata)

    with open(jobfile, 'w') as f:
        f.write(filedata)

    # nwxutils file modification
    utilsfile = 'nwxutils.py'
    keyword = "'.+?/mpich-3.2"

    with open(utilsfile, 'r') as f:
        filedata = f.read()

    filedata = re.sub(keyword,
                      "'{}/mpich-3.2".format(mpidest),
                      filedata)

    with open(utilsfile, 'w') as f:
        f.write(filedata)

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Short script to add user options to pipeline. "
                     "-e will add an email to the job script "
                     "to be notified of job termination. "
                     "-p will change the path to the mpi executable "
                     "in the appropriate files in the pipeline."))
    parser.add_argument('-e', '--email', action='store', dest='email',
                        type=str, required=True,
                        help=("The email to be notified upon job completion. "
                              "Must be a valid address."))
    parser.add_argument('-p', '--mpidest', action='store', dest='mpidest',
                        type=str, required=True,
                        help=("The path to the mpich-3.2 folder from which to "
                              "obtain the appropriate executables."))

    args = parser.parse_args()

    # mpidest = str(Path(args.mpidest).resolve())
    mpidest = args.mpidest

    if args.email == "email":
        add_email_to_job_template(None)
    else:
        add_email_to_job_template(args.email)

    modify_mpipath(mpidest)
