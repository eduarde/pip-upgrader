from __future__ import print_function, unicode_literals
import csv
from collections import OrderedDict

from colorclass import Color
from terminaltables import AsciiTable


def user_input(prompt=None):  # pragma: nocover
    try:
        input_func = raw_input
    except NameError:
        input_func = input
    return input_func(prompt)


class PackageInteractiveSelector(object):
    packages_for_upgrade = OrderedDict()
    selected_packages = []

    def __init__(self, packages_map, options):
        self.selected_packages = []
        self.packages_for_upgrade = {}

        # map with index number, for later choosing
        i = 1
        for package in packages_map.values():
            if package['upgrade_available']:
                self.packages_for_upgrade[i] = package.copy()
                i += 1

        # maybe all packages are up-to-date
        if not self.packages_for_upgrade:
            print(Color('{autogreen}All packages are up-to-date.{/autogreen}'))
            raise KeyboardInterrupt()

        # choose which packages to upgrade (interactive or not)
        if '-p' in options and options['-p']:
            if options['-p'] == ['all']:
                self._select_packages(self.packages_for_upgrade.keys())
            else:
                for index, package in self.packages_for_upgrade.items():
                    for chosen_package in options['-p']:
                        if chosen_package.lower().strip() == package['name'].lower().strip():
                            self._select_packages([index])
        else:
            self.ask_for_packages()

    def get_packages(self):
        return self.selected_packages

    def _get_packages_list(self):
        data = [[
            Color('{autoblue}No.{/autoblue}'),
            Color('{autoblue}Package{/autoblue}'),
            Color('{autoblue}Current version{/autoblue}'),
            Color('{autoblue}Latest version{/autoblue}'),
            Color('{autoblue}Release date{/autoblue}'),
        ]]

        for i, package in self.packages_for_upgrade.items():
            data.append([Color('{{autobgblack}}{{autogreen}} {} {{/autogreen}}{{/bgblack}}'.format(i)),
                         Color('{{autogreen}} {} {{/autogreen}}'.format(package['name'])),
                         package['current_version'],
                         package['latest_version'],
                         package['upload_time']])

        return data

    def _get_packages_list_to_print(self):
        data = [[
            'No.',
            'Package',
            'Current version',
            'Latest version',
            'Release date',
        ]]

        for i, package in self.packages_for_upgrade.items():
            data.append(['{}'.format(i),
                         '{}'.format(package['name']),
                         package['current_version'],
                         package['latest_version'],
                         package['upload_time']])

        return data

    def ask_for_packages(self):

        packages_list = self._get_packages_list()
        table = AsciiTable(packages_list).table

        print('')
        print(Color('{autogreen}Available upgrades:{/autogreen}'))
        print(table)
        print('')

        print('Please choose which packages should be upgraded. Choices: "all", "q" (quit), "x" (exit), "p" (print) or "1 2 3"')
        choice = user_input(Color('{autogreen}Choice:{/autogreen} ')).strip()

        if not choice and not choice.strip():
            print(Color('{autored}No choice selected.{/autored}'))
            raise KeyboardInterrupt()

        choice = choice.strip()

        if choice == 'q':  # pragma: nocover
            print(Color('{autored}Quit.{/autored}'))
            raise KeyboardInterrupt()

        if choice == 'x':  # pragma: nocover
            print(Color('{autored}Exit.{/autored}'))
            raise KeyboardInterrupt()

        if choice == 'p':
            print(Color('{autogreen}Print. CSV file was created.{/autogreen}'))
            self._print_upgrades()
            raise KeyboardInterrupt()

        if choice == "all":
            self._select_packages(self.packages_for_upgrade.keys())
        else:
            try:
                selected = list(self._select_packages([int(index.strip()) for index in choice.split(' ')]))
                if not any(selected):
                    print(Color('{autored}No valid choice selected.{/autored}'))
                    raise KeyboardInterrupt()
            except ValueError:  # pragma: nocover
                print(Color('{autored}Invalid choice{/autored}'))
                raise KeyboardInterrupt()


    def _print_upgrades(self):
        packages_list = self._get_packages_list_to_print()
        with open('AVAILABLE_UPGRADES.csv', 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
            for row in packages_list:
                wr.writerow(row)

    def _select_packages(self, indexes):
        selected = []

        for index in indexes:
            if index in self.packages_for_upgrade:
                self.selected_packages.append(self.packages_for_upgrade[index].copy())
                selected.append(True)

        return selected
