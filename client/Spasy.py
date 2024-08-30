from SpasyTree import *
import time
import sys
from pympler import asizeof

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

    def add_data_to_tree(self, data_to_add: str) -> None:
        """
        Inserts named data in the SpasyTree.

        Args:
            data_to_add (str): the named data to be inserted in the SpasyTree
        """
        self._tree.insert(data_to_add)

    def remove_data_from_tree(self, delete_data: str) -> None:
        """
        Deletes named data from the SpasyTree.

        Args:
            delete_data (str): the named data to delete.
            delete_geocode (str): the geocode from which the data should be deleted.
        """
        self._tree.delete(self._tree.root, delete_data, self._tree.root.length_geocode())
    
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

    def search(self, data_to_find: str) -> bool:
        """
        Find all of the geohashes in which the named data is stored.

        Args:
            data_to_find (str): the named data being sought.

        Returns:
            list: a list of geohashes where the data is stored.
        """
        return self._tree.find_data(data_to_find)
    
    def search_without_geocode(self, data_to_find: str, geocode_list: list | None = None) -> list:

        return self._tree.find_data_without_geocode(self._tree.root, data_to_find, geocode_list)
    
    def gather_all_data_by_namespace(self) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by
        namespace.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into namespaces  
        """
        return self._tree.find_data_by_namespace(self._tree.root)
    

    def gather_all_data_by_geocode(self) -> dict:

        return self._tree.find_data_by_geocode(self._tree.root)
    

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
    # spasy = Spasy('dpwhwts')
    # other_tree = SpasyTree(10, Node('dpwhwts'))

    # # compare trees
    # print(f"\n######### COMPARE TREES BEFORE ADDING NEW DATA #########\n")
    # start = time.time()
    # print(spasy.is_newer_tree(other_tree.root.hashcode))
    # end = time.time()
    # print(end - start)

    # # add data, then compare trees
    # print(f"\n######### COMPARE TREES AFTER ADDING NEW DATA #########\n")
    # other_tree.insert('/data/test/dpwhwtsh000')
    # print(spasy.is_newer_tree(other_tree.root.hashcode))

    # # Sync related things to be added
    # print(f'\n######### SEND A SYNC INTEREST #########\n')

    # # replace tree
    # print(f'\n######### THE TREE BEFORE REPLACING IT #########\n')
    # print(spasy.tree.root)

    # geohash_tree = SpasyTree(10, Node('dpwhwts'))
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsh300')
    # geohash_tree.insert('/some/data/dpwhwtsh001')
    # geohash_tree.insert('/some/more/data/dpwhwtsh009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsh00h')
    # geohash_tree.insert('/some/data/dpwhwtsh00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsh000')
    # geohash_tree.insert('/extra/data/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwts0214')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsp000')
    # geohash_tree.insert('/some/data/dpwhwtsz001')
    # geohash_tree.insert('/some/more/data/dpwhwtsb009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsn00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwts1000')
    # geohash_tree.insert('/extra/data/dpwhwts2000')
    # geohash_tree.insert('/some/data/dpwhwts9214')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwtsh001')
    # geohash_tree.insert('/some/more/data/dpwhwtsh009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsh00h')
    # geohash_tree.insert('/some/data/dpwhwtshpqs')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsprtu')
    # geohash_tree.insert('/extra/data/dpwhwts9bzx')
    # geohash_tree.insert('/some/data/dpwhwts/9214')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtspc18')
    # geohash_tree.insert('/some/data/dpwhwtspcdq')
    # geohash_tree.insert('/some/more/data/dpwhwtsmnz4')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsp00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsq000')
    # geohash_tree.insert('/extra/data/dpwhwtsvw0z')
    # geohash_tree.insert('/some/data/dpwhwtsm0p1')
    # # print(geohash_tree.root)

    # start = time.time()
    # spasy.is_newer_tree(geohash_tree.root.hashcode)
    # spasy.replace_tree(geohash_tree)
    # end = time.time()
    # print(f'end: {end}, start: {start}; calculation = {end - start}')
    # print(f'The tree contains {asizeof.asizeof(geohash_tree)} bytes.')
    # print(f'\n######### THE TREE AFTER REPLACING IT #########\n')

    # # add, delete and find data
    # spasy.add_data_to_tree('/add/data/dpwhwtsh401')
    # print(f'\n########## THE TREE WITH ADDED DATA #########\n')
    # #print(spasy.tree.root)
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search('/add/data')}")
    # spasy.add_data_to_tree('/data/test/dpwhwtsb900')
    # print(f'\n######### THE TREE BEFORE REMOVAL #########\n')
    # print(spasy.tree.root)
    # spasy.remove_data_from_tree('/data/test/dpwhwtsb900')
    # print(f'\n########## THE TREE WITH DATA REMOVED #########\n')
    # print(spasy.tree.root)
    # print(f"FIND '/add/data/dpwhwtsh401' (should be True): {spasy.search('/add/data/dpwhwtsh401')}")
    # print(f"FIND '/data/test' (should be []): {spasy.search_without_geocode('/data/test')}")
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search_without_geocode('/add/data')}")
    # start = time.time()
    # print(f"\n#########FIND ALL DATA #########\n: {spasy.gather_all_data_by_namespace()}")
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO NAMESPACE DICTIONARY: {end - start}')
    # start = time.time()
    # print(f'\n######### ORGANIZE ALL DATA BY GEOCODE #########\n: {spasy.gather_all_data_by_geocode()}')
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO GEOCODE DICTIONARY: {end - start}')


    



    

