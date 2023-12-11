import os
import shutil
import uuid
import json
import tempfile
from typing import Union, AnyStr

from ..utils.graphmanager_exception import GraphManagerException, NO_GRAPH, NO_ID, NAME_EXISTS, NO_TITLE
from ..utils.abc_graphmanager import AbstractGraphManager
from pathlib import Path


class FilesystemGraphManager(AbstractGraphManager):
    """
    This is a manager that reads, writes, rewrites and deletes json files.

    :: final_path : path to a folder where all graph jason files are stored
    :: tmp_file_path : path to a some temporary graph `graphml` file
    :: map_file_path : path to a map (dictionary) `json` file, which stores {graph_id:title} pairs.

    :: map_backup_path : path to a map backup `json` file: temporary storage for a map path
    :: map_tmp_path : path to a graph_tmp.json file inside a map folder
    :: default_filename : presumably default name of the graph

    the files seem to be stored like this:
        Path(final_path / id / graph.graphml)

    and all the graph data stored in that file in a 'content' part, like this
        with open(Path(self.final_path) / graph_id / self.default_filename, 'r') as graph:
            graph_data['content'] = graph.read()

    id_map json file has this format now:
    {
        "some-graph-001-uuid-id": "some-graph-001-title",
        "some-graph-002-uuid-id": "some-graph-002-title"
    }

    graph json file is stored at:
        GRAPH_BASE_DIR/some-graph-001-uuid-id/graph.graphml

    each json graph file has this format now:
    {
        'title' : 'title-of-the-graph`,     <--- here we store graph's title | why we need to store title in graph json?
        'nodes': {nodes info},              <--- here we store the graph nodes
        'edges': {edges info},              <--- here we store the graph edges
        'groups': {groups info}             <--- here we store the graph groups
    }
    """

    def __init__(self, path, tmp_folder_path, map_folder_path):  # or better import it from settings here?
        self.final_path = path  # graph base dir
        self.tmp_file_path = tmp_folder_path + '/tmp.graphml'
        self.map_file_path = map_folder_path + '/graph_map.json'  # not empty, at least {}
        if not os.path.isfile(self.map_file_path):
            with open(self.map_file_path, 'w') as map_file:
                map_file.write('{}')
        self.map_backup_path = map_folder_path + '/graph_backup.json'
        self.map_tmp_path = map_folder_path + '/graph_tmp.json'
        self.default_filename = 'graph.json'

    def read(self, graph_id) -> dict:
        """Read graph json file by 'graph_id'"""
        try:
            # read graph.graphml by its name and id and get the 'content' of it
            file_path = Path(self.final_path) / str(graph_id) / self.default_filename
            with open(file_path, 'r') as graph:
                graph_data = json.load(graph)

            # return result
            return graph_data
        except OSError:
            raise GraphManagerException(NO_GRAPH, graph_id)

    def read_all(self) -> list[dict]:
        """Read all graph json files
        """
        with open(self.map_file_path, 'r') as map_file:
            graph_data = json.load(map_file)
        result = [{"id": graph_id, "title": title} for graph_id, title in graph_data.items()]
        return result

    def write(self, graph: dict) -> dict:
        """Create graph json file with `graph` data"""
        # backup the map file
        shutil.copyfile(self.map_file_path, self.map_backup_path)

        # read the map file
        with open(self.map_file_path, 'r') as map_file:
            id_map = json.load(map_file)
            # check if we have this graph already
            if graph["title"] in id_map.values():
                raise GraphManagerException(NAME_EXISTS, graph["title"])

        # create unique id
        unique_id = str(uuid.uuid4())
        # save the name to map with new id
        id_map[unique_id] = graph["title"]

        # save id_map to map_tmp
        with open(self.map_tmp_path, 'w') as map_tmp_file:
            json.dump(id_map, map_tmp_file)
        # rename map_tmp_path to map_folder_path
        os.rename(self.map_tmp_path, self.map_file_path)  # atomic operation

        # create new graph dir by its id
        graph_dir = Path(self.final_path) / unique_id
        os.mkdir(graph_dir)

        # save graph to file
        save_data_to_file(graph, Path(graph_dir / self.default_filename))
        return {unique_id: graph['title']}

    def update(self, graph: dict, graph_id: str) -> None:
        """Rewrite graph json file with `graph` data"""
        # read the id_map file
        with open(self.map_file_path, 'r') as map_file:
            id_map = json.load(map_file)

        graph_dir = Path(self.final_path) / str(graph_id)
        # check if we don't have this graph or there is no such dir
        if not os.path.isdir(graph_dir):
            raise GraphManagerException(NO_GRAPH, graph_id)

        # rewrite the content of the graph
        save_data_to_file(graph, Path(graph_dir) / self.default_filename)

    def remove(self, graph_id: str) -> None:
        """Delete graph json file by 'graph_id'"""
        graph_dir = Path(self.final_path) / graph_id
        # check if we have graph with this id
        # if not os.path.isdir(graph_dir):
        #     raise GraphManagerException(NO_GRAPH, graph_id)

        # delete directory, and it's content
        # shutil.rmtree(Path(self.final_path) / str(graph_id))

        # back up id_map file
        shutil.copyfile(self.map_file_path, self.map_backup_path)

        # read id_map
        with open(self.map_file_path, 'r') as map_file:
            id_map = json.load(map_file)
        # delete id from id_map
        del id_map[graph_id]

        save_data_to_file(id_map, self.map_file_path)


def save_data_to_file(data: Union[dict, AnyStr], destination_path: Path) -> None:
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(json.dumps(data).encode('utf-8'))
        file.flush()
        os.rename(file.name, destination_path)
