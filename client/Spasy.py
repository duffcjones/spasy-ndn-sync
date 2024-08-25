from SpasyTree import *


class Spasy:
    """
    Spatial Sync (SPASY) is a Named Data Networking (NDN) Sync protocol meant for 
    use in augmented reality environments (and eventually the Metaverse). 

    Uses a SpasyTree to identify where all digital assets are within a given
    area and maintain synchronization of assets between users.

    Assumes SpasyTree root is at Geohash Level 6 and data is stored in leaves
    at Geohash Level 11.
    """

    def __init__(self, geocode: str) -> None:
        
        self._tree = SpasyTree(10, Node(geocode))
    
    ######### ACCESSORS #########
    @property
    def tree(self) -> SpasyTree:
        """Get or set the data SpasyTree data structure."""
        return self._tree
    
    ######### MUTATORS #########
    def replace_tree(self, replacement_tree: SpasyTree) -> None:
        """
        Replace the current SpasyTree with the newer version of the SpasyTree received
        via sending an Interest.

        Args:
            replacement_tree (SpasyTree): the newer version of the SpasyTree
        """
        self._tree = replacement_tree

    def add_data_to_tree(self, geocode: str, data_to_add: str) -> None:
        """
        Inserts named data in the SpasyTree.

        Args:
            data_to_add (str): the named data to be inserted in the SpasyTree
        """
        self._tree.insert(geocode, data_to_add)

    def remove_data_from_tree(self, delete_data: str, delete_geocode: str) -> None:
        """
        Deletes named data from the SpasyTree.

        Args:
            delete_data (str): the named data to delete.
            delete_geocode (str): the geocode from which the data should be deleted.
        """
        self._tree.delete(self._tree.root, delete_data, delete_geocode, self._tree.root.length_geocode())
    
    ######### OTHER #########
    def is_newer_tree(self, sync_tree_hash: str) -> bool:
        """
        When a Sync Interest is received, the hashcodes must be compared.

        Args:
            sync_tree_hash (str): the root hashcode of a SpasyTree

        Returns:
            bool: True if they match
                  False otherwise
        """
        if self._tree.root.hashcode == sync_tree_hash:
            print(f'The tree is already up-to-date.')
            return False
        elif sync_tree_hash in self._tree._recent_hashes:
            print(f'That is an older version of the tree.')
            return False
        else:
            print(f'This is a newer version of the tree. Send an Interest packet.')
            return True

    def search(self, data_to_find: str) -> list:
        """
        Find all of the geohashes in which the named data is stored.

        Args:
            data_to_find (str): the named data being sought.

        Returns:
            list: a list of geohashes where the data is stored.
        """
        return self._tree.find_data(self._tree.root, data_to_find)
    
    def gather_all_data(self) -> dict:
        return self._tree.find_data_by_namespace(self._tree.root)



    ######### NAMED DATA NETWORKING #########
        
    # TODO: build a method for constructing Sync Interests
    def create_sync_interest(self) -> None:
        pass

    # TODO: build a method for sending Interest packets to replace trees
    def send_interest(self) -> None:
        pass

    # TODO: build a method for receiving Data packets
    def receive_data(self) -> None:
        pass
    


# testing
if __name__ == '__main__':
    print(f'\nTesting SPASY...\n')
    # spasy = Spasy('DPWHWT')
    # other_tree = SpasyTree(10, Node('DPWHWT'))

    # # compare trees
    # print(f"\n######### COMPARE TREES BEFORE ADDING NEW DATA #########\n")
    # print(spasy.is_newer_tree(other_tree.root.hashcode))

    # # add data, then compare trees
    # print(f"\n######### COMPARE TREES AFTER ADDING NEW DATA #########\n")
    # other_tree.insert('DPWHWTSH000', '/data/test')
    # print(spasy.is_newer_tree(other_tree.root.hashcode))

    # # Sync related things to be added
    # print(f'\n######### SEND A SYNC INTEREST #########\n')

    # # replace tree
    # print(f'\n######### THE TREE BEFORE REPLACING IT #########\n')
    # print(spasy.tree.root)

    # spasy.replace_tree(other_tree)
    
    # print(f'\n######### THE TREE AFTER REPLACING IT #########\n')
    # print(spasy.tree.root)

    # # add, delete and find data
    # spasy.add_data_to_tree('DPWHWTSH401', '/add/data')
    # print(f'\n########## THE TREE WITH ADDED DATA #########\n')
    # print(spasy.tree.root)
    # print(f"FIND '/add/data' (should be ['DPWHWTSH000', 'DPWHWTSH401']): {spasy.search('/add/data')}")
    # print(f"FIND ALL DATA: {spasy.gather_all_data()}")
    # spasy.remove_data_from_tree('/data/test', 'DPWHWTSH000')
    # print(f'\n########## THE TREE WITH DATA REMOVED #########\n')
    # print(spasy.tree.root)
    # print(f"FIND '/add/data' (should be ['DPWHWTSH000', 'DPWHWTSH401']): {spasy.search('/add/data')}")
    # print(f"FIND '/data/test' (should be []): {spasy.search('/data/test')}")

    



    

