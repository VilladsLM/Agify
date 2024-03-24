import argparse
import json
import requests as requests
from typing import Generator


class AgifyPerson:
    input_file = None
    output_file = None

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def _get_people_from_file(self) -> list[dict]:
        with open(f"{self.input_file}", "r") as openfile:
            input_file = json.load(openfile)
            return input_file

    def _group_people(self, people: list[dict]) -> Generator[list, None, None]:
        group = []
        api_chunk_len = 10
        for person in people:
            group.append(person)
            if len(group) >= api_chunk_len:
                yield group
                group = []

        if len(group):
            yield group

    def _get_result_from_group(self, group: list[dict]) -> list[dict]:
        url = "https://api.agify.io"
        names = [i['name'] for i in group]
        param = self._get_query_params(names)
        res = requests.get(url, params=param)
        return res.json()

    def _get_query_params(self, names: list) -> dict:
        params = {}

        for key, name in enumerate(names):
            params[f'name[{key}]'] = name

        return params

    def _append_age_to_people(self, group: list[dict], agify_results: list[dict]) -> list[dict]:
        for i, person in enumerate(group):
            person_results = agify_results[i]
            person['age'] = person_results['age']

        return group

    def _agify_people(self) -> list[list]:
        agified_groups = []
        people = self._get_people_from_file()
        for group in self._group_people(people):
            agify_results = self._get_result_from_group(group)
            agified_groups.append(self._append_age_to_people(group, agify_results))
        return agified_groups

    def _flatten_groups(self, groups: list[list]) -> list:
        return [item for sublist in groups for item in sublist]

    def pull_people_and_agify(self):
        people = self._agify_people()
        flattened_people = self._flatten_groups(people)
        with open(f"{self.output_file}", "w") as f:
            json.dump(flattened_people, f, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='the config')
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()

    pull = AgifyPerson(args.input_file, args.output_file)

    pull.pull_people_and_agify()
