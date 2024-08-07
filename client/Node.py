from typing import Self, Optional

class Node:
    """
    Build a node for a Merkle quadtree. Updates to a Node's 
    Merkle hash indicate changes in the data stored in that Node.
    """

    def __init__(self, merkle: str, 
                 geocode: set,
                 child_node_1: Optional[Self]=None, 
                 child_node_2: Optional[Self]=None, 
                 child_node_3: Optional[Self]=None, 
                 child_node_4: Optional[Self]=None) -> None:
        """
        Args:
            merkle (str): the node's Merkle hash
            geocode (set): a set containing the geospatial index/indices 
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
        child_dictionary = {}
        self._child_node_1 = child_node_1
        self._child_node_2 = child_node_2
        self._child_node_3 = child_node_3
        self._child_node_4 = child_node_4
        self._data = list()

    ######### ACCESSORS #########
    @property
    def merkle(self) -> str:
        """Get or set the current Merkle hash."""
        return self._merkle

    @property
    def geocode(self) -> set:
        """Get or set the set of geospatial indices."""
        return self._geocode
    
    @property
    def child_node_1(self) -> Self:
        """Get, set, or delete the first child."""
        return self._child_node_1
    
    @property
    def child_node_2(self) -> Self:
        """Get, set, or delete the second child."""
        return self._child_node_2
    
    @property
    def child_node_3(self) -> Self:
        """Get, set, or delete the third child."""
        return self._child_node_3
    
    @property
    def child_node_4(self) -> Self:
        """Get, set, or delete the fourth child."""
        return self._child_node_4
    
    @property
    def data(self) -> Self:
        """Get, set, or delete the list of assets."""
        return self._data
    
    def get_children(self) -> list:
        """Get a list containing all of the Node's children."""
        children = [self._child_node_1,
                    self._child_node_2,
                    self._child_node_3,
                    self._child_node_4
                    ]
        return children
    
    def number_children(self) -> int:
        """Determine how many children hold data."""
        count = 0
        for child in self.get_children():
            if child is not None:
                count += 1
        return count

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
    def geocode(self, geocode: set) -> None:
        self._geocode = geocode

    @child_node_1.setter
    def child_node_1(self, hash: str) -> None:
        self._child_node_1 = hash

    @child_node_2.setter
    def child_node_2(self, hash: str) -> None:
        self._child_node_2 = hash

    @child_node_3.setter
    def child_node_3(self, hash: str) -> None:
        self._child_node_3 = hash
    
    @child_node_4.setter
    def child_node_4(self, hash: str) -> None:
        self._child_node_4 = hash

    def add_geocode(self, geocode: str) -> None:
        """Add a geocode to the set of geocodes associated with this node."""
        self._geocode.add(geocode)

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
    @child_node_1.deleter
    def child_node_1(self) -> None:
        self._child_node_1 = None
    
    @child_node_2.deleter
    def child_node_2(self) -> None:
        self._child_node_2 = None
    
    @child_node_3.deleter
    def child_node_3(self) -> None:
        self._child_node_3 = None
    
    @child_node_4.deleter
    def child_node_4(self) -> None:
        self._child_node_4 = None

    def remove_children(self) -> None:
        """
        Remove all children from the node. 
        Turns the node into a leaf node.
        """
        self.child_node_1 = None
        self.child_node_2 = None
        self.child_node_3 = None
        self.child_node_4 = None

    ######### COMPARISONS #########
    def __eq__(self, node: Self) -> bool:
        """Check if another Node has the same Merkle hash as this Node."""
        return self._merkle == node.merkle

    ######### STRINGS #########
    def __str__(self) -> str:
        return f'\nNode hash: {self.merkle}\nNode geocode: {self.geocode}' +\
              ''.join(f'\nChild: {child}' for child in self.get_children())
    
    def __repr__(self) -> str:
        return f"Node({self.merkle}, {self.geocode}, {repr(self.child_node_1)},"\
            f" {repr(self.child_node_2)}, {repr(self.child_node_3)}, {repr(self.child_node_4)})"
        
# TESTING
if __name__ == '__main__':
    print(f'Testing Node class...\n')
    node = Node('678e749011f8a911f011e105c618db898a71f8759929cc9a9ebcfe7b125870ee', {'ABCD', '1234'})
    print(f'\n######### After construction #########\n {node}')
    node.child_node_1 = Node('some_hash', 'EFGH')
    node.child_node_3 = Node('some_other_hash', 'IJKL')
    node.child_node_2 = Node('more hashing', 'MNOP')
    print(f'\n######### After adding children #########\n {node}')
    del(node.child_node_1)
    print(f'\n######### After deleting the front_left child #########\n {node}')
    node.remove_children()
    node.child_node_3 = Node('last_hash', 'QRST')
    print(f'\n######### After removing all children and adding' 
          f' a back_left child: #########\n {node}')
    print(f'\n######### Programmer representation #########\n\n {repr(node)}')
    node.child_node_2 = Node('last_hash', 'EFGH')
    node.child_node_4 = Node('some_hash', 'EFGH')
    print(f'\n######### Comparison tests #########\n')
    print(f'Child 3 and Child 4 have the same Merkle hash? {node.child_node_3 == node.child_node_4}')
    print(f'Child 3 and Child 2 have the same Merkle hash? {node.child_node_3 == node.child_node_2}')
    print(f'\n######### Geocode Test #########\n')
    for child in node.get_children():
        if child is not None:
            print(f"The Node's geocode is: {child.geocode}")
        else:
            print(f"The Node is empty.")
    print(f'\n######### Testing data insertion #########\n')
    node.child_node_2.insert_data('/Name/to/add/to/list')
    node.child_node_2.insert_data('/name/To/add/to/list')
    node.child_node_2.insert_data('/name/to/Add/to/list/again/2')
    node.child_node_2.insert_data('/some/new/Name/001')
    node.child_node_2.insert_data('/some/NeW/name/002')
    node.child_node_2.insert_data('/name/to/Add/to/list/2')
    node.child_node_2.insert_data('/name/to/add/to/list/1')
    node.child_node_2.insert_data('/some/new/name')
    print(f'Data stored in Child 2: {node.child_node_2.data}')
    node.child_node_2.delete_data('/some/new/name/002')
    print(f"Data stored in Child 2 after deletion of '/some/new/name/002': {node.child_node_2.data}")
    print(f'Geocode: {node.geocode}')
