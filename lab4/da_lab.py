# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:05:35 2020

@author: rk260
"""

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

global node_list
node_list=set()

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
    list_of_nodes=set()
    for z in read_osm_data(ways_filename):
        if 'highway' in z['tags'].keys():    
            if z['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                for f in z['nodes']:
                    list_of_nodes.add(f)
    for y in read_osm_data(nodes_filename):
        if y['id'] in list_of_nodes:
            big_nodes.update({y['id']:y})
            big_tuple=(y['id'],y['lat'],y['lon'])
            node_list.add(big_tuple)
    list_of_nodes.clear()
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
                        '''
                        #to avoid duplicate reference nodes.
                        length=None
                        sonic=None
                        for f in answer_dict[x['nodes'][w]]:
                            if f[0]==x['nodes'][w+1]:
                                length=f[3]
                                sonic=f[4]
                        if length==None:
                            answer_dict[x['nodes'][w]].add((x['nodes'][w+1],lat,lon,dist,speed))
                        elif (length/sonic)>(dist/speed):
                            answer_dict[x['nodes'][w]].remove((x['nodes'][w+1],lat,lon,length,sonic))
                            answer_dict[x['nodes'][w]].add((x['nodes'][w+1],lat,lon,dist,speed))
                            '''
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
                                '''
                                #to avoid duplicate reference nodes.
                                length1=None
                                sonic1=None
                                for f in answer_dict[x['nodes'][w]]:
                                    if f[0]==x['nodes'][w-1]:
                                        length1=f[3]
                                        sonic1=f[4]
                                if length1==None:
                                    answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                                elif (length1/sonic1)>(dist/speed):
                                    answer_dict[x['nodes'][w]].remove((x['nodes'][w-1],lat,lon,length1,sonic1))
                                    answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                                '''
                    else:
                        if w!=0:
                            #calculate distance between x['nodes'][w] and x['nodes'][w-1]
                            lat=big_nodes[x['nodes'][w-1]]['lat']
                            lon=big_nodes[x['nodes'][w-1]]['lon']
                            oth_lat=big_nodes[x['nodes'][w]]['lat']
                            oth_lon=big_nodes[x['nodes'][w]]['lon']
                            dist=great_circle_distance((lat,lon), (oth_lat,oth_lon))
                            answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                            '''
                            #to avoid duplicate reference nodes.
                            length2=None
                            sonic2=None
                            for f in answer_dict[x['nodes'][w]]:
                                if f[0]==x['nodes'][w-1]:
                                    length2=f[3]
                                    sonic2=f[4]
                            if length2==None:
                                answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                            elif (length2/sonic2)>(dist/speed):
                                answer_dict[x['nodes'][w]].remove((x['nodes'][w-1],lat,lon,length2,sonic2))
                                answer_dict[x['nodes'][w]].add((x['nodes'][w-1],lat,lon,dist,speed))
                            '''
    big_nodes.clear()
    #removing any empty keys
    actual_dict={}
    for f in answer_dict.keys():
        if answer_dict[f]!=set():
            actual_dict.update({f:answer_dict[f]})
    answer_dict.clear()
    return actual_dict

def find_short_path_nodes(aux_structures, node1, node2, n=0):
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
    #n=0 for optimizing distance, n=1 for optimizing time.
    expanded=set()
    #agenda has all nodes we want to check for expanding (w/ value of distance)
    agenda={node1:0}
    #paths has the shortest path for each node.
    paths={node1:([node1],0)}
    if node1==node2:
        return [node1]
    expanded.add(node1)
    #Adding node id, (distance, traversed path) key-value pairs
    if node1 not in aux_structures:
        return None
    for f in aux_structures[node1]:
        if n!=0:
            agenda.update({f[0]:f[3]/f[4]})
            paths.update({f[0]:([node1,f[0]],f[3]/f[4])})
        else:
            agenda.update({f[0]:f[3]})
            paths.update({f[0]:([node1,f[0]],f[3])})
        if f[0]==node2:
            return[node1,node2]
    #count=0 
    #minicount=0
    #dist1=12.223428415881951
    while True:
        #key we want to expand
        #count+=minicount
        #minicount=0
        z=min(agenda, key=agenda.get)
        if (z in aux_structures.keys()) and not (z in expanded):
            expanded.add(z)
            for x in aux_structures[z]:
                #Go through every child in the expansion
                if not (x[0] in expanded):
                    #Update agenda and paths with child.
                    #if great_circle_distance((x[1],x[2]),(42.5465, -71.1787))<dist1: 
                    #    minicount+=1
                    if n!=0:
                        agenda.update({x[0]:agenda[z]+(x[3]/x[4])})
                        if not (x[0] in paths):
                            the_sum=(agenda[z]+(x[3]/x[4]))    
                            temp=(paths[z][0][:],the_sum)
                            paths.update({x[0]:temp})
                            if not (z in paths[x[0]][0]):
                                paths[x[0]][0].append(z)
                        else:
                            if (agenda[z]+(x[3]/x[4]))<paths[x[0]][1]:
                                oth_sum=(agenda[z]+(x[3]/x[4]))
                                oth_temp=(paths[z][0][:],oth_sum)
                                paths.update({x[0]:oth_temp})
                                if not (z in paths[x[0]][0]):
                                    paths[x[0]][0].append(z)
                    else:
                        agenda.update({x[0]:agenda[z]+x[3]})
                        if not (x[0] in paths):
                            the_sum=(agenda[z]+x[3])    
                            temp=(paths[z][0][:],the_sum)
                            paths.update({x[0]:temp})
                            if not (z in paths[x[0]][0]):
                                paths[x[0]][0].append(z)
                        else:
                            if (agenda[z]+x[3])<paths[x[0]][1]:
                                oth_sum=(agenda[z]+x[3])
                                oth_temp=(paths[z][0][:],oth_sum)
                                paths.update({x[0]:oth_temp})
                                if not (z in paths[x[0]][0]):
                                    paths[x[0]][0].append(z)
            agenda.pop(z)
        else:
            if not(z in expanded):
                expanded.add(z)
            agenda.pop(z)
        if node2 in agenda.keys():
            if min(agenda, key=agenda.get)==node2:
                paths[node2][0].append(node2)
                #print(count)
                return paths[node2][0]
        if len(agenda)==0:
            return None
    
def find_short_path(aux_structures, loc1, loc2, n=0, oth_nodes=node_list):
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
    the_nodes=oth_nodes.copy()
    nodes_to_remove=set()
    for s in the_nodes:
        if not (s[0] in aux_structures.keys()):
            nodes_to_remove.add(s)
    the_nodes=the_nodes.difference(nodes_to_remove)
    min_dist1=-1
    min_dist2=-1
    min1=0
    min2=0
    for r in the_nodes:
        #parsing through every node to search for least distance to a node.
        one_dist=great_circle_distance((r[1],r[2]),(loc1[0],loc1[1]))
        two_dist=great_circle_distance((r[1],r[2]),(loc2[0],loc2[1]))
        if (one_dist<min_dist1) or (min_dist1==-1):
            min_dist1=one_dist
            min1=r[0]
        if (two_dist<min_dist2) or (min_dist2==-1):
            min_dist2=two_dist
            min2=r[0]
    
    #find the shortest path between these nodes
    if n!=0:
        real_path=find_short_path_nodes(aux_structures, min1, min2, 1)
    else:
        real_path=find_short_path_nodes(aux_structures, min1, min2)
    
    if real_path is None or len(real_path)==1:
        return None
    #convert node ids to coordinates
    for q in the_nodes:
        if q[0] in real_path:
            the_index= real_path.index(q[0])
            new_tuple=(q[1],q[2])
            real_path.remove(q[0])
            real_path.insert(the_index,new_tuple)
    return real_path
        


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
    return find_short_path(aux_structures, loc1, loc2, 1)


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    #Section 2 Questions:
    #   count=0
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    count+=1
    
    '''for way in read_osm_data('resources/mit.ways'):
        print(way)'''
    '''for node in read_osm_data('resources/mit.nodes'):
        print(node)'''
    
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
    
    #Section 4 Questions:
    #stuff=build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    #print(find_short_path(stuff, ((41.4452463, -89.3161394)),(41.4441902,-89.3179527)))
    #stuff=build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways')
    #print(find_short_path(stuff, (42.3576 , -71.0951),(42.3609, -71.0911)))
    
    #stuff=build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways')
    #print(stuff)
    #print(find_fast_path(stuff, (42.36, -71.0907),(42.3592, -71.0932)))
    
    #heuristic statistics:
    #stuff=build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
    #print(find_fast_path(stuff, (42.3858, -71.0783),(42.5465, -71.1787)))
    #before heuristic: 509449 paths searched (ran a count for every path added).
    #after heuristic: 156274 paths searched (only permitted paths which were closer
    #than before to be expanded).
    
    #implementing server:
    #from_spot = (41.375288, -89.459541)
    #to_spot = (41.452802, -89.443683)
    #aux = build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
    #print(to_local_kml_url(find_(SHORT OR FAST)_path(aux, from_spot, to_spot)))
    #pass
