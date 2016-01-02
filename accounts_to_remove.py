#!/usr/bin/env python
# Determine members to be removed from Basecamp by identifying those members that did not reply to the
# 'Basecamp cleaning' thread. Run with -h/--help flag for more information.
from __future__ import print_function
import argparse
import collections
import logging
import re
import os
logging.basicConfig(level=logging.INFO)

__author__ = 'Alexander Junge (alexander.junge@gmail.com)'


def is_existing_file(arg):
    if not os.path.isfile(arg):
        parser.error('Given path {} does not point to an existing directory. Exiting.'.format(arg))
    return arg


def map_organizations_to_members(all_people_html_path):
    organization_to_people = collections.defaultdict(set)

    # Organizations are listed with the following tag: <h3 class="fn org">The Middle layer</h3>
    organization_regexp = re.compile('<h3 class="fn org">(.+)</h3>')
    # People are listed with the following tag: <h3 class="fn">Alexander Junge</h3>
    people_regex = re.compile('<h3 class="fn">(.+)</h3>')

    current_organization = None
    with open(all_people_html) as all_people_file:
        for line in all_people_file:
            line_stripped = line.strip()
            organization_match = organization_regexp.match(line_stripped)
            people_match = people_regex.match(line_stripped)

            if organization_match and people_match:
                logging.error('Line {} in file {} matched both organization and people html tag.'.format(line,
                                                                                                         all_people_html))

            if organization_match:
                current_organization = organization_match.groups(1)[0]
            elif people_match:
                organization_to_people[current_organization].add(people_match.groups(1)[0])
    return organization_to_people


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
                                     """
    Determine members to be removed from Basecamp by identifying those members that did not reply to the 'Basecamp cleaning'
    thread. Names of accounts to be removed are written to stdout while stderr is used for logging purposes.
                                     """)
    parser.add_argument('all_people_html', type=is_existing_file,
                        help='Obtained by saving https://iscbsc.basecamphq.com/companies as an .html file.')
    parser.add_argument('basecamp_cleaning_html', type=is_existing_file,
                        help='Obtained by saving Basecamp cleaning thread as an .html file.')
    args = parser.parse_args()

    all_people_html = args.all_people_html
    # all_people_html = 'ISCB Student Council_ All People.html'
    basecamp_cleaning_html = args.basecamp_cleaning_html
    # basecamp_cleaning_html = 'General Operations _ Basecamp cleaning 2015.html'

    org_to_people = map_organizations_to_members(all_people_html)
    for org in sorted(org_to_people.keys()):
        member_set = org_to_people[org]
        logging.info('Organization {} has {:d} members.'.format(org, len(member_set)))
