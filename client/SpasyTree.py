from Node import *
from collections import deque
import time


class SpasyTree:
    """
    A Merkle-based quaternary tree used as a dataset representation for 
    Spatial Sync (SPASY), a Named Data Networking (NDN) Sync 
    protocol.

    Assumes the use of Geohash.
    """

    def __init__(self, max_depth: int, node: Node = None) -> None:
        """
        Args:
            node (Node, optional): a node object representing the tree's root. 
                                   Defaults to None.
        """
        self._root = node 
        self._max_depth = max_depth
        self._recent_changes = deque(maxlen=10)
 
    ######### ACCESSORS #########
    @property
    def root(self) -> Node:
        """Get, set, or delete the tree's root."""
        return self._root
    
    @property
    def recent_changes(self) -> deque:
        """Get a deque of recently used root hashes."""
        return self._recent_changes
    
    @property
    def max_depth(self) -> int:
        """
        Get the tree's maximum allowable depth.
        This will be based on the chosen geocoding approach.
        It will determine how granular the tree is.
        """
        return self._max_depth
    
    def find_data(self, named_data: str) -> bool:
        """
        Determine if an element of named data is in the tree.

        Args:
            named_data (str): the full hierarchical data name (with geocode).

        Returns:
            bool: True if in the tree
                  False otherwise
        """
        current_node = self._root
        named_data = named_data.lower()
        geocode = named_data.split('/')[-1]
        current_level = current_node.length_geocode()
        #print(f'MAX DEPTH: {self._max_depth}')
        while current_level <= self._max_depth + 1:
            #print(f'CURRENT LEVEL: {current_level} and CURRENT CODE: {geocode[:current_level]}')
            for child in current_node.children:
                if child is not None:
                    if geocode[:current_level] in child.geocode:
                        # we found the child
                        #print(f'GEOCODE: {child.geocode}')
                        if named_data in child.data:
                            #print(f'WE FOUND IT IN {child}')
                            return True
                        else:
                            current_node = child
                            #print(f'THE CURRENT NODE: {current_node.geocode}')
                            break
            current_level += 1
        return False
    
    def find_data_without_geocode(self, node: Node, named_data_without_geocode: str,
                                  geocode_list: list | None = None) -> list:
        """
        A traversal that returns the geocodes of all instances 
        of a piece of named data (regardless of geocode) within the tree.

        Args:
            node (Node): The node being searched.
            named_data_without_geocode (str): The data being sought. This has no geocode attached to it.
            geocode_list (list | None, optional): a list of geocodes in which the data is located. 
                                                  Defaults to None, which becomes an empty list.

        Returns:
            list: A list of geocodes identifying where the data (regardless of geocode) is located.
        """
        if geocode_list is None:
            geocode_list = []

        named_data_without_geocode = named_data_without_geocode.lower()

        if node is not None:
            #print(f'NODE {node.geocode} IS NOT NONE')
            if node.in_data(named_data_without_geocode):
                # because we are using buckets, we will add each possible geocode individually
                for code in node.geocode:
                    if code not in geocode_list:
                        #print(f'ADDING GEOCODE: {code}')
                        geocode_list.append(code)
            else:
                for child in node.children:
                    self.find_data_without_geocode(child, named_data_without_geocode, geocode_list)

        #print(f'GEOCODE LIST: {geocode_list}')
        return geocode_list

    # TODO: it is possible it makes more sense for this to be part of Spasy
    def find_data_by_namespace(self, node: Node, data_by_namespace: dict | None = None) -> dict:
        """
        Traverses the tree to gather all of the namespaces and their data. 
        This can be used by applications to allow a user to filter the namespaces they want.

        Args:
            node (Node): _description_
            data_by_namespace (dict | None, optional): _description_. Defaults to None.

        Returns:
            dict: the dictionary representation of the SpasyTree with namespaces as keys.
        """
        if data_by_namespace is None:
            data_by_namespace = dict()

        current_node = node

        # recursion will stop once all nodes have been considered
        for child in current_node.children:
            # if there is a child that stores data
            if child is not None:
                if child.data:
                    for name in child.data:
                        string_split = name.split('/')
                        namespace = string_split[1]
                        data_to_add = name
                        # if already in the dictionary
                        if namespace in data_by_namespace:
                            data_by_namespace[namespace].add(data_to_add)
                        
                        # if the namespace doesn't exist in the dictionary, create it, and add the data
                        else:
                            data_by_namespace[namespace] = {data_to_add}
                # recurse
                else:
                    current_node = child
                    self.find_data_by_namespace(child, data_by_namespace)
    
        return data_by_namespace
    
    # TODO: it is possible it makes more sense for this to be part of Spasy
    def find_data_by_geocode(self, node: Node, data_by_geocode: dict | None = None) -> dict:
        """
        Reorganize the SpasyTree into a dictionary using geocodes.

        Args:
            node (Node): the root of the tree.
            data_by_geocode (dict | None, optional): a dictionary whose keys are geocodes and
                                                     values are named data. Defaults to None.

        Returns:
            dict: the dictionary representation of the SpasyTree with geocodes as keys.
        """
        
        if data_by_geocode is None:
            data_by_geocode = dict()

        current_node = node

        # recursion will stop once all nodes have been considered
        for child in current_node.children:
            # if there is a child that stores data
            if child is not None:
                if child.data:
                    for name in child.data:
                        string_split = name.split('/')
                        geocode = string_split[-1]
                        data_to_add = name
                        # if already in the dictionary
                        if geocode in data_by_geocode:
                            data_by_geocode[geocode].add(data_to_add)
                        
                        # if the geocode doesn't exist in the dictionary, create it, and add the data
                        else:
                            data_by_geocode[geocode] = {data_to_add}
                # recurse
                else:
                    current_node = child
                    self.find_data_by_geocode(child, data_by_geocode)
    
        return data_by_geocode
    
    def delete(self, node: Node, data_to_delete: str, current_position: int) -> bool:
        """
        Removes a specific piece of named data from the tree.

        Args:
            data_to_delete (str): The named data to be removed.
            current_position (int): The length of the geocode being considered.

        Returns:
            bool: True if it is safe to delete the data;
                  False otherwise.
        """
        # print(f'-------------RECURSING--------------')
        # print(f'Arguments passed: Node (geocode): {node.geocode}, current_position: {current_position}')
        # CASE 1: Trivial case - the data to be deleted isn't in the tree
        data_to_delete = data_to_delete.lower()
        delete_geocode = data_to_delete.split('/')[-1]
        if not self.find_data(data_to_delete):
            print(f"Sorry, but '{data_to_delete}' associated with the geocode '{delete_geocode}' is not in the tree.")
            return False

        #print(f'THIS IS THE NODE GEOCODE: {node.geocode}')
        siblings = node.number_children()
        #print(f"The current node, {node.geocode}, has {siblings} child(ren).")
        next_position = current_position + 1
        for i in range(len(node.children)):
            child_node = node.children[i]
            if child_node is None:
                continue
            # Case 2: the child node has the right geocode, but it has siblings, so we can't delete its parent node
            elif child_node is not None and delete_geocode in child_node.geocode:
                # print(f'---CASE 2---')
                # print(f'RIGHT GEOCODE WITH {siblings - 1} SIBLINGS.')
                # print(f'CHECKING... does the deletion geocode {delete_geocode} contain the child geocode, {child_node.geocode}?')
                # print(f'The child geocode, {child_node.geocode}, contains the deletion geocode, {delete_geocode}')
                # print(f'CHILD DATA BEFORE REMOVAL: {child_node.data}')
                child_node.delete_data(data_to_delete)
                self._add_to_recent_changes('delete', data_to_delete)
                #print(f'CHILD DATA AFTER REMOVAL: {child_node.data}')
                # if the child has no data, we set it to None, but we return True if there is no sibling, False otherwise
                #print(f'THE CHILD DATA: {child_node.data} AND SIBLINGS: {siblings - 1}')
                if not child_node.data and siblings > 1:
                    #print(f'DELETE ONLY THE CHILD.')
                    #print(f'THE CHILD: {child_node.geocode}')
                    node.remove_child(i)
                    self._update_merkle(node) # removing a child requires an update to hashes
                    return False
                elif not child_node.data:
                    #print('DELETE THE WHOLE NODE.')
                    #print(f'THE CURRENT NODE: {node}')
                    node.remove_children()
                    self._update_merkle(node)              
                    return True
                else:
                    # there is still data, so we calculate a new hash
                    self._update_merkle(child_node)  # the child remains, so we need to update the hash
                    return False
  
            # the next position stores the next geocode in the path to the geocode that holds the data
            elif child_node is not None:
                for code in child_node.geocode:
                    #print(f"THE CODE: {code[0:next_position]}, and the DELETE CODE: {delete_geocode[0:next_position]}")
                    if code[0:next_position] == delete_geocode[0:next_position]:
                        #print(f'THE CODE TO NEXT POSITION: {code[0:next_position]}')
                        #print(f'CHILD GEOCODE: {child_node.geocode}, NEXT POSITION: {next_position}')
                        safe_to_delete = self.delete(child_node, data_to_delete, next_position) 
                        # Case 3: if there is only one geocode, we can safely delete
                        if safe_to_delete:
                            #print(f'CHILD NODE GEOCODE: {node.geocode}')
                            #print(f'---CASE 3---')
                            node.remove_child(i)
                            self._update_merkle(node) 
                            #check if there are still children
                            for child in node.children:
                                if child is not None:
                                    #print(f'THE NODE STILL HAS CHILDREN, SO UNSAFE TO DELETE...')
                                    return False
                            return True
                        else:
                            return False
            else:
                return True

    ######### MUTATORS #########
    @root.setter
    def root(self, new_root: Node):
        self._root = new_root

    def _add_to_recent_changes(self, change_type: str, new_item: str) -> None:
        """
        Add tuples containing timestamps and new_items to a deque of recent changes.
        Deque provides queue-like behaviour, while dequeuing
        items when items are added to a full deque.
        """
        timestamp = time.time()
        recent_change = (timestamp, change_type, new_item)
        self.recent_changes.append(recent_change)
        
    def insert(self, named_data: str) -> None:
        """
        Add a node to the quadtree at the maximum depth of the tree.

        Args:
            insert_geocode (str): the location of the object
            named_data (str): the data to insert in the tree
            depth (int): the maximum depth of the tree 
        """
        current_node = self._root
        current_level = self._root.length_geocode()
        named_data = named_data.lower()
        insert_geocode = named_data.split('/')[-1].lower()
        #print(f'CURRENT DEPTH: {current_level}')
        start_level = current_level
        #print(f'START LEVEL: {start_level}')
        #print(f'INSERT GEOCODE: {insert_geocode}')

        # because all data is at leaf level, the geocode must match the height of the tree
        if self._max_depth != len(insert_geocode) - 1:
            print(f'The leaf level {self._max_depth} does not match the length of the geocode being inserted {len(insert_geocode) - 1}')
            return
        
        # if the set of geocodes doesn't contain the insertion geocode, then 
        # the named data object doesn't belong in this tree
        for geocode in current_node.geocode:
            # the object is from a higher level if there are fewer characters
            if start_level > len(insert_geocode):
                print(f"{insert_geocode} does not belong in the tree because it has a shorter geocode.") 
                return
            for i in range(start_level):
                if insert_geocode[i] != geocode[i]:
                    print(f"{insert_geocode} does not belong in this tree because it does not match the"
                          f" substring of the tree's geocode: {geocode}." )
                    return
        
        while current_level <= self._max_depth:
            found = False
            child_count = 0
            for child in current_node.children:
                child_count += 1
                if not found and child is not None:
                    for code in child.geocode:
                        # we have found the node to which this data belongs
                        if code == insert_geocode:
                            #print(f'{named_data} BEING INSERTED IN {code}')
                            child.insert_data(named_data)
                            self._add_to_recent_changes('insert', named_data)
                            self._update_merkle(child)
                            return
                        # we have found a parent of the node we wish to add data to
                        elif code in insert_geocode:
                            current_level += 1
                            current_node = child
                            #current_level += 1
                            found = True
                            #print(f'THE NODE WAS FOUND AND THE CURRENT LEVEL IS {current_level}')
                            break

            # we must create the child or add this geocode to an existing node
            if not found:
                current_level += 1  # we need to move down the tree         
                geocode_to_add = insert_geocode[0:current_level]
                
                node_to_insert = Node(geocode_to_add)  # the node to be added to the tree
                #print(f'ADDING CHILD: {node_to_insert.geocode} in NODE {current_node.geocode} at LEVEL {current_level} and DEPTH {current_level}')
                index = current_node.add_child(node_to_insert)
                current_node = current_node.children[index]
                
                # we haven't found the node, and we have reached the deepest level of the tree, 
                # so we should add the data
                if current_level > self._max_depth:
                    current_node.insert_data(named_data)
                    self._add_to_recent_changes('insert', named_data)
                    self._update_merkle(current_node)
    
  
    # TODO If a change is detected with the compare_merkle method, this method
    # ensures that you update just the branch that needs updating
    # Updating data is the same as adding data, but updating the tree is  
    # updating a branch
    def update(self, other_tree: Self) -> None:
        """
        Update the tree to reflect changes to the dataset.

        Args:
            other_tree (Self): An updated version of the dataset.
        """

    def _update_merkle(self, node: Node) -> None:
        """
        Update each of the Merkle hashes along a path (from leaf to root).
        """
        if node is self._root:
            node.generate_hash() # the tree is empty, so this will generate the empty string hash
        else:
            reached_root = False
            current_node = node
            # print(f'THE PARENT: {current_node.parent}')
            # print(f"BECAUSE IT'S THE ROOT: {current_node is self._root}")
            # print(f"THE LEAF NODE'S HASH: {current_node.hashcode}")
            while not reached_root:
                current_node.parent.generate_hash()
                current_node = current_node.parent
                if current_node is self._root:
                    reached_root = True

    ######### STRINGS #########
    def __str__(self) -> str:
        return f"Root: {self.root.geocode}"
    
    ######### BUILT-INS #########
    def __eq__(self, node_hashcode: Self) -> bool:
        return self._root.hashcode == node_hashcode

# Testing
if __name__ == '__main__':
    print('\nTesting SpasyTree...\n')

    # diagram example
    # paper_tree = SpasyTree(9, Node('dpwhwt'))
    # print(paper_tree.root)
    # paper_tree.insert('/alice/ball/0/dpwhwtsh00')
    # print(paper_tree.root)
    # paper_tree.insert('/bob/net/1/dpwhwtsh20')
    # print(paper_tree.root)
    # print(paper_tree.root.children[3].children[2].children[0].children[0].data)
    # paper_tree.delete(paper_tree.root, '/bob/net/1/dpwhwtsh20', paper_tree.root.length_geocode())
    # print(paper_tree.root)
    # print(paper_tree.root.children[3].children[2].children[0].children[0].data)
    # print(paper_tree.recent_changes)
    # deque_to_set = set(paper_tree.recent_changes)
    # print(deque_to_set)


    # hashing tests
    # print(f'\n######### TESTING MERKLE HASHING #########\n')
    # merkle_tree = SpasyTree(2, Node('a'))

    # # just the root
    # print(f'\n######### THE MERKLE TREE BEFORE ADDING DATA: #########\n')
    # print(merkle_tree.root)
    # merkle_tree.insert('/some/data/abc')
    # print(f'\n######### THE MERKLE TREE AFTER ADDING DATA: #########\n')
  
    # # add data
    # print(f'\n######### ADDING DATA #########\n')
    # merkle_tree.insert('/more/data/ab0')
    # merkle_tree.insert('/data/added/for/deletion/ab0')
    # print(f'\n######### THE TREE #########\n')
    # print(merkle_tree.root)
    
    # # find test
    # print(f'\n######### FIND DATA TESTING #########\n')
    # print(f'SEARCHING FOR DATA /data/added/for/deletion/ab0: {merkle_tree.find_data('/data/added/for/deletion/ab0')}')
    # print(f'THE ROOT CHILDREN: {merkle_tree.root.children}')
    # print(f'THEIR CHILDREN: {merkle_tree.root.children[1].children}')
    # print(f'SHOWING ALL AB0 DATA: {merkle_tree.root.children[1].children[0].data}')
    
    # # hashing after adding data
    # print(f'\n######### CHECKING HASHES AFTER NEW DATA #########\n')
    # root_hash = merkle_tree.root.hashcode
    # internal_hash = merkle_tree.root.children[1].hashcode
    # AB0_hash = merkle_tree.root.children[1].children[0].hashcode
    # ABC_hash = merkle_tree.root.children[1].children[1].hashcode
    # print(f'THE CURRENT ROOT HASH for geocode {merkle_tree.root.geocode}: {root_hash}')
    # print(f'THE CURRENT INTERNAL HASH for geocode {merkle_tree.root.children[1].geocode}: {internal_hash}')
    # print(f'THE CURRENT LEAF HASH for geocode {merkle_tree.root.children[1].children[0].geocode}: {AB0_hash}')
    # print(f'THE CURRENT LEAF HASH for geocode {merkle_tree.root.children[1].children[1].geocode}: {ABC_hash}')

    # # hashing after deletion
    # print(f'\n ######### HASHING WITH DELETION #########\n')
    # merkle_tree.delete(merkle_tree.root, '/data/added/for/deletion/ab0', merkle_tree.root.length_geocode())
    # print(merkle_tree.root)

    # # data after deleting one element
    # print(f'SHOWING ALL AB0 DATA AFTER DELETION OF /data/added/for/deletion: {merkle_tree.root.children[1].children[0].data}')
    # merkle_tree.delete(merkle_tree.root, '/data/added/for/deletion/ab0', merkle_tree.root.length_geocode())

    # #checking hashes after deleting some AB0 data
    # print(f'\n######### CHECKING HASHES AFTER DELETING DATA #########\n')
    # new_root_hash = merkle_tree.root.hashcode
    # new_internal_hash = merkle_tree.root.children[1].hashcode
    # new_AB0_hash = merkle_tree.root.children[1].children[0].hashcode
    # new_ABC_hash = merkle_tree.root.children[1].children[1].hashcode
    # print(f'THE CURRENT ROOT HASH for geocode {merkle_tree.root.geocode}: {new_root_hash}')
    # print(f'THE CURRENT INTERNAL HASH for geocode {merkle_tree.root.children[1].geocode}: {new_internal_hash}')
    # print(f'THE CURRENT LEAF HASH for geocode {merkle_tree.root.children[1].children[0].geocode}: {new_AB0_hash}')
    # print(f'THE CURRENT LEAF HASH for geocode {merkle_tree.root.children[1].children[1].geocode}: {new_ABC_hash}')
    # print(f'\n######### CHECKING THAT HASHES HAVE CHANGED #########\n')
    # print(f'THE ROOT HASH HAS CHANGED (should be True): {root_hash != new_root_hash}')
    # print(f'THE INTERNAL NODE HASH HAS CHANGED (should be True): {internal_hash != new_internal_hash}')
    # print(f'THE AB0 HASH HAS CHANGED (should be True): {AB0_hash != new_AB0_hash}')
    # print(f'THE ABC HASH HAS CHANGED (should be False): {ABC_hash != new_ABC_hash}')

    # # check after deleting all AB0 data
    # print(f'\n######### CHECKING HASHES AFTER DELETING ALL AB0 DATA #########\n')
    # merkle_tree.delete(merkle_tree.root, '/more/data/AB0', merkle_tree.root.length_geocode())
    # new_root_hash = merkle_tree.root.hashcode
    # new_internal_hash = merkle_tree.root.children[1].hashcode
    # new_ABC_hash = merkle_tree.root.children[1].children[1].hashcode
    # print(f'THE CURRENT ROOT HASH for geocode {merkle_tree.root.geocode}: {new_root_hash}')
    # print(f'THE CURRENT INTERNAL HASH for geocode {merkle_tree.root.children[1].geocode}: {new_internal_hash}')
    # print(f'THE CURRENT LEAF HASH for geocode {merkle_tree.root.children[1].children[1].geocode}: {new_ABC_hash}')

    # # make sure hashes have changed
    # print(f'\n######### CHECKING THAT HASHES HAVE CHANGED #########\n')
    # print(f'THE ROOT HASH HAS CHANGED (should be True): {root_hash != new_root_hash}')
    # print(f'THE INTERNAL NODE HASH HAS CHANGED (should be True): {internal_hash != new_internal_hash}')
    # print(f'THE ABC HASH HAS CHANGED (should be False): {ABC_hash != new_ABC_hash}')

    # # check after all data deleted (just the root left)
    # print(f'\n######### CHECKING HASHES AFTER DELETING ALL DATA #########\n')
    # merkle_tree.delete(merkle_tree.root, '/some/data/abc', merkle_tree.root.length_geocode())
    # last_root_hash = merkle_tree.root.hashcode
    # print(f'THE CURRENT ROOT HASH for geocode {merkle_tree.root.geocode}: {last_root_hash}')

    # # should just have one hash left
    # print(f'\n######### CHECKING THAT HASHES HAVE CHANGED #########\n')
    # print(f'THE ROOT HASH HAS CHANGED (should be True): {new_root_hash != last_root_hash}')
    # print(f'THE ROOT HASH: {last_root_hash}')

    # # just the root left
    # print(f'\n######### THE REMAINING TREE #########\n')
    # print(merkle_tree.root)

  
    # # testing hashes manually
    # print(f'\n######### MANUAL TESTING OF HASHES #########\n')
    # leaf_data = ['/some/data']
    # leaf_hash = '5fe5a125e93a82b7f1aad8b263fac21b6e9541e2ea136b656aa043231d32ee99'
    # hash_value = sha256(leaf_data[0].encode()).hexdigest()
    # print(f'{hash_value == leaf_hash}')
    # hash_value = sha256(hash_value.encode()).hexdigest()
    # parent_hash = 'b133840e29e9a7855063b30a7a819bd3ec3eea983d7f878ab6c8aa5e9fd17895'
    # print(f'{parent_hash == hash_value}')
    # second_leaf_hash = '4f89cb414164b9f0ce61686950044d9315007275c24dac698d5bbdc25ebeb946'
    # new_parent_hash = 'ca98b7d0f5f004d8231c5bc096c35befc59467a3855d6444b0a1a9a6b7e27c5e'
    # hash_value = sha256(second_leaf_hash.encode() + leaf_hash.encode()).hexdigest()
    # print(f'{new_parent_hash == hash_value}')
    # AB0_hash = '4f89cb414164b9f0ce61686950044d9315007275c24dac698d5bbdc25ebeb946'
    # ABC_hash = '5fe5a125e93a82b7f1aad8b263fac21b6e9541e2ea136b656aa043231d32ee99'
    # AB_hash = 'ca98b7d0f5f004d8231c5bc096c35befc59467a3855d6444b0a1a9a6b7e27c5e'
    # hash_value = sha256(AB0_hash.encode() + ABC_hash.encode()).hexdigest()
    # print(f'{AB_hash == hash_value}')
    # root_hash = '864ada23c63325bc183c42fbfa552b29d27aebd7dd87a6f480083590b4f5a7d2'
    # hash_value = sha256(AB_hash.encode()).hexdigest()
    # print(f'{root_hash == hash_value}')


    # # SpasyTree Tests
    # geohash_tree = SpasyTree(10, Node('dpwhwts'))
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsh000')
    # geohash_tree.insert('/some/data/DPWHWTSH001')
    # print(f'DATA: {geohash_tree.root.children[2].children[0].children[0].children[0].data}')
    # geohash_tree.insert('/some/more/data/dpwhwtsh009')
    # geohash_tree.insert('/some/testing/data/DPWHWTSH00H')
    # geohash_tree.insert('/some/data/DPWHWTSH00S')
    # geohash_tree.insert('/second/piece/of/data/DPWHWTSH00Z')
    # geohash_tree.insert('/extra/data/DPWHWTSZH00')
    # geohash_tree.insert('/some/data/DPWHWTSB214')
    # geohash_tree.insert('/another/data/piece/dpwhwts0202')
    # geohash_tree.insert('/more/data/dpwhwts1020')
    # geohash_tree.insert('/data/dpwhwtsmzp9')
    # print(f'\n######### FIND DATA BY NAMESPACE #########\n')
    # print(geohash_tree.find_data_by_namespace(geohash_tree.root))
    # print(geohash_tree.root)
    # print(f"FOUND '/some/data'(should include ['dpwhwtsb214', 'dpwhwtsh000', 'dpwhwtsh001', 'dpwhwtsh00s', 'dpwhwtsh00z']):"\
    #        f" {geohash_tree.find_data_without_geocode(geohash_tree.root, '/some/data')}")
    # print(f"FOUND /some/data/dpwhwtsh00z (should be False): {geohash_tree.find_data('/some/data/dpwhwtsh00z')}")
    # print(f"FOUND /some/data/dpwhwtsh001 (should be True): {geohash_tree.find_data('/some/data/dpwhwtsh001')}")
    # geohash_tree.delete(geohash_tree.root, '/extra/data/to/add/dpwhwtsh000', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/some/data/DPWHWTSH001', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/some/more/data/DPWHWTSH009', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/some/testing/data/DPWHWTSH00H', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/some/data/DPWHWTSH00S', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/second/piece/of/data/DPWHWTSH00Z', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/extra/data/DPWHWTSZH00', geohash_tree.root.length_geocode())
    
    # print(f"FOUND '/extra/data' (should be []): {geohash_tree.find_data_without_geocode(geohash_tree.root, '/extra/data')}")
    # geohash_tree.insert('/extra/data/dpwhwtsqp01')
    # print(f"FOUND '/extra/data' (should include ['dpwhwtsh001']):"
    #       f" {geohash_tree.find_data_without_geocode(geohash_tree.root, '/extra/data')}")
    # print(geohash_tree.root)
    # print(geohash_tree.recent_hashes)
    # print(f'\n######### FIND DATA BY NAMESPACE #########\n')
    # print(geohash_tree.find_data_by_namespace(geohash_tree.root))
    # print(f'\n######### THE TREE #########\n')
    # print(geohash_tree.root)



