# User guide

## API:

### Get list of all graphs: 
Method: `GET`  
Request: `graphs/`  
Result is a list of dicts: {`"id"`: `"graph_id"`, `"title"`: `"graph_title"`}  
Example: `[{"id":"25382325-0c26-4ff0-bf26-a3f87fb61502","title":"some-new-graph-012"},{"id":"8d788a5f-310e-40d7-a8d7-060c247bd89e","title":"some-new-graph-013"}, {"id":"73976e44-ea1b-467c-96d2-1e5008726a48","title":"some-new-graph-014"}]`  

### Get exact graph by id
Method: `GET`  
Request: `graph/graph_id/`  
Example of id: `73976e44-ea1b-467c-96d2-1e5008726a48`  
Result is a dict: `{"graph": "graph_data", "title": "graph_title"}`  

### Create new graph
Method: `POST`  
Request: `graphs/`  
Request body: `{"graph": "some graph data", "title": "some-new-graph-014"}`  
`graph` stores all the graph data  
`title` stores the title of the graph  
Both parameters of the body are **required**  
Result is a dict: `{"status" : "status of the request", "result" : "graph and title of the graph"}`  
Example: `{"status":"SUCCESS","result":{"graph_id":"73976e44-ea1b-467c-96d2-1e5008726a48","title":"some-new-graph-014"}}`  

### Change graph by id
Method: `PUT`  
Request: Request: `graph/graph_id/`  
Example of id: `73976e44-ea1b-467c-96d2-1e5008726a48`  
Request body: `{"graph": "updated graph_data"}`  
Result is a dict: `{"status": "request_status"}`  
Example: `{"status": "SUCCESS"}`  

## Delete graph by id
Method: `DELETE`  
Request: Request: `graph/graph_id/`  
Example of id: `73976e44-ea1b-467c-96d2-1e5008726a48`  
Result is a dict: `{"status": "request_status"}`  
Example: `{"status": "SUCCESS"}`  