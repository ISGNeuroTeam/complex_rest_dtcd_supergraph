import os
import shutil
import uuid
import json

from ..utils.graphmanager_exception import GraphManagerException, NO_GRAPH, NO_ID, NAME_EXISTS
from ..utils.abc_graphmanager import AbstractGraphManager
from pathlib import Path


class FilesystemGraphManager(AbstractGraphManager):
    """
    This is a manager that reads, writes, rewrites and deletes json files.

    :: final_path : path to a folder where all graph jason files are stored
    :: tmp_path : path to a some temporary graph `graphml` file
    :: map_path : path to a map (dictionary) `json` file, which stores {graph_id:title} pairs.

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
        'some-graph-001-uuid-id' : 'some-graph-001-title',
        'some-graph-002-uuid-id' : 'some-graph-002-title',
    }

    each json graph file has this format now:
    {
        'graph_id' : 'some-uuid64-data`,    <--- here we store its id
        'title' : 'title-of-the-graph`,     <--- here we store its title
        'graph': {}                         <--- here we store all the graph data: nodes, edges, groups
    }

    """

    def __init__(self, path, tmp_path, map_path):  # or better import it from settings here?
        self.final_path = path  # graph base dir
        self.tmp_path = tmp_path + '/tmp.graphml'
        self.map_path = map_path + '/graph_map.json'  # not empty, at least {}
        if not os.path.isfile(self.map_path):
            with open(self.map_path, 'w') as map_file:
                map_file.write('{}')
        self.map_backup_path = map_path + '/graph_backup.json'
        self.map_tmp_path = map_path + '/graph_tmp.json'
        self.default_filename = 'graph.json'

    def read(self, graph_id) -> dict:
        """Read graph json file by 'graph_id'"""
        graph_data: dict = {}
        try:
            # read graph.graphml by its name and id and get the 'content' of it
            with open(Path(self.final_path) / graph_id / self.default_filename, 'r') as graph:
                graph_data['graph'] = graph.read()

            # back up current map file
            # shutil.copyfile(self.map_path,
            #                 self.map_backup_path)  # TODO why do we need to backup map file if we do not change it?

            # read the map file and get the title of the graph by its id
            with open(self.map_path, 'r') as map_file:
                id_map = json.load(map_file)
                graph_data['title'] = id_map[graph_id]  # this is the only place where the NO_GRAPH error may trigger

            # add graph_id to graph data
            graph_data['graph_id'] = graph_id

            # return result
            return graph_data
        except OSError:
            raise GraphManagerException(NO_GRAPH, graph_id)

    def read_all(self) -> list[dict]:
        """Read all graph json files"""
        graph_list = []
        with open(self.map_path, 'r') as map_file:
            id_map = json.load(map_file)
            for k, v in id_map.items():
                graph_list.append({'graph_id': k, 'title': v})
        return graph_list

    def write(self, graph: dict) -> None:
        """Create graph json file with `graph` data"""
        # backup the map file
        shutil.copyfile(self.map_path, self.map_backup_path)

        # read the map file
        with open(self.map_path, 'r') as map_file:
            id_map = json.load(map_file)
            # check if we have this graph already
            if graph["title"] in id_map.values():
                raise GraphManagerException(NAME_EXISTS, graph["title"])

        # create unique id
        unique_id = str(uuid.uuid4())
        # save the name to map with new id
        id_map[unique_id] = graph["title"]

        # save id_map to map_tmp_path
        with open(self.map_tmp_path, 'w') as map_tmp_file:
            json.dump(id_map, map_tmp_file)
        # rename map_tmp_path to map_path
        os.rename(self.map_tmp_path, self.map_path)  # atomic operation

        # save graph['content'] to tmp_path file
        with open(self.tmp_path, 'w') as file:
            file.write(graph["graph"])
        # create new graph dir by its id
        graph_dir = Path(self.final_path) / unique_id
        os.mkdir(graph_dir)
        # move graph data from tmp_path to its new placement
        os.rename(self.tmp_path, Path(graph_dir / self.default_filename))  # atomic operation

    def update(self, graph: dict) -> None:
        """Rewrite graph json file with `graph` data"""
        if 'graph_id' not in graph:
            raise GraphManagerException(NO_ID)
        if 'title' in graph:
            # backing up the map file | why?
            shutil.copyfile(self.map_path, self.map_backup_path)
            # read the id_map file
            with open(self.map_path, 'r') as map_file:
                id_map = json.load(map_file)
                # check if we have this graph already
                if graph["title"] in id_map.values():
                    raise GraphManagerException(NAME_EXISTS, graph["title"])
            # try:
            # saving the name of the graph to current id_map | why? it is the same
            # id_map[graph['graph_id']] = graph["title"]
            # except KeyError:
            # this error is thrown when there is no such id in the map
            # may be it is simpler to just check if current id is in id_map?
            # raise GraphManagerException(NO_GRAPH, graph['graph_id'])

            # opening tmp map file for writing and saving current id_map to it
            with open(self.map_tmp_path, 'w') as map_tmp_file:
                json.dump(id_map, map_tmp_file)
            os.rename(self.map_tmp_path, self.map_path)  # atomic operation

        # rewrite the content of the graph
        if 'graph' in graph:
            graph_dir = Path(self.final_path) / graph['graph_id']
            if not os.path.isdir(graph_dir):
                raise GraphManagerException(NO_GRAPH, graph['graph_id'])
            with open(self.tmp_path, 'w') as file:
                file.write(graph["graph"])
            os.rename(self.tmp_path, Path(graph_dir) / self.default_filename)  # atomic operation

    def remove(self, graph_id) -> None:
        """Delete graph json file by 'graph_id'"""
        graph_dir = Path(self.final_path) / graph_id
        # check if we have graph with this id
        if not os.path.isdir(graph_dir):
            raise GraphManagerException(NO_GRAPH, graph_id)

        # delete directory and it's content
        shutil.rmtree(Path(self.final_path) / graph_id)

        # back up id_map file
        shutil.copyfile(self.map_path, self.map_backup_path)

        # read id_map
        with open(self.map_path, 'r') as map_file:
            id_map = json.load(map_file)
        # delete id from id_map
        del id_map[graph_id]

        # save the id_map
        with open(self.map_tmp_path, 'w') as map_tmp_file:
            json.dump(id_map, map_tmp_file)
        os.rename(self.map_tmp_path, self.map_path)  # atomic operation
