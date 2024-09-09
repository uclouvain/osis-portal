#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os.path
import subprocess
import sys
from os import path

project_dir = os.getcwd()
project_branch = subprocess.check_output('git branch --show-current', shell=True).decode(sys.stdout.encoding).strip()
default_module_branch = 'dev'
modules_branches = {}
modules = {
    "continuing_education": "https://github.com/uclouvain/osis-portal-continuing-education.git",
    "dissertation": "https://github.com/uclouvain/osis-portal-dissertation.git",
    "internship": "https://github.com/uclouvain/osis-portal-internship.git",
    "osis_common": "git@github.com:uclouvain/osis-common.git",
    "admission": "git@github.com:uclouvain/osis-portal-admission.git",
}
arguments = len(sys.argv) - 1
if arguments > 0:
    default_module_branch = sys.argv[1]
    if arguments > 1:
        if arguments % 2 == 0:
            raise Exception("Le nombre d'arguments doit être impair : "
                            "la branche par défaut en premier et un suite de couple nom_dule/branhc_module")
        idx = 2
        while idx < arguments:
            module_name = sys.argv[idx]
            if module_name not in modules:
                raise Exception("Le module {} n'est pas dans la liste des modules".format(module_name))
            idx = idx + 1
            module_branch = sys.argv[idx]
            modules_branches[module_name] = module_branch
            idx = idx + 1

elif project_branch in ['dev', 'test', 'qa', 'master']:
    default_module_branch = project_branch
print('Project Dir : {}'.format(project_dir))
print('Project Branch : {}'.format(project_branch))
print('Module Branch : {}'.format(default_module_branch))
print('')

for module, git_url in modules.items():
    module_dir = os.path.join(project_dir, module)
    specific_module_branch = default_module_branch
    if path.exists(module_dir) and path.isdir(module_dir):
        print('')
        print('Module {} exists in project directory'.format(module))
        print('Updating module {} from branch {}'.format(module, default_module_branch))
        if module in modules_branches:
            specific_module_branch = modules_branches.get(module)
        fetch_command = 'git fetch origin {branch}'.format(branch=specific_module_branch)
        switch_branch_command = 'git checkout {branch}'.format(branch=specific_module_branch)
        new_branch_command = 'git checkout -b {branch} origin/{branch}'.format(branch=specific_module_branch)
        check_branch_exists_locally_command = ' git rev-parse --verify {branch}'.format(branch=specific_module_branch)
        pull_command = 'git pull'
        os.chdir(module_dir)
        os.system(fetch_command)
        try:
            command_status = subprocess.check_call(check_branch_exists_locally_command.split())
            os.system(switch_branch_command)
        except subprocess.CalledProcessError:
            os.system(new_branch_command)
        os.system(pull_command)
        os.chdir(project_dir)
    else:
        print('')
        print('Module {} not exists in project directory'.format(module))
        if module in modules_branches:
            specific_module_branch = modules_branches.get(module)
        print('Cloning module {} from branch {} in directory {}'.format(module, specific_module_branch, module_dir))
        command = 'git clone {git_url} -b {branch} {directory}'.format(branch=specific_module_branch,
                                                                       git_url=git_url,
                                                                       directory=module_dir)
        os.system(command)
