from typing import Self, Optional

class Node:
    """
    Build a node for a Merkle quadtree. Updates to a Node's 
    Merkle hash indicate changes in the data stored in that Node.
    """

    def __init__(self, merkle: str, 
                 geocode: list=[]) -> None:
        """
        Args:
            merkle (str): the node's Merkle hash
            geocode (list): a list containing the geospatial index/indices 
                           associated with the Node
            child_node_1 (Optional[Self], optional): contains a geospatial index 
                                                     one level deeper than 
                                                     the current Node. Defaults to None.
            child_node_2 (Optional[Self], optional): contains a geospatial index 
                                                     one level deeper than 
                                                     the current Node. Defaults to None.
            child_node_3 (Optional[Self], optional): contains a geospatial index 
                                                     one level deeper than 
                                                     the current Node. Defaults to None.
            child_node_4 (Optional[Self], optional): contains a geospatial index 
                                                     one level deeper than 
                                                     the current Node. Defaults to None.
        """
        self._merkle = merkle
        self._geocode = geocode
        # TODO 
        self._children = dict()
        self._data = list()

    ######### ACCESSORS #########
    @property
    def merkle(self) -> str:
        """Get or set the current Merkle hash."""
        return self._merkle

    @property
    def geocode(self) -> list:
        """Get or set the list of geospatial indices."""
        return self._geocode
    
    @property
    def children(self) -> dict:
        """Get the node's children."""
        return self._children
    
    @property
    def data(self) -> list:
        """Get, set, or delete the list of assets."""
        return self._data
    
    def number_children(self) -> int:
        """Determine how many children hold data."""
        return len(self._children)
    
    def in_data(self, named_data: str) -> bool:
        """
        Determine if the string being sought is in the node's 
        list of data. 

        Returns:
            bool: True if the data is in the node's data list;
                  False otherwise
        """
        for element in self._data:
            if element == named_data.lower():
                return True
        
        return False
    

    # TODO: grab element [0] instead
    def length_geocode(self) -> int:
        length = 0
        if self._geocode:
            for element in self._geocode:
                length = len(element) 
                break
        return length
    
    ######### MUTATORS #########
    @merkle.setter
    def merkle(self, hash: str) -> None:
        self._merkle = hash

    @geocode.setter
    def geocode(self, geocode: list) -> None:
        self._geocode = geocode

    def add_geocode(self, geocode: str) -> None:
        """Add a geocode to the set of geocodes associated with this node."""
        if geocode not in self._geocode:
            self._geocode.append(geocode)

    def delete_data(self, named_data: str) -> None:
        """Delete a piece of named data from the node."""
        
        if named_data.lower() in self._data:
            self._data.remove(named_data)

    def insert_data(self, named_data: str) -> None:
        """
        Inserts new named data into the list of data. 
        Checks if the new data is a version of previous data or new data.
        The expectation is that the final value in a hierarchical named data
        string is fully numeric only when being used to indicate a version
        number or timestamp.

        Args:
            named_data (str): the named data object's name
        """
        existing_data = self._data
        named_data = named_data.lower() # all names added to a list should follow the same format
        
        # if the list is empty, we can safely insert the data
        if len(existing_data) == 0:
            self._data.append(named_data)
        else:
            # split the string to be inserted; get a version number if there is one
            split_data = named_data.split('/')
            if split_data[-1].isnumeric():
                data_to_check = ''.join(split_data[0:-1])
                insert_version = split_data[-1]
            else:
                data_to_check = ''.join(split_data)
                insert_version = None

            for i in range(len(existing_data)):
                # the data is already stored; do nothing
                if existing_data[i] == named_data:
                    return
                
                # split the named data element in the list and check if there is a version
                element_split = existing_data[i].split('/')
                if element_split[-1].isnumeric():
                    element_without_version = ''.join(element_split[0:-1])
                    current_version = element_split[-1]
                else:
                    element_without_version = ''.join(element_split)
                    current_version = None

                # the hierarchical names match
                if element_without_version == data_to_check:
                    if insert_version is not None:
                        if current_version is not None:
                            # the current version is older than the one to be inserted
                            if current_version < insert_version:
                                self._data[i] = named_data
                                return
                            elif current_version >= insert_version:
                                return
                        # current version must be older, as it didn't have a version number
                        elif current_version is None:
                            self._data[i] = named_data
                            return
                    # the current version is already up-to-date   
                    elif current_version is not None:
                        return
                    
            # the data is new and should be added
            self._data.append(named_data)

    ######### DELETERS #########
    def remove_children(self) -> None:
        """
        Remove all children from the node. 
        Turns the node into a leaf node.
        """
        self._children = {}

    def remove_child(self, child_to_remove: str) -> None:

        del self._children[child_to_remove]

    ######### COMPARISONS #########
    def __eq__(self, node: Self) -> bool:
        """Check if another Node has the same Merkle hash as this Node."""
        return self._merkle == node.merkle

    ######### STRINGS #########
    def __str__(self) -> str:
        return f'\nNode hash: {self.merkle}\nNode geocode: {self.geocode}' +\
              ''.join(f'\nChild: {child}' for child in self._children.values())
        
# TESTING
if __name__ == '__main__':
    print(f'Testing Node class...\n')
    node = Node('678e749011f8a911f011e105c618db898a71f8759929cc9a9ebcfe7b125870ee', {'ABCD', '1234'})
    print(f'\n######### After construction #########\n {node}')
    node.children['child1'] = Node('some_hash', 'EFGH')
    node.children['child2'] = Node('some_other_hash', 'IJKL')
    node.children['child3'] = Node('more hashing', 'MNOP')
    print(f'\n######### After adding children #########\n {node}')
    node.children.pop('child3')
    print(f'\n######### After deleting the front_left child #########\n {node}')
    node.remove_children()
    node.children['child3'] = Node('last_hash', 'QRST')
    print(f'\n######### After removing all children and adding' 
          f' a child: #########\n {node}')
    node.children['child2'] = Node('last_hash', 'EFGH')
    node.children['child4'] = Node('some_hash', 'EFGH')
    print(f'\n######### Comparison tests #########\n')
    print(f'Child 3 and Child 4 have the same Merkle hash? {node.children['child3'].merkle == node.children['child4'].merkle}')
    print(f'Child 3 and Child 2 have the same Merkle hash? {node.children['child3'].merkle == node.children['child2'].merkle}')
    print(f'\n######### Geocode Test #########\n')
    for child in node.children:
        print(f'The child: {child}')
        if child is not None:
            print(f"The Node's geocode is: {node.children[child].geocode}")
        else:
            print(f"The Node is empty.")
    print(f'\n######### Testing data insertion #########\n')
    node.children['child2'].insert_data('/Name/to/add/to/list')
    node.children['child2'].insert_data('/name/To/add/to/list')
    node.children['child2'].insert_data('/name/to/Add/to/list/again/2')
    node.children['child2'].insert_data('/some/new/Name/001')
    node.children['child2'].insert_data('/some/NeW/name/002')
    node.children['child2'].insert_data('/name/to/Add/to/list/2')
    node.children['child2'].insert_data('/name/to/add/to/list/1')
    node.children['child2'].insert_data('/some/new/name')
    print(f'Data stored in Child 2: {node.children['child2'].data}')
    node.children['child2'].delete_data('/some/new/name/002')
    print(f"Data stored in Child 2 after deletion of '/some/new/name/002': {node.children['child2'].data}")
    print(f'Geocode: {node.geocode}')
