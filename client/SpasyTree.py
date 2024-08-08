from Node import *

class SpasyTree:
    """
    A Merkle quadtree used as a dataset representation for 
    Spatial Sync (SPASY), a Named Data Networking (NDN) Sync 
    protocol.
    """

    def __init__(self, max_depth: int, node: Node=None) -> None:
        """
        Args:
            node (Node, optional): a node object representing the tree's root. 
                                   Defaults to None.
        """
        self._root = node 
        self._max_depth = max_depth
        self._recent_changes = list() # TODO: will hold a list of recent Merkle hashes
 
    ######### ACCESSORS #########
    @property
    def root(self) -> Node:
        """Get, set, or delete the tree's root."""
        return self._root
    
    @property
    def max_depth(self) -> int:
        """
        Get the tree's maximum allowable depth.
        This will be based on the chosen geocoding approach.
        It will determine how granular the tree is.
        """
        return self._max_depth
    
    def find_data(self, node: Node, named_data: str, geocode_list: list=[]) -> list:
        """
        A traversal that returns the geocodes of all instances 
        of a piece of named data within the tree.

        Args:
            node (Node): The node being searched.
            named_data (str): The data being sought.
            geocode_list (list): A list of geocodes in which the data is located.
                                 Defaults to being empty.

        Returns:
            list: A list of geocodes identifying where the data is located.
        """
        # TODO: right now, this is built for Geohash, so it will return a set of geocodes,
        # as the data is associated with that set right now, not a specific geocode
        
        if node is not None:
            if node.in_data(named_data):
                # because we are using buckets, we will add each possible geocode individually
                for code in node.geocode:
                    if code not in geocode_list:
                        geocode_list.append(code)
            else:
                for child in node.children.values():
                    self.find_data(child, named_data, geocode_list)

        return geocode_list
        
    

      # TODO: Consider whether there is a better way of handling this
    # right now, we need a geocode to avoid the deletion of duplicate data
    def delete(self, node: Node, data_to_delete: str, delete_geocode: str, current_position: int) -> bool:
        """
        Removes a specific piece of named data from a geocode in the tree.

        Args:
            data_to_delete (str): The named data to be removed.
            delete_geocode (str): The geocode the named data is associated with.
            current_position (int): The length of the geocode being considered.

        Returns:
            bool: True if it is safe to delete the data;
                  False otherwise.
        """
        print(f'-------------RECURSING--------------')
        print(f'Arguments passed: Node (geocode): {node.geocode}, current_position: {current_position}')
        # CASE 1: Trivial case - the data to be deleted isn't in the tree
        if delete_geocode not in self.find_data(node, data_to_delete):
            print(f"Sorry, but '{data_to_delete}' associated with the geocode '{delete_geocode}' is not in the tree.")
            return False

        print(f'THIS IS THE NODE GEOCODE: {node.geocode}')
        siblings = node.number_children()
        print(f"The current node, {node.geocode}, has {siblings} child(ren).")
        next_position = current_position + 1
        for child_key, child_node in node.children.items():
            print(f'CHECKING... does the deletion geocode {delete_geocode} contain the child geocode, {child_node.geocode}?')
            # the child node has the right geocode, but it has siblings, so we can't delete its parent node
            if child_node is not None and delete_geocode in child_node.geocode:
                print(f'The child geocode, {child_node.geocode}, contains the deletion geocode, {delete_geocode}')
                child_node.delete_data(data_to_delete)
                print(f'Child data: {child_node.data}')
                # if the child has no data, we set it to None, but we return True if there is no sibling, False otherwise
                print(f'THE CHILD DATA: {child_node.data} AND SIBLINGS: {siblings}')
                if not child_node.data and siblings > 1:
                    print(f'DELETE ONLY THE CHILD.')
                    print(f'THE CHILD: {child_node.geocode}')
                    node.remove_child(child_key)
                    return False
                elif not child_node.data:
                    print('DELETE THE WHOLE NODE.')
                    print(f'THE CURRENT NODE: {node}')
                    node.remove_children()
                    return True
  
            # the next position stores the next geocode in the path to the geocode that holds the data
            elif child_node is not None:
                for code in child_node.geocode:
                    print(f"THE CODE: {code[0:next_position]}, and the CHILD CODE: {delete_geocode[0:next_position]}")
                    if code[0:next_position] == delete_geocode[0:next_position]:
                        print(f'Child: {child_node.geocode}, current position: {current_position}')
                        safe_to_delete = self.delete(child_node, data_to_delete, delete_geocode, next_position) 

                        # if there is only one geocode, we can safely delete
                        if safe_to_delete and len(child_node.geocode) < 2:
                            print(f'SAFE TO DELETE: {node.geocode}')
                            node.remove_child(child_key)
                            print(f'THE REMAINING NODE: {node.geocode}')
                            return True
                        else:
                            return False
            
            else:
                print(f"EITHER THE CHILD IS NONE, OR THE GEOCODE DOESN'T WORK")
                return True


    # TODO
    def find_all_in_namespace(self, node: Node, namespace: str, named_data: dict) -> dict:
        """
        Create a dictionary that contains all data in a specific namespace.

        Args:
            node (Node): 
            namespace (str): _description_
            named_data (dict): _description_

        Returns:
            dict: _description_
        """
    
    ######### MUTATORS #########
    @root.setter
    def root(self, new_root: Node):
        self._root = new_root
    
    # TODO: may want to rework this to be a proper trie (e.g, Node 1 - 'A', Node 2 -'B', Node 3 - 'C')
    def insert(self, insert_geocode: str, named_data: str) -> None:
        """
        Add a node to the quadtree at the maximum depth of the tree.

        Args:
            insert_geocode (str): the location of the object
            named_data (str): the data to insert in the tree
            depth (int): the maximum depth of the tree 
        """
        current_node = self._root
        current_depth = 0
        start_level = current_node.length_geocode()
        print(f'The geocode to insert is: {insert_geocode}')
        
        # if the set of geocodes doesn't contain the insertion geocode, then 
        # the named data object doesn't belong in this tree
        # TODO: This is true of Geohash, but will have to double-check on S2
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
        
        while current_depth < self._max_depth:
            found = False
            child_count = 0
            for child in current_node.children.values():
                child_count += 1
                if not found and child is not None:
                    for code in child.geocode:
                        # we have found the node to which this data belongs
                        if code == insert_geocode:
                            child.insert_data(named_data)
                            return
                        # we have found a parent of the node we wish to add data to
                        elif code in insert_geocode:
                            current_level = start_level + current_depth
                            current_character = insert_geocode[current_level - 1]
                            current_node = child
                            current_depth += 1
                            found = True
                            break

            # we must create the child or add this geocode to an existing node
            if not found:
                current_depth += 1  # we need to move down the tree         
                current_level = start_level + current_depth  # allows us to obtain the current character
                current_character = insert_geocode[current_level - 1]
                geocode_to_add = insert_geocode[0:current_level]
                
                # TODO: create a proper Merkle hash for the node
                node_to_insert = Node('', [geocode_to_add])  # the node to be added to the tree

                # TODO: these conditions are currently hardcoded to Geohash and will have to be made generic
                if current_character in '01234567':
                    if 'child1' in current_node.children:
                        current_node.children['child1'].add_geocode(geocode_to_add)
                    else:
                        current_node.children['child1'] = node_to_insert
                    current_node = current_node.children['child1']
                elif current_character in '89BCDEFG':
                    if 'child2' in current_node.children:
                        print(f'TYPE: {current_node.children['child2'].geocode}')
                        current_node.children['child2'].add_geocode(geocode_to_add)
                    else:
                        current_node.children['child2'] = node_to_insert
                    current_node = current_node.children['child2']
                elif current_character in 'HJKMNPQR':
                    if 'child3' in current_node.children:
                        current_node.children['child3'].add_geocode(geocode_to_add)
                    else:
                        current_node.children['child3'] = node_to_insert
                    current_node = current_node.children['child3']
                elif current_character in 'STUVWXYZ':
                    if 'child4' in current_node.children:
                        current_node.children['child4'].add_geocode(geocode_to_add)
                    else:
                        current_node.children['child4'] = node_to_insert
                    current_node = current_node.children['child4']
                else:
                    print("That is not a valid geocode.")

                # we haven't found the node, and we have reached the deepest level of the tree, 
                # so we should add the data (occurs when we have to add the deepest node)
                if current_depth == self.max_depth:
                    current_node.insert_data(named_data)

        
    # TODO If a change is detected with the compare_merkle method, this method
    # ensures that you update just the branch that needs updating
    # Will make use of the insert() method
    def update_data(self, other_tree: Self) -> None:
        """
        Update the tree to reflect changes to the dataset.

        Args:
            other_tree (Self): An updated version of the dataset.
        """


    # TODO compare the merkle hashes of this tree with another to determine if 
    # updates are necessary
    def compare_merkle(self, hash: str) -> bool:
        """
        Compare two Merkle hashes to see if there have been changes.

        Args:
            hash (str): Another Node's Merkle hash value.

        Returns:
            bool: True if different;
                  False otherwise.
        """


    # TODO: update the Merkle string associated with a node in the tree
    def update_merkle(self) -> None:
        """
        Update each of the Merkle hashes along a path (from leaf to root)
        """
        pass


    ######### STRINGS #########
    def __str__(self) -> str:
        return f"Root: {self.root.geocode}"


# Testing
if __name__ == '__main__':
    print('Testing SpasyTree class...\n')

    print(f'\n######### Test a SpasyTree with a Geohash #########\n')
    node = Node('root_hash', {'DPWHWTS'})
    # node.children['child1'] = Node('level_1_child_1_hash', ['DPWHWTS0'])
    # node.children['child2'] = Node('level_1_child_2_hash', ['DPWHWTS8'])
    # node.children['child3'] = Node('level_1_child_3_hash', ['DPWHWTSH'])
    # node.children['child4'] = Node('level_1_child_4_hash', ['DPWHWTSS'])
    geohash_tree = SpasyTree(4, node)
    geohash_tree.insert('DPWHWTSH000', '/data/to/add')
    geohash_tree.insert('DPWHWTSB1XQ', '/some/data')
    geohash_tree.insert('DPWHWTSB1XR', '/test/data')
    geohash_tree.insert('DPWHWTSB1XC', '/testing/more/data')
    geohash_tree.insert('DPWHWTS89C3', '/some/data')
    geohash_tree.insert('DPWHWTSH000', '/a/second/piece/of/data')
    print(f'\n######### SpasyTree root data #########\n')
    print(geohash_tree.root.children['child3'].children['child1'].children['child1'].children['child1'].data)
    print(geohash_tree.root.children['child2'].children['child1'].children['child4'].children['child3'].data)
    print(geohash_tree.root.children['child2'].children['child2'].children['child2'].children['child1'].data)
    # even though '/some/data' is only stored twice, it will show three geocodes, as the XQ and XR geocodes are in the same node
    print(f"Should be ['DPWHWTSB1XQ','DPWHWTSB1XR','DPWHWTS89C3']: {geohash_tree.find_data(geohash_tree.root, '/some/data', [])}")
    #print(geohash_tree.root)
    print(f'Before removal: {geohash_tree.root.children['child2'].children['child2'].children['child2'].children['child1'].data}')
    print(f'\n#### DELETING ####\n')
    geohash_tree.delete(geohash_tree.root, '/some/data', 'DPWHWTS89C3', geohash_tree.root.length_geocode())
    geohash_tree.delete(geohash_tree.root, '/some/data', 'DPWHWTSB1XQ', geohash_tree.root.length_geocode())
    geohash_tree.delete(geohash_tree.root, '/test/data', 'DPWHWTSB1XR', geohash_tree.root.length_geocode())
    geohash_tree.delete(geohash_tree.root, '/testing/more/data', 'DPWHWTSB1XC', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/data/to/add', 'DPWHWTSH000', geohash_tree.root.length_geocode())
    # geohash_tree.delete(geohash_tree.root, '/a/second/piece/of/data', 'DPWHWTSH000', geohash_tree.root.length_geocode())


    print(f'\n#### THE REMAINING TREE ####\n')
    #print(f'After removal: {geohash_tree.root.children['child2'].children['child2'].children['child2'].children['child1'].data}')
    print(geohash_tree.root)
    
    # print(f'\n######### Test a SpasyTree with short geocodes #########\n')
    # node_short = Node('root', ['A'])
    # short_tree = SpasyTree(2, node_short)
    # short_tree.insert('ABC', '/find/test')
    # short_tree.insert('A7D', '/some/data')
    # short_tree.insert('AB7', '/testing')
    # short_tree.insert('AB5', '/shared/parent')
    # short_tree.insert('7GH', '/should/not/work')
    # short_tree.insert('AQX', '/find/test')
    # print(f'\n######### SpasyTree #########\n')
    # print(short_tree.root)
    # print(f"\n######### Data stored in the node AB(0-7) #########\n")
    # print(short_tree.root.children['child2'].children['child1'].data)
    # print(f"\n######### Data stored in 'AQX' #########\n")
    # print(f"Should be ['/last/test'], and it is: {short_tree.root.children['child3'].children['child4'].data}")
    # print(f"\n######### Testing find_data #########\n")
    # print(f"Should be ['ABC', 'AQX'], and it is: {short_tree.find_data(short_tree.root, '/find/test')}")
    # short_tree.delete(short_tree.root, '/find/test', 'AQX', short_tree.root.length_geocode())
    # print(f'\n######### Tree after deletion #########\n')
    # print(short_tree.root)
    

    # print(f'\n######### Find data #########\n')
    # find_node = Node('root', ['A'])
    # find_tree = SpasyTree(2, find_node)
    # find_tree.insert('ABC', '/find/test')
    # print(f'The data is: {find_tree.root.children['child2'].children['child2'].data}')
    # print(f'The geocode length is: {find_tree.root.children['child2'].children['child2'].length_geocode()}')
    # print(f"Should be []: {find_tree.find_data(find_tree.root, '/not/in/tree')}")
    # print(f"Should be ['ABC']: {find_tree.find_data(find_tree.root, '/find/test')}")
    # print(f"Should be False: {find_tree.delete(find_tree.root, '/find/test', 'ABD', find_tree.root.length_geocode())}")
    # print(f"Should be True: {find_tree.delete(find_tree.root, '/find/test', 'ABC', find_tree.root.length_geocode())}")
    # #print(f"After being removed, the data is: {find_tree.root.children['child2'].children['child2'].data}")
    # print(f"\n######### The resulting tree #########\n")
    # print(find_tree.root)