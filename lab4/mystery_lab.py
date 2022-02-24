#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url
# NO ADDITIONAL IMPORTS!
ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

global min_dist
min_dist=0

def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
    #The datatype I will be a dict with keys of eligible node ids
    #with values containing a set of tuples of adjacent eligible nodes:
    #{node: {(id,lat,lon,distance,speed_limit)}}
    answer_dict={}
    big_nodes={}
    #for way in read_osm_data(ways_filename):
    #    print (way)
    for y in read_osm_data(nodes_filename):
        big_nodes.update({y['id']:y})
    for x in read_osm_data(ways_filename):
        if 'highway' in x['tags'].keys():    
            if x['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                for w in range(len(x['nodes'])):
                    #find speed limit:
                    if 'maxspeed_mph' in x['tags'].keys():
                        speed=x['tags']['maxspeed_mph']
                    else:
                        speed=DEFAULT_SPEED_LIMIT_MPH[x['tags']['highway']]
                    #adds a new key if id is not in answer_dict
                    if x['nodes'][w] not in answer_dict.keys():
                        answer_dict.update({x['nodes'][w]:set()})
                    if w!=len(x['nodes'])-1:
                        #calculate distance between x['nodes'][w] and x['nodes'][w+1]
                        lat=big_nodes[x['nodes'][w+1]]['lat']
                        lon=big_nodes[x['nodes'][w+1]]['lon']
                        oth_lat=big_nodes[x['nodes'][w]]['lat']
                        oth_lon=big_nodes[x['nodes'][w]]['lon']
                        dist=great_circle_distance((lat,lon), (oth_lat,oth_lon))
                        answer_dict[x['nodes'][w]].add((x['nodes'][w+1],lat,lon,dist,speed))
                    if 'oneway' in x['tags'].keys():
                        if x['tags']['oneway']!='yes':
                            if w!=0:
                                #calculate distance between x['nodes'][w] and x['nodes'][w-1]
                                lat=big_nodes[x['nodes'][w-1]]['lat']
                                lon=big_nodes[x['nodes'][w-1]]['lon']
                                oth_lat=big_nodes[x['nodes'][w]]['lat']
                                oth_lon=big_nodes[x['nodes'][w]]['lon']
                                dist=great_circle_distance((lat,lon), (oth_lat,oth_lon))
                                answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                    else:
                        if w!=0:
                            #calculate distance between x['nodes'][w] and x['nodes'][w-1]
                            lat=big_nodes[x['nodes'][w-1]]['lat']
                            lon=big_nodes[x['nodes'][w-1]]['lon']
                            oth_lat=big_nodes[x['nodes'][w]]['lat']
                            oth_lon=big_nodes[x['nodes'][w]]['lon']
                            dist=great_circle_distance((lat,lon), (oth_lat,oth_lon))
                            answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
    #removing any empty keys
    actual_dict={}
    for f in answer_dict.keys():
        if answer_dict[f]!=set():
            actual_dict.update({f:answer_dict[f]})
    return actual_dict
 
def findPath(aux_structures, even_before, even_before_dist, past_in1, previous_value, final_value, further_dist, final_node, first_node):                       
    #Given previous networks, the database, and the distance all the way to the
    #previous node, this finds the path of nodes traveled.
    past_in2=past_in1[:]
    path=[final_node]
    #Add final node itself as well as just before.
    past_in2.append({even_before:even_before_dist})
    while not(first_node in path):
        #Check previous bacon set
        for x in past_in2[-(len(path))]:
            previous_value=past_in2[-(len(path))][x]
            if previous_value==0:
                path.append(first_node)
                break
            #Find the distance between the 2 bacon sets.
            if x in aux_structures.keys():
                for f in aux_structures[x]:
                    if f[0]==path[-1]:
                        further_dist=f[3]
                if (past_in2[-(len(path))][x])!=0:
                    #determining if this was the right node before
                    if (round(final_value-previous_value,6)==round(further_dist,6)) and round(final_value-previous_value,3)!=0.000:
                        path.append(x)
                        final_value=previous_value
                        break
    path=path[::-1]
    return path

def sortThird(val):
    return val[3]

def find_short_path_nodes(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    #For past_in, I do bacon-like sets, except have key-value pair instead of set, 
    #where key is particular node id, and value is distance travelled so far 
    #(min if multiple) parent nodes.
    past_in=[]
    past_in.append({node1:0})
    #current_in has current bacon set, and next_in is for next set.
    current_in={}
    next_in={}
    the_path=[]
    the_distance=0
    if node1==node2:
        return [node1]
    #Adding node id, distance key-value pairs
    if node1 not in aux_structures:
        return None
    else:
        for f in aux_structures[node1]:
                current_in.update({f[0]:f[3]})
                if f[0]==node2:
                    return[node1,node2]
    while len(current_in.keys())!=0:
        for x in current_in.keys():
            if x in aux_structures:
                for y in aux_structures[x]:
                    #find all the child nodes for the parent node in current_in
                    #Add these child nodes to next_in
                    if (y[0] not in next_in.keys()):
                        next_in.update({y[0]:current_in[x]+y[3]})
                    elif (y[0] in next_in.keys()):
                        if (current_in[x]+y[3])<next_in[y[0]]:
                            next_in.pop(y[0])
                            next_in.update({y[0]:current_in[x]+y[3]})
                    #If our id is the end_node, we just need to work backwards
                    #to find the path
                    if y[0]==node2:
                        if (next_in[y[0]]<the_distance) or (the_distance==0):
                            the_path=findPath(aux_structures, x, current_in[x], past_in, current_in[x], next_in[y[0]], y[3], node2, node1)
                            the_distance=next_in[y[0]]
                        next_in.pop(y[0])
                    #If value is over the_distance, remove node. 
                    #Or if the node can't be found for a long time, remove it.
                    elif (((the_distance!=0) and (next_in[y[0]]>the_distance)) or ((the_distance==0) and (next_in[y[0]]>10))):
                        next_in.pop(y[0])
                    if(len(past_in)>10000):
                        return None
        #Move around data for next round of processing
        past_in.append(current_in.copy())
        current_in.clear()
        current_in=next_in.copy()
        next_in.clear()
    if len(the_path)==0:
        return None
    return the_path

def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    raise NotImplementedError


def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    raise NotImplementedError


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    #Section 2 Questions:
    #   count=0
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    count+=1
    
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    if len(node['tags'])!=0:
    #        if 'name' in node['tags'].keys():        
    #            count+=1
    #print(count)    

    #for node in read_osm_data('resources/cambridge.nodes'):
    #    if len(node['tags'])!=0:
    #        if 'name' in node['tags'].keys():
    #            if node['tags']['name']=='77 Massachusetts Ave':
    #                print(node['id'])
    
    #for way in read_osm_data('resources/cambridge.ways'):
    #    count+=1
    #print("count")

    #for way in read_osm_data('resources/cambridge.ways'):
    #    if len(way['tags'])!=0:
    #        if 'oneway' in way['tags'].keys():
    #            if way['tags']['oneway']=='yes':
    #                count+=1
    #print(count)   
    
    #Section 3 Questions:
    #a=(42.363745, -71.100999)
    #b=(42.361283, -71.239677)
    #print(great_circle_distance(a, b))
    
    #for node in read_osm_data('resources/midwest.nodes'):
    #    if node['id']==233941454:
    #        a=(node['lat'],node['lon'])
    #    if node['id']==233947199:
    #        b=(node['lat'],node['lon'])
    #print(great_circle_distance(a, b))
    
    #for way in read_osm_data('resources/midwest.ways'):
    #    if way['id']==21705939:
    #        the_nodes=way['nodes'][:]
    #dist=0
    #for w in range(len(the_nodes)-1):
    #    for node in read_osm_data('resources/midwest.nodes'):
    #        if node['id']==the_nodes[w]:
    #            a=(node['lat'],node['lon'])
    #        if node['id']==the_nodes[w+1]:
    #            b=(node['lat'],node['lon'])
    #    dist+=(great_circle_distance(a, b))
    #print(dist)
    
    stuff=build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways')
    print(find_short_path_nodes(stuff, 7,3))
    '''for node in read_osm_data('resources/cambridge.nodes'):
        print(node)
        break
    for way in read_osm_data('resources/cambridge.ways'):
        print(way)
        break'''