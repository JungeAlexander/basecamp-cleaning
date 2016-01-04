#!/usr/bin/env python3
# The ISCBSC Basecamp cleaning utility.
# Determines members to be removed from Basecamp by identifying those members that did not reply to the
# 'Basecamp cleaning' thread. Run with -h/--help flag for more information.
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
    """
    Extract members of each organization on Basecamp.

    :param all_people_html_path: path to .html file containing all Basecamp members
    :return: dict: str -> set(str); maps each organization to its set of members
    """
    organization_to_people = collections.defaultdict(set)

    # Organizations are listed with the following tag: <h3 class="fn org">The Middle layer</h3>
    organization_regexp = re.compile('<h3 class="fn org">(.+)</h3>')
    # People are listed with the following tag: <h3 class="fn">Alexander Junge</h3>
    people_regex = re.compile('<h3 class="fn">(.+)</h3>')

    current_organization = None
    with open(all_people_html_path) as all_people_file:
        for line in all_people_file:
            line_stripped = line.strip()
            organization_match = organization_regexp.match(line_stripped)
            people_match = people_regex.match(line_stripped)

            assert not(organization_match and people_match)

            if organization_match:
                current_organization = organization_match.groups(1)[0].strip()
            elif people_match:
                organization_to_people[current_organization].add(people_match.groups(1)[0].strip())
    return organization_to_people


def extract_people_to_keep(basecamp_cleaning_html_path):
    """
    Load a list of members to keep on Basecamp.

    :param basecamp_cleaning_html_path: Path to .html file with thread about Basecamp cleaning.
    :return: set(str); containers those members that replied to the Basecamp cleaning thread.
    """
    # Match the following two lines occurring in header of each post
    # <a href="https://iscbsc.basecamphq.com/projects/1765680-general-operations/posts/95816049/comments#comment_331359817" class="permalink" name="331359817">
    # <strong>Some user name</strong>
    user_header_re = re.compile('<a href="https://iscbsc.basecamphq.com/projects/.+" class="permalink" name=.+>')
    user_name_re = re.compile('<strong>(.+)</strong>')

    people_set = set()
    with open(basecamp_cleaning_html_path) as basecamp_cleaning_file:
        for line in basecamp_cleaning_file:
            line_stripped = line.strip()
            if user_header_re.match(line_stripped):
                next_line_stripped = basecamp_cleaning_file.readline().strip()
                user_name_match = user_name_re.match(next_line_stripped)
                if user_name_match:
                    user_name = user_name_match.groups(1)[0]
                    people_set.add(user_name.strip())
    return people_set


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    The ISCBSC Basecamp cleaning utility.
    Determines members to be removed from Basecamp by identifying those members that did not reply to the
    'Basecamp cleaning' thread. Names of accounts to be removed are written to stdout while stderr is used for logging
    purposes. Note: the content of the reply by t user is not checked; only the fact that the user replied to the
    Basecamp cleaning thread is enough to keep the account active.
    """)
    parser.add_argument('all_people_html', type=is_existing_file,
                        help='Obtained by saving https://iscbsc.basecamphq.com/companies as an .html file.')
    parser.add_argument('basecamp_cleaning_html', type=is_existing_file,
                        help='Obtained by saving Basecamp cleaning thread as an .html file.')
    parser.add_argument('cleaning_post_author',
                        help="""
                        User name of the author of the Basecamp post introducing the Basecamp cleaning.
                        The author's user name must be specified as it is not read from
                        file given as basecamp_cleaning_html argument.
                        Remember quotation marks around user names containing spaces.
                        """)
    args = parser.parse_args()

    all_people_html = args.all_people_html
    # all_people_html = 'ISCB Student Council_ All People.html'
    basecamp_cleaning_html = args.basecamp_cleaning_html
    # basecamp_cleaning_html = 'General Operations _ Basecamp cleaning 2015.html'
    cleaning_post_author = args.cleaning_post_author
    # cleaning_post_author = "Alexander Junge"

    org_to_people = map_organizations_to_members(all_people_html)
    all_people = set()
    for org in sorted(org_to_people.keys()):
        member_set = org_to_people[org]
        all_people.update(member_set)
        logging.info('Organization {} has {:d} members.'.format(org, len(member_set)))
    logging.info('Total: {:d}'.format(len(all_people)))

    keep_people = extract_people_to_keep(basecamp_cleaning_html)
    keep_people.add(cleaning_post_author)
    logging.info('{:d} members replied to cleaning thread in order to keep their account.'.format(len(keep_people)))

    keep_people_not_in_organization = [keep for keep in keep_people if keep not in all_people]
    if len(keep_people_not_in_organization) > 0:
        logging.warning('These {:d} member(s) that replied to Basecamp cleaning thread were/was not found in any '
                      'organization: {}'.format(len(keep_people_not_in_organization),
                                                ', '.join(keep_people_not_in_organization)))

    remove_people = set()
    for org in sorted(org_to_people.keys()):
        member_set = org_to_people[org]
        member_set.difference_update(keep_people)
        remove_people.update(member_set)
    assert len(all_people) == (len(remove_people) + len(keep_people) - len(keep_people_not_in_organization))
    logging.info('{:d} members should be removed from Basecamp.'.format(len(remove_people)))

    print('Members to remove:' + os.linesep)
    for org in sorted(org_to_people.keys()):
        if len(member_set) > 0:
            print(org)
            print('---------')
            print('\n'.join(sorted(list(member_set))))
        print()
